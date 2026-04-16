import pytest

from backend.ai.yolo.track_motion import TrackMotionAnalyzer


class TestTrackMotionAnalyzer:
    def test_returns_empty_motion_metrics_for_untracked_detection(self):
        analyzer = TrackMotionAnalyzer()

        assessment = analyzer.assess_detection_track(
            track_id=None,
            class_name="knife",
            bbox=[0.1, 0.1, 0.2, 0.2],
            frame_width=640,
            frame_height=480,
            timestamp_ms=1000.0,
        )

        assert assessment.velocity_x_px_s is None
        assert assessment.velocity_y_px_s is None
        assert assessment.speed_px_s is None
        assert assessment.area_growth_ratio_2s is None
        assert assessment.is_approaching is False
        assert assessment.track_age_ms == 0.0
        assert assessment.is_track_stable is False

    def test_calculates_velocity_from_consecutive_observations(self):
        analyzer = TrackMotionAnalyzer()

        analyzer.assess_detection_track(
            track_id=7,
            class_name="person",
            bbox=[0.10, 0.10, 0.30, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=0.0,
        )
        assessment = analyzer.assess_detection_track(
            track_id=7,
            class_name="person",
            bbox=[0.20, 0.10, 0.40, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=1000.0,
        )

        assert assessment.velocity_x_px_s == pytest.approx(10.0)
        assert assessment.velocity_y_px_s == pytest.approx(0.0)
        assert assessment.speed_px_s == pytest.approx(10.0)

    def test_flags_approach_when_bbox_grows_more_than_twenty_percent_in_two_seconds(self):
        analyzer = TrackMotionAnalyzer()

        analyzer.assess_detection_track(
            track_id=3,
            class_name="dog",
            bbox=[0.10, 0.10, 0.30, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=0.0,
        )
        assessment = analyzer.assess_detection_track(
            track_id=3,
            class_name="dog",
            bbox=[0.10, 0.10, 0.35, 0.35],
            frame_width=100,
            frame_height=100,
            timestamp_ms=2000.0,
        )

        assert assessment.area_growth_ratio_2s == pytest.approx(1.5625)
        assert assessment.is_approaching is True

    def test_does_not_flag_approach_before_two_seconds_of_history(self):
        analyzer = TrackMotionAnalyzer()

        analyzer.assess_detection_track(
            track_id=11,
            class_name="cat",
            bbox=[0.10, 0.10, 0.30, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=0.0,
        )
        assessment = analyzer.assess_detection_track(
            track_id=11,
            class_name="cat",
            bbox=[0.10, 0.10, 0.34, 0.34],
            frame_width=100,
            frame_height=100,
            timestamp_ms=1500.0,
        )

        assert assessment.area_growth_ratio_2s is None
        assert assessment.is_approaching is False

    def test_marks_track_as_stable_after_three_seconds(self):
        analyzer = TrackMotionAnalyzer()

        analyzer.assess_detection_track(
            track_id=21,
            class_name="bicycle",
            bbox=[0.10, 0.10, 0.30, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=0.0,
        )
        assessment = analyzer.assess_detection_track(
            track_id=21,
            class_name="bicycle",
            bbox=[0.12, 0.10, 0.32, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=3000.0,
        )

        assert assessment.track_age_ms == pytest.approx(3000.0)
        assert assessment.is_track_stable is True

    def test_resets_track_history_when_class_changes_for_same_track_id(self):
        analyzer = TrackMotionAnalyzer()

        analyzer.assess_detection_track(
            track_id=5,
            class_name="person",
            bbox=[0.10, 0.10, 0.30, 0.30],
            frame_width=100,
            frame_height=100,
            timestamp_ms=0.0,
        )
        assessment = analyzer.assess_detection_track(
            track_id=5,
            class_name="car",
            bbox=[0.20, 0.20, 0.40, 0.40],
            frame_width=100,
            frame_height=100,
            timestamp_ms=1000.0,
        )

        assert assessment.velocity_x_px_s is None
        assert assessment.area_growth_ratio_2s is None
        assert assessment.track_age_ms == pytest.approx(0.0)