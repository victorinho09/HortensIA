from dataclasses import dataclass
from enum import Enum

class ObjectSizeCategory(str,Enum):
    """
    Relative object size categories based on bounding box area.
    """
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"

@dataclass(frozen=True)
class DetectionSizeAssessment:
    """
    Intermediate size factors for one detected object
    """
    size_ratio: float
    category: ObjectSizeCategory
    factor: float

DEFAULT_SMALL_THRESHOLD = 0.03
DEFAULT_MEDIUM_THRESHOLD = 0.10

DEFAULT_SIZE_CATEGORY_FACTORS: dict[ObjectSizeCategory,float] = {
    ObjectSizeCategory.SMALL: 0.25,
    ObjectSizeCategory.MEDIUM: 0.75,
    ObjectSizeCategory.LARGE: 1,
}

def calculate_bbox_size_ratio(bbox: list[float]) -> float:
    """
    Calculate bounding box area relative to image size.
    Remember normalized bbox format: [x1,y1,x2,y2]
    """
    x1,y1,x2,y2 = bbox
    width = max(0.0,x2-x1)
    height = max(0.0,y2-y1)
    return width * height

def categorize_detection_size(
        size_ratio: float,
        small_threshold: float = DEFAULT_SMALL_THRESHOLD,
        medium_threshold: float = DEFAULT_MEDIUM_THRESHOLD,
) -> ObjectSizeCategory:
    """
    Categorize a detection size using configurable threshold
    """
    if small_threshold > medium_threshold:
        raise ValueError("small_threshold must be less than or equal to medium_threshold")

    if size_ratio < small_threshold:
        return ObjectSizeCategory.SMALL
    if size_ratio < medium_threshold:
        return ObjectSizeCategory.MEDIUM
    return ObjectSizeCategory.LARGE

def get_size_factor_for_category(
    category: ObjectSizeCategory,
    category_factors: dict[ObjectSizeCategory, float] = DEFAULT_SIZE_CATEGORY_FACTORS
) -> float:
    """
    Return the configured size factor a especific size category
    """
    try:
        return category_factors[category]
    except KeyError as exc:
        raise ValueError(f"Unsupported object size category: {category}") from exc
    
def assess_detection_size(
    bbox: list[float],
    small_threshold: float = DEFAULT_SMALL_THRESHOLD,
    medium_threshold: float = DEFAULT_MEDIUM_THRESHOLD,
    category_factors: dict[ObjectSizeCategory, float] = DEFAULT_SIZE_CATEGORY_FACTORS
) -> DetectionSizeAssessment:
    """
    Resolve intermediate size factors for a detected object
    """
    size_ratio = calculate_bbox_size_ratio(bbox)
    category = categorize_detection_size(
        size_ratio=size_ratio,
        small_threshold=small_threshold,
        medium_threshold=medium_threshold
    )
    factor = get_size_factor_for_category(
        category=category,
        category_factors=category_factors
    )
    return DetectionSizeAssessment(
        size_ratio=size_ratio,
        category=category,
        factor=factor
    )