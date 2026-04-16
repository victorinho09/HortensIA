import pytest

from backend.ai.yolo.coco_taxonomy import COCOSupercategory
from backend.ai.yolo.detection_zone import DetectionZone
from backend.ai.yolo.domestic_risk import RiskLevel, RiskSource
from backend.ai.yolo.object_size import ObjectSizeCategory
from backend.ai.yolo.scene_risk import (
    SceneRiskAnalyzer,
    calculate_approach_factor,
    calculate_motion_factor,
    calculate_object_risk,
    calculate_proximity_factor,
    calculate_scene_risk,
    get_zone_factor,
)
from backend.models.websocket import AlertSeverity, DetectedObject


def make_detected_object(**overrides) -> DetectedObject:
    payload = {
        "class_name": "knife",
        "confidence": 1.0,
        "bbox": [0.10, 0.10, 0.40, 0.60],
        "track_id": 7,
        "zone": DetectionZone.BOTTOM,
        "supercategory": COCOSupercategory.KITCHEN,
        "supercategory_risk_level": RiskLevel.MEDIUM,
        "supercategory_risk_weight": 0.50,
        "effective_risk_level": RiskLevel.HIGH,
        "effective_risk_weight": 1.0,
        "risk_source": RiskSource.CLASS_OVERRIDE,
        "size_ratio": 0.15,
        "size_category": ObjectSizeCategory.MEDIUM,
        "size_factor": 0.66,
        "velocity_x_px_s": None,
        "velocity_y_px_s": None,
        "speed_px_s": None,
        "area_growth_ratio_2s": None,
        "is_approaching": False,
        "track_age_ms": 0.0,
        "is_track_stable": False,
        "object_risk": None,
    }
    payload.update(overrides)
    return DetectedObject(**payload)


class TestGetZoneFactor:
    def test_returns_expected_factors_for_each_zone(self):
        assert get_zone_factor(DetectionZone.TOP) == 0.25
        assert get_zone_factor(DetectionZone.CENTER) == 0.60
        assert get_zone_factor(DetectionZone.BOTTOM) == 1.00


class TestCalculateApproachFactor:
    def test_returns_zero_for_missing_growth_or_unstable_track(self):
        assert calculate_approach_factor(None, True) == 0.0
        assert calculate_approach_factor(1.6, False) == 0.0

    def test_normalizes_growth_between_start_and_saturation(self):
        assert calculate_approach_factor(1.20, True) == pytest.approx(0.0)
        assert calculate_approach_factor(1.50, True) == pytest.approx(0.5)
        assert calculate_approach_factor(1.80, True) == pytest.approx(1.0)

    def test_clips_outside_range(self):
        assert calculate_approach_factor(1.05, True) == 0.0
        assert calculate_approach_factor(2.10, True) == 1.0

    def test_raises_error_when_saturation_is_not_greater_than_start(self):
        with pytest.raises(ValueError, match="Saturation ratio must be greater than start ratio"):
            calculate_approach_factor(1.5, True, start_ratio=1.2, saturation_ratio=1.2)


class TestCalculateMotionFactor:
    def test_returns_zero_for_unstable_track(self):
        detection = make_detected_object(is_track_stable=False, area_growth_ratio_2s=1.8, is_approaching=True)

        assert calculate_motion_factor(detection) == 0.0

    def test_combines_continuous_growth_and_boolean_signal(self):
        detection = make_detected_object(
            is_track_stable=True,
            area_growth_ratio_2s=1.50,
            is_approaching=True,
        )

        assert calculate_motion_factor(detection) == pytest.approx(0.6)


class TestCalculateProximityFactor:
    def test_combines_size_and_zone(self):
        detection = make_detected_object(
            zone=DetectionZone.CENTER,
            size_factor=0.66,
        )

        assert calculate_proximity_factor(detection) == pytest.approx(0.636)


class TestCalculateObjectRisk:
    def test_combines_semantic_proximity_motion_and_confidence(self):
        detection = make_detected_object(
            confidence=0.9,
            zone=DetectionZone.BOTTOM,
            size_factor=1.0,
            effective_risk_weight=1.0,
            is_track_stable=True,
            area_growth_ratio_2s=1.50,
            is_approaching=True,
        )

        assert calculate_object_risk(detection) == pytest.approx(0.9)

    def test_confidence_scales_down_the_weighted_risk(self):
        detection = make_detected_object(
            confidence=0.5,
            zone=DetectionZone.BOTTOM,
            size_factor=1.0,
            effective_risk_weight=1.0,
            is_track_stable=False,
        )

        assert calculate_object_risk(detection) == pytest.approx(0.5)


class TestCalculateSceneRisk:
    def test_returns_zero_with_no_objects(self):
        assert calculate_scene_risk([]) == 0.0

    def test_combines_multiple_object_risks_using_noisy_or(self):
        assert calculate_scene_risk([0.6, 0.5]) == pytest.approx(0.8)


class TestSceneRiskAnalyzer:
    def test_assess_detections_adds_object_risks_and_resolves_dominant_object(self):
        analyzer = SceneRiskAnalyzer(smoothing_alpha=1.0)
        low_risk_detection = make_detected_object(
            class_name="cup",
            track_id=1,
            zone=DetectionZone.TOP,
            supercategory=COCOSupercategory.KITCHEN,
            effective_risk_level=RiskLevel.LOW,
            effective_risk_weight=0.10,
            risk_source=RiskSource.CLASS_OVERRIDE,
            size_category=ObjectSizeCategory.SMALL,
            size_factor=0.33,
            size_ratio=0.03,
        )
        high_risk_detection = make_detected_object(
            class_name="knife",
            track_id=2,
            zone=DetectionZone.BOTTOM,
            size_category=ObjectSizeCategory.LARGE,
            size_factor=1.0,
            size_ratio=0.30,
            effective_risk_level=RiskLevel.HIGH,
            effective_risk_weight=1.0,
            is_track_stable=True,
            area_growth_ratio_2s=1.50,
            is_approaching=True,
        )

        score = analyzer.assess_detections([low_risk_detection, high_risk_detection])

        assert score.detections[0].object_risk is not None
        assert score.detections[1].object_risk is not None
        assert score.dominant_object_index == 1
        assert score.dominant_track_id == 2
        assert score.dominant_class_name == "knife"
        assert score.instant_risk == pytest.approx(
            calculate_scene_risk([
                score.detections[0].object_risk,
                score.detections[1].object_risk,
            ])
        )

    def test_smooths_risk_across_consecutive_frames(self):
        analyzer = SceneRiskAnalyzer(smoothing_alpha=0.5)
        high_risk_detection = make_detected_object(
            zone=DetectionZone.BOTTOM,
            size_factor=1.0,
            effective_risk_weight=1.0,
            is_track_stable=True,
            area_growth_ratio_2s=1.50,
            is_approaching=True,
        )

        first_score = analyzer.assess_detections([high_risk_detection])
        second_score = analyzer.assess_detections([high_risk_detection])

        assert first_score.instant_risk == pytest.approx(1.0)
        assert first_score.smoothed_risk == pytest.approx(0.5)
        assert second_score.instant_risk == pytest.approx(1.0)
        assert second_score.smoothed_risk == pytest.approx(0.75)

    def test_resolves_severity_from_smoothed_risk(self):
        analyzer = SceneRiskAnalyzer(smoothing_alpha=1.0)
        warning_detection = make_detected_object(
            confidence=1.0,
            zone=DetectionZone.BOTTOM,
            size_factor=1.0,
            effective_risk_weight=0.50,
            is_track_stable=False,
        )
        critical_detection = make_detected_object(
            confidence=1.0,
            zone=DetectionZone.BOTTOM,
            size_factor=1.0,
            effective_risk_weight=1.0,
            is_track_stable=True,
            area_growth_ratio_2s=1.80,
            is_approaching=True,
        )

        warning_score = analyzer.assess_detections([warning_detection])
        critical_score = analyzer.assess_detections([critical_detection])
        info_score = analyzer.assess_detections([])

        assert warning_score.severity == AlertSeverity.WARNING
        assert critical_score.severity == AlertSeverity.CRITICAL
        assert info_score.severity == AlertSeverity.INFO