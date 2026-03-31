import pytest

from backend.ai.yolo.coco_taxonomy import COCOSupercategory
from backend.ai.yolo.domestic_risk import (
    RiskLevel,
    RiskSource,
    get_supercategory_risk_profile,
    get_class_risk_override,
    assess_detection_risk,
)


class TestRiskLevel:
    def test_all_values(self):
        assert RiskLevel.LOW == "low"
        assert RiskLevel.MEDIUM == "medium"
        assert RiskLevel.HIGH == "high"


class TestRiskSource:
    def test_all_values(self):
        assert RiskSource.SUPERCATEGORY_BASE == "supercategory_base"
        assert RiskSource.CLASS_OVERRIDE == "class_override"


class TestGetSupercategoryRiskProfile:
    def test_kitchen_base_risk_is_medium(self):
        profile = get_supercategory_risk_profile(COCOSupercategory.KITCHEN)
        assert profile.level == RiskLevel.MEDIUM
        assert profile.weight == 0.60

    def test_appliance_base_risk_is_medium(self):
        profile = get_supercategory_risk_profile(COCOSupercategory.APPLIANCE)
        assert profile.level == RiskLevel.MEDIUM
        assert profile.weight == 0.60

    def test_vehicle_base_risk_is_low(self):
        profile = get_supercategory_risk_profile(COCOSupercategory.VEHICLE)
        assert profile.level == RiskLevel.LOW
        assert profile.weight == 0.25


class TestGetClassRiskOverride:
    def test_knife_override_is_high(self):
        profile = get_class_risk_override("knife")
        assert profile is not None
        assert profile.level == RiskLevel.HIGH
        assert profile.weight == 1.00

    def test_bowl_override_is_low(self):
        profile = get_class_risk_override("bowl")
        assert profile is not None
        assert profile.level == RiskLevel.LOW
        assert profile.weight == 0.25

    def test_unknown_class_has_no_override(self):
        assert get_class_risk_override("banana") is None


class TestAssessDetectionRisk:
    def test_class_override_replaces_supercategory_base(self):
        assessment = assess_detection_risk("knife", COCOSupercategory.KITCHEN)

        assert assessment.supercategory_level == RiskLevel.MEDIUM
        assert assessment.supercategory_weight == 0.60
        assert assessment.effective_level == RiskLevel.HIGH
        assert assessment.effective_weight == 1.00
        assert assessment.source == RiskSource.CLASS_OVERRIDE

    def test_base_risk_is_used_when_no_override_exists(self):
        assessment = assess_detection_risk("banana", COCOSupercategory.FOOD)

        assert assessment.supercategory_level == RiskLevel.LOW
        assert assessment.supercategory_weight == 0.25
        assert assessment.effective_level == RiskLevel.LOW
        assert assessment.effective_weight == 0.25
        assert assessment.source == RiskSource.SUPERCATEGORY_BASE

    def test_low_override_can_reduce_a_medium_base(self):
        assessment = assess_detection_risk("bowl", COCOSupercategory.KITCHEN)

        assert assessment.supercategory_level == RiskLevel.MEDIUM
        assert assessment.supercategory_weight == 0.60
        assert assessment.effective_level == RiskLevel.LOW
        assert assessment.effective_weight == 0.25
        assert assessment.source == RiskSource.CLASS_OVERRIDE