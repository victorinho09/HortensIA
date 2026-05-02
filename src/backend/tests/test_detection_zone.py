import pytest

from backend.ai.yolo.detection_zone import DetectionZone, calculate_detection_zone


class TestDetectionZone:
    def test_all_values(self):
        assert DetectionZone.TOP == "top"
        assert DetectionZone.CENTER == "center"
        assert DetectionZone.BOTTOM == "bottom"


class TestCalculateDetectionZone:
    def test_returns_top_for_bbox_in_top_zone(self):
        assert calculate_detection_zone([0.1, 0.05, 0.4, 0.2]) == DetectionZone.TOP

    def test_returns_center_for_bbox_in_center_zone(self):
        assert calculate_detection_zone([0.1, 0.2, 0.4, 0.5]) == DetectionZone.CENTER

    def test_returns_bottom_for_bbox_in_bottom_zone(self):
        assert calculate_detection_zone([0.1, 0.4, 0.4, 0.9]) == DetectionZone.BOTTOM

    def test_boundary_at_one_third_belongs_to_center(self):
        assert calculate_detection_zone([0.1, 0.0, 0.4, 1 / 3]) == DetectionZone.CENTER

    def test_boundary_at_two_thirds_belongs_to_bottom(self):
        assert calculate_detection_zone([0.1, 0.0, 0.4, 2 / 3]) == DetectionZone.BOTTOM

    def test_crossing_boundary_uses_bottom_edge(self):
        assert calculate_detection_zone([0.1, 0.2, 0.4, 0.34]) == DetectionZone.CENTER

    @pytest.mark.parametrize(
        ("bbox", "expected_zone"),
        [
            ([0.0, 0.0, 1.0, 0.0], DetectionZone.TOP),
            ([0.0, 0.0, 1.0, 0.60], DetectionZone.CENTER),
            ([0.0, 0.0, 1.0, 1.0], DetectionZone.BOTTOM),
        ],
    )
    def test_uses_only_bottom_edge_position(self, bbox, expected_zone):
        assert calculate_detection_zone(bbox) == expected_zone