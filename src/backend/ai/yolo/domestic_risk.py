from dataclasses import dataclass

from enum import Enum
from backend.ai.yolo.coco_taxonomy import COCOSupercategory

class RiskLevel(str,Enum):
    """
    Domestic risk severity levels
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RiskSource(str,Enum):
    """
    Indicates where the effective risk value comes from
    """
    SUPERCATEGORY_BASE = "supercategory_base"
    CLASS_OVERRIDE = "class_override"

@dataclass(frozen=True)
class RiskProfile:
    """
    Risk profile used by intermediate risk calculations.
    """
    level: RiskLevel
    weight: float

@dataclass(frozen=True)
class DetectionRiskAssessment:
    """
    Intermediate domestic risk factors for one detected object
    """
    supercategory_level: RiskLevel
    supercategory_weight: float
    effective_level: RiskLevel
    effective_weight: float
    source: RiskSource

LOW_RISK= RiskProfile(level=RiskLevel.LOW,weight=0.25)
MEDIUM_RISK=RiskProfile(level=RiskLevel.MEDIUM,weight=0.60)
HIGH_RISK=RiskProfile(level=RiskLevel.HIGH,weight=1.00)

DOMESTIC_SUPERCATEGORY_RISK_MAP: dict[COCOSupercategory, RiskProfile] = {
    COCOSupercategory.PERSON: LOW_RISK,
    COCOSupercategory.VEHICLE: LOW_RISK,
    COCOSupercategory.OUTDOOR: LOW_RISK,
    COCOSupercategory.ANIMAL: MEDIUM_RISK,
    COCOSupercategory.ACCESSORY: LOW_RISK,
    COCOSupercategory.SPORTS: LOW_RISK,
    COCOSupercategory.KITCHEN: MEDIUM_RISK,
    COCOSupercategory.FOOD: LOW_RISK,
    COCOSupercategory.FURNITURE: LOW_RISK,
    COCOSupercategory.ELECTRONIC: LOW_RISK,
    COCOSupercategory.APPLIANCE: MEDIUM_RISK,
    COCOSupercategory.INDOOR: LOW_RISK,
}

DOMESTIC_CLASS_RISK_OVERRIDES: dict[str, RiskProfile] = {
    "knife": HIGH_RISK,
    "scissors": HIGH_RISK,
    "oven": HIGH_RISK,
    "toaster": HIGH_RISK,
    "microwave": MEDIUM_RISK,
    "fork": MEDIUM_RISK,
    "wine glass": MEDIUM_RISK,
    "bottle": MEDIUM_RISK,
    "hair drier": MEDIUM_RISK,
    "vase": MEDIUM_RISK,
    "sink": LOW_RISK,
    "refrigerator": LOW_RISK,
    "bowl": LOW_RISK,
    "cup": LOW_RISK,
    "spoon": LOW_RISK,
}

def get_supercategory_risk_profile(supercategory: COCOSupercategory) -> RiskProfile:
    """
    Return the domestic base risk profile for a COCO supercategory
    """
    try:
        return DOMESTIC_SUPERCATEGORY_RISK_MAP[supercategory]
    except KeyError as exc:
        raise ValueError(f"Unsupported COCO supercategory: {supercategory}") from exc
    

def get_class_risk_override(class_name: str) -> RiskProfile | None:
    """
    Return a class-specific domestic risk override if one exists
    """
    return DOMESTIC_CLASS_RISK_OVERRIDES.get(class_name)

def assess_detection_risk(class_name: str, supercategory: COCOSupercategory) -> DetectionRiskAssessment:
    """
    Resolve intermediate domestic risk factors for a detected object.
    Class-specific risk overrides replace the supercategory base risk.
    """

    supercategory_profile = get_supercategory_risk_profile(supercategory)
    class_profile = get_class_risk_override(class_name)

    if class_profile is not None:
        return DetectionRiskAssessment(
            supercategory_level=supercategory_profile.level,
            supercategory_weight=supercategory_profile.weight,
            effective_level=class_profile.level,
            effective_weight=class_profile.weight,
            source=RiskSource.CLASS_OVERRIDE
        )
    return DetectionRiskAssessment(
        supercategory_level=supercategory_profile.level,
        supercategory_weight=supercategory_profile.weight,
        effective_level=supercategory_profile.level,
        effective_weight=supercategory_profile.weight,
        source=RiskSource.SUPERCATEGORY_BASE,
    )