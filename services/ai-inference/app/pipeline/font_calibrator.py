import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("FontCalibrator")


class MetricSpatialCalibrator:
    def __init__(self, nominal_barcode_width_mm: float = 37.29):
        # GS1 EAN-13 nominal standard width is 37.29 mm
        self.nominal_barcode_width_mm = nominal_barcode_width_mm

    def calculate_scale_ratio(self, barcode_region: Optional[Dict[str, Any]]) -> float:
        """
        Computes spatial resolution ratio (mm per pixel).
        Ratio = Nominal_Barcode_Width_mm / Barcode_Width_Pixels
        """
        if not barcode_region or "bbox" not in barcode_region:
            logger.info("Barcode region not detected. Utilizing default 300 DPI packaging scale (0.0846 mm/px).")
            return 0.0846  # 25.4 / 300 dpi standard

        bbox = barcode_region["bbox"]  # [x, y, w, h]
        pixel_width = float(bbox[2])

        if pixel_width < 10:
            logger.warning(f"Barcode width pixel count too small ({pixel_width} px). Using default scale.")
            return 0.0846

        scale_ratio = self.nominal_barcode_width_mm / pixel_width
        logger.info(f"Calibrated scale: {scale_ratio:.4f} mm/px based on barcode width {pixel_width}px")
        return scale_ratio

    def measure_font_height_mm(self, height_px: float, scale_ratio_mm_per_px: float) -> float:
        """Converts glyph/text bounding box pixel height to physical millimeters."""
        measured_mm = height_px * scale_ratio_mm_per_px
        return round(measured_mm, 2)

    def calculate_pdp_area_cm2(self, pdp_region: Optional[Dict[str, Any]], scale_ratio_mm_per_px: float) -> float:
        """
        Calculates physical surface area of the Principal Display Panel (PDP) in cm^2.
        Area_cm2 = (Width_mm * Height_mm) / 100
        """
        if not pdp_region or "bbox" not in pdp_region:
            return 120.0  # Safe default within 50 < A <= 200 bracket

        bbox = pdp_region["bbox"]  # [x, y, w, h]
        w_px, h_px = float(bbox[2]), float(bbox[3])

        width_mm = w_px * scale_ratio_mm_per_px
        height_mm = h_px * scale_ratio_mm_per_px

        area_cm2 = (width_mm * height_mm) / 100.0
        return round(area_cm2, 2)
