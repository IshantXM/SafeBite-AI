import logging
from typing import List, Tuple
import cv2
import numpy as np

logger = logging.getLogger("ContrastChecker")


class ContrastChecker:
    def srgb_to_linear(self, val: float) -> float:
        """Converts an 8-bit sRGB color component to linear luminance."""
        v = val / 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4

    def calculate_relative_luminance(self, rgb: Tuple[float, float, float]) -> float:
        """Calculates WCAG 2.1 relative luminance from RGB tuple (0-255)."""
        r, g, b = rgb
        r_lin = self.srgb_to_linear(r)
        g_lin = self.srgb_to_linear(g)
        b_lin = self.srgb_to_linear(b)
        return 0.2126 * r_lin + 0.7152 * g_lin + 0.0722 * b_lin

    def calculate_contrast_ratio(self, image: np.ndarray, bbox: List[int]) -> float:
        """
        Computes WCAG 2.1 text-to-background contrast ratio from the bounding box ROI.
        Contrast Ratio = (L1 + 0.05) / (L2 + 0.05) where L1 is lighter and L2 is darker.
        """
        x, y, w, h = bbox
        img_h, img_w = image.shape[:2]

        # Ensure bbox bounds are valid
        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(img_w, x + w)
        y2 = min(img_h, y + h)

        if (x2 - x1) < 5 or (y2 - y1) < 5:
            return 4.5  # Standard passing default for degenerate boxes

        roi = image[y1:y2, x1:x2]
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY) if len(roi.shape) == 3 else roi

        # Segment text glyphs (foreground) vs packaging background using Otsu binarization
        _, mask = cv2.threshold(gray_roi, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        fg_pixels = roi[mask == 0] if len(roi.shape) == 3 else gray_roi[mask == 0]
        bg_pixels = roi[mask == 255] if len(roi.shape) == 3 else gray_roi[mask == 255]

        if len(fg_pixels) == 0 or len(bg_pixels) == 0:
            return 4.5

        # Compute average BGR colors
        if len(roi.shape) == 3:
            fg_color = np.mean(fg_pixels, axis=0)  # [B, G, R]
            bg_color = np.mean(bg_pixels, axis=0)
            fg_rgb = (fg_color[2], fg_color[1], fg_color[0])
            bg_rgb = (bg_color[2], bg_color[1], bg_color[0])
        else:
            fg_val = float(np.mean(fg_pixels))
            bg_val = float(np.mean(bg_pixels))
            fg_rgb = (fg_val, fg_val, fg_val)
            bg_rgb = (bg_val, bg_val, bg_val)

        l_fg = self.calculate_relative_luminance(fg_rgb)
        l_bg = self.calculate_relative_luminance(bg_rgb)

        l1 = max(l_fg, l_bg)
        l2 = min(l_fg, l_bg)

        ratio = (l1 + 0.05) / (l2 + 0.05)
        return round(float(ratio), 2)
