import pytest

from backend.ai.yolo.object_size import (
    DEFAULT_MEDIUM_THRESHOLD,
    DEFAULT_SMALL_THRESHOLD,
    DEFAULT_SIZE_CATEGORY_FACTORS,
    DetectionSizeAssessment,
    ObjectSizeCategory,
    assess_detection_size,
    calculate_bbox_size_ratio,
    categorize_detection_size,
    get_size_factor_for_category,
)


class TestObjectSizeCategory:
    def test_all_values(self):
        assert ObjectSizeCategory.SMALL == "small"
        assert ObjectSizeCategory.MEDIUM == "medium"
        assert ObjectSizeCategory.LARGE == "large"


class TestDetectionSizeAssessment:
    def test_stores_resolved_size_fields(self):
        assessment = DetectionSizeAssessment(
            size_ratio=0.12,
            category=ObjectSizeCategory.MEDIUM,
            factor=0.66,
        )

        assert assessment.size_ratio == 0.12
        assert assessment.category == ObjectSizeCategory.MEDIUM
        assert assessment.factor == 0.66


class TestCalculateBboxSizeRatio:
    def test_returns_bbox_area_for_normalized_bbox(self):
        assert calculate_bbox_size_ratio([0.1, 0.2, 0.5, 0.8]) == pytest.approx(0.24)

    def test_returns_zero_when_width_is_negative(self):
        assert calculate_bbox_size_ratio([0.5, 0.1, 0.2, 0.4]) == 0.0

    def test_returns_zero_when_height_is_negative(self):
        assert calculate_bbox_size_ratio([0.1, 0.8, 0.5, 0.2]) == 0.0


class TestCategorizeDetectionSize:
    def test_uses_expected_default_thresholds(self):
        assert DEFAULT_SMALL_THRESHOLD == 0.05
        assert DEFAULT_MEDIUM_THRESHOLD == 0.20

    def test_returns_small_below_small_threshold(self):
        assert categorize_detection_size(0.03) == ObjectSizeCategory.SMALL

    def test_boundary_at_small_threshold_belongs_to_medium(self):
        assert categorize_detection_size(0.05) == ObjectSizeCategory.MEDIUM

    def test_returns_medium_below_medium_threshold(self):
        assert categorize_detection_size(0.12) == ObjectSizeCategory.MEDIUM

    def test_boundary_at_medium_threshold_belongs_to_large(self):
        assert categorize_detection_size(0.20) == ObjectSizeCategory.LARGE

    def test_returns_large_above_medium_threshold(self):
        assert categorize_detection_size(0.35) == ObjectSizeCategory.LARGE

    def test_invalid_threshold_order_raises_error(self):
        with pytest.raises(ValueError, match="small_threshold must be less than or equal to medium_threshold"):
            categorize_detection_size(0.10, small_threshold=0.30, medium_threshold=0.20)


class TestGetSizeFactorForCategory:
    def test_returns_default_factor_for_each_category(self):
        assert get_size_factor_for_category(ObjectSizeCategory.SMALL) == DEFAULT_SIZE_CATEGORY_FACTORS[ObjectSizeCategory.SMALL]
        assert get_size_factor_for_category(ObjectSizeCategory.MEDIUM) == DEFAULT_SIZE_CATEGORY_FACTORS[ObjectSizeCategory.MEDIUM]
        assert get_size_factor_for_category(ObjectSizeCategory.LARGE) == DEFAULT_SIZE_CATEGORY_FACTORS[ObjectSizeCategory.LARGE]

    def test_returns_factor_from_custom_mapping(self):
        custom_factors = {
            ObjectSizeCategory.SMALL: 0.2,
            ObjectSizeCategory.MEDIUM: 0.5,
            ObjectSizeCategory.LARGE: 0.9,
        }

        assert get_size_factor_for_category(ObjectSizeCategory.MEDIUM, custom_factors) == 0.5


class TestAssessDetectionSize:
    def test_resolves_small_detection(self):
        assessment = assess_detection_size([0.0, 0.0, 0.2, 0.2])

        assert assessment.size_ratio == pytest.approx(0.04)
        assert assessment.category == ObjectSizeCategory.SMALL
        assert assessment.factor == 0.33

    def test_resolves_medium_detection(self):
        assessment = assess_detection_size([0.0, 0.0, 0.3, 0.4])

        assert assessment.size_ratio == pytest.approx(0.12)
        assert assessment.category == ObjectSizeCategory.MEDIUM
        assert assessment.factor == 0.66

    def test_resolves_large_detection(self):
        assessment = assess_detection_size([0.0, 0.0, 0.5, 0.6])

        assert assessment.size_ratio == pytest.approx(0.30)
        assert assessment.category == ObjectSizeCategory.LARGE
        assert assessment.factor == 1.0

    def test_supports_custom_thresholds_and_factors(self):
        custom_factors = {
            ObjectSizeCategory.SMALL: 0.1,
            ObjectSizeCategory.MEDIUM: 0.4,
            ObjectSizeCategory.LARGE: 0.8,
        }

        assessment = assess_detection_size(
            [0.0, 0.0, 0.25, 0.40],
            small_threshold=0.04,
            medium_threshold=0.12,
            category_factors=custom_factors,
        )

        assert assessment.size_ratio == pytest.approx(0.10)
        assert assessment.category == ObjectSizeCategory.MEDIUM
        assert assessment.factor == 0.4