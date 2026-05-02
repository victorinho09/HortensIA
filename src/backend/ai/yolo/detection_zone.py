from enum import Enum

class DetectionZone(str,Enum):
    """
    Vertical risk zones for a detection inside the image.
    """
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"

def calculate_detection_zone(bbox: list[float]) -> DetectionZone:
    """
    Classify a detection into a vertical zone using the bottom edge of the
    bounding box.

    Bounding box format: [x1, y1, x2, y2], normalized between 0 and 1.
    """
    y2 = bbox[3]

    if y2 < (1 / 3):
        return DetectionZone.TOP
    if y2 < (2 / 3):
        return DetectionZone.CENTER
    return DetectionZone.BOTTOM