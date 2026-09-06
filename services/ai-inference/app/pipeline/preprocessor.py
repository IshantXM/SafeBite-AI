import logging
from typing import Tuple
import cv2
import numpy as np

logger = logging.getLogger("Preprocessor")


class ImagePreprocessor:
    def __init__(self, clip_limit: float = 2.5, tile_grid_size: Tuple[int, int] = (8, 8)):
        self.clip_limit = clip_limit
        self.tile_grid_size = tile_grid_size
        self.clahe = cv2.createCLAHE(clipLimit=self.clip_limit, tileGridSize=self.tile_grid_size)

    def apply_clahe(self, image: np.ndarray) -> np.ndarray:
        """
        Applies Contrast Limited Adaptive Histogram Equalization to the L-channel
        in LAB color space to mitigate glare, glossy reflections, and uneven ambient lighting.
        """
        if len(image.shape) == 2:
            return self.clahe.apply(image)

        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        cl = self.clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    def deskew_image(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Detects primary orientation angle using probabilistic Hough line transforms
        and deskews the image so text polygons and barcodes align horizontally.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image.copy()
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

        angle = 0.0
        if lines is not None and len(lines) > 0:
            angles = []
            for line in lines:
                x1, y1, x2, y2 = line[0]
                rad = np.arctan2(y2 - y1, x2 - x1)
                deg = np.degrees(rad)
                # Keep lines close to horizontal (-45 to 45 deg)
                if -45 < deg < 45:
                    angles.append(deg)
            if angles:
                angle = float(np.median(angles))

        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            deskewed = cv2.warpAffine(
                image, M, (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            logger.info(f"Deskewed image by {angle:.2f} degrees")
            return deskewed, angle

        return image, 0.0

    def adaptive_binarization(self, image: np.ndarray) -> np.ndarray:
        """
        Computes local adaptive Gaussian thresholding for high-contrast segmentation
        of text glyphs against noisy packaging graphics.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binarized = cv2.adaptiveThreshold(
            blurred, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return binarized

    def check_blur(self, image: np.ndarray) -> Tuple[bool, float]:
        """
        Calculates Laplacian variance to check image sharpness.
        Variance < 100 indicates excessive blur.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        variance = cv2.Laplacian(gray, cv2.CV_64F).var()
        is_sharp = variance >= 100.0
        return is_sharp, float(variance)

    def validate_food_package(self, image: np.ndarray, text_token_count: int = 0) -> Tuple[bool, str]:
        """
        Detects if the image is a valid food package label panel vs a blank wall,
        plain bottle, or featureless background.
        Calculates edge density, color variance, and structural contours.
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
        
        # 1. Edge density test (blank walls have near 0 edges)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / (gray.shape[0] * gray.shape[1])

        # 2. Intensity standard deviation (plain surfaces have low variance)
        std_dev = np.std(gray)

        # 3. Contour complexity
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        num_contours = len(contours)

        logger.info(f"Package Detection - Edges: {edge_density:.4f}, StdDev: {std_dev:.2f}, Contours: {num_contours}, Tokens: {text_token_count}")

        # Thresholds for non-food / blank wall rejection
        if edge_density < 0.015 and std_dev < 25.0 and num_contours < 15 and text_token_count < 3:
            return False, "Invalid Scan: Blank wall or plain surface detected. Point camera at a food packaging label."

        return True, "Valid packaging panel detected."

    def process(self, image: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        """
        Executes full preprocessing pipeline:
        Returns (enhanced_color_image, binarized_image, deskew_angle).
        """
        clahe_enhanced = self.apply_clahe(image)
        deskewed, angle = self.deskew_image(clahe_enhanced)
        binarized = self.adaptive_binarization(deskewed)
        return deskewed, binarized, angle

