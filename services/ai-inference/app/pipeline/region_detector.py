import logging
import os
from typing import Any, Dict, List, Optional
import cv2
import numpy as np

logger = logging.getLogger("RegionDetector")

try:
    from ultralytics import YOLO
except ImportError:
    YOLO = None


class RegionDetector:
    def __init__(self, model_path: Optional[str] = None):
        self.model = None
        if YOLO and model_path and os.path.exists(model_path):
            try:
                self.model = YOLO(model_path)
                logger.info(f"Loaded YOLOv8 model from {model_path}")
            except Exception as e:
                logger.warning(f"Could not load YOLO model at {model_path}: {e}. Utilizing computer-vision fallbacks.")

    def detect_regions(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Detects:
        - pdp: Principal Display Panel bbox [x, y, w, h] and estimated area
        - barcode: Barcode bounding box [x, y, w, h] and orientation
        - tamper_stickers: Suspect price sticker overlays
        """
        h, w = image.shape[:2]
        regions = {
            "pdp": None,
            "barcode": None,
            "tamper_stickers": [],
            "source": "heuristic"
        }

        # 1. YOLOv8 inference if model loaded
        if self.model:
            try:
                results = self.model.predict(image, conf=0.35, verbose=False)
                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        cls_name = r.names.get(cls_id, "")
                        coords = box.xywh[0].cpu().numpy().tolist()  # [xc, yc, w, h]
                        conf = float(box.conf[0])

                        # Convert xc, yc, w, h to x1, y1, w, h
                        x1 = int(coords[0] - coords[2] / 2)
                        y1 = int(coords[1] - coords[3] / 2)
                        bw = int(coords[2])
                        bh = int(coords[3])

                        if "pdp" in cls_name.lower() or "display" in cls_name.lower():
                            regions["pdp"] = {"bbox": [x1, y1, bw, bh], "confidence": conf}
                        elif "barcode" in cls_name.lower():
                            regions["barcode"] = {"bbox": [x1, y1, bw, bh], "confidence": conf}
                        elif "sticker" in cls_name.lower() or "tamper" in cls_name.lower():
                            regions["tamper_stickers"].append({
                                "bbox": [x1, y1, bw, bh],
                                "confidence": conf,
                                "suspect_type": "OVERLAPPING_PRICE_STICKER"
                            })
                regions["source"] = "yolov8"
            except Exception as e:
                logger.warning(f"YOLO detection error: {e}. Falling back to visual heuristics.")

        # 2. Heuristic fallback for Barcode if not detected
        if not regions["barcode"]:
            barcode_box = self._find_barcode_heuristic(image)
            if barcode_box:
                regions["barcode"] = {"bbox": barcode_box, "confidence": 0.75}

        # 3. Default PDP to primary package boundary if not detected
        if not regions["pdp"]:
            # Standard PDP default: outer 80% boundary of front panel
            regions["pdp"] = {
                "bbox": [int(w * 0.05), int(h * 0.05), int(w * 0.9), int(h * 0.9)],
                "confidence": 0.80
            }

        # 4. Detect physical sticker overlays via contour edges and chromatic difference
        if not regions["tamper_stickers"]:
            stickers = self._detect_tamper_stickers_heuristic(image)
            regions["tamper_stickers"].extend(stickers)

        return regions

    def _find_barcode_heuristic(self, image: np.ndarray) -> Optional[List[int]]:
        """
        Locates barcode region via vertical gradient morphology:
        Barcodes feature dense high-frequency vertical edges.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        # Horizontal and vertical Scharr gradients
        grad_x = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=1, dy=0, ksize=-1)
        grad_y = cv2.Sobel(gray, ddepth=cv2.CV_32F, dx=0, dy=1, ksize=-1)
        gradient = cv2.subtract(grad_x, grad_y)
        gradient = cv2.convertScaleAbs(gradient)

        # Blur and threshold
        blurred = cv2.blur(gradient, (9, 9))
        _, thresh = cv2.threshold(blurred, 225, 255, cv2.THRESH_BINARY)

        # Morphological closing with rectangular kernel
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 7))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        closed = cv2.erode(closed, None, iterations=4)
        closed = cv2.dilate(closed, None, iterations=4)

        contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            # Sort by area descending
            c = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(c)
            aspect_ratio = float(w) / h if h > 0 else 0
            if 1.2 <= aspect_ratio <= 3.5 and w > 80:
                return [x, y, w, h]

        return None

    def _detect_tamper_stickers_heuristic(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detects rectangular adhesive sticker overlays that conceal printed prices or dates.
        Characterized by sharp unnatural rectangular boundaries and distinct local white/yellow substrate.
        """
        h, w = image.shape[:2]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(edges, kernel, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        stickers = []
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.04 * peri, True)
            # Quadrilateral with typical price tag proportions
            if len(approx) == 4:
                x, y, sw, sh = cv2.boundingRect(approx)
                area = sw * sh
                # Sticker must be a fraction of the total package (between 1% and 15%)
                if (0.01 * w * h) < area < (0.15 * w * h):
                    aspect = float(sw) / sh if sh > 0 else 0
                    if 1.0 <= aspect <= 4.0:
                        # Check if region has high average brightness (typical white paper sticker)
                        roi = gray[y:y+sh, x:x+sw]
                        mean_brightness = float(np.mean(roi))
                        if mean_brightness > 190:
                            stickers.append({
                                "bbox": [x, y, sw, sh],
                                "confidence": 0.82,
                                "suspect_type": "OVERLAPPING_PRICE_STICKER",
                                "description": "Suspect price sticker overlay concealing printed declarations"
                            })

        return stickers[:2]  # return top detected stickers
