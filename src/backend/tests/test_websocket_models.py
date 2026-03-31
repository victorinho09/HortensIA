"""
WebSocket Message Model Tests

Unit tests for WebSocket message models used in the live camera session protocol.
"""

import pytest
from pydantic import ValidationError
from backend.models.websocket import (
    ClientMessageType,
    FrameMessage,
    ServerMessageTypes,
    AlertSeverity,
    DetectionZone,
    calculate_detection_zone,
    DetectedObject,
    AlertMessage,
    DetectionMessage,
    StatusMessage,
    ErrorMessage,
)
from backend.ai.yolo.coco_taxonomy import (
    COCOSupercategory,
    calculate_detection_supercategory,
)


class TestClientMessageType:
    """Test suite for ClientMessageType enum"""

    def test_frame_value(self):
        """Test FRAME enum value is correct"""
        assert ClientMessageType.FRAME == "frame"

    def test_is_string_enum(self):
        """Test ClientMessageType members are strings"""
        assert isinstance(ClientMessageType.FRAME, str)


class TestFrameMessage:
    """Test suite for FrameMessage model"""

    def test_valid_frame_message(self, sample_frame_message_data):
        """Test FrameMessage creation with valid data"""
        msg = FrameMessage(**sample_frame_message_data)
        assert msg.type == "frame"
        assert msg.data == sample_frame_message_data["data"]
        assert msg.timestamp == sample_frame_message_data["timestamp"]

    def test_type_field_is_always_frame(self):
        """Test that type field is always 'frame' regardless of input"""
        msg = FrameMessage(data="abc", timestamp=1000.0)
        assert msg.type == "frame"

    def test_missing_data_raises_error(self):
        """Test ValidationError is raised when data field is missing"""
        with pytest.raises(ValidationError):
            FrameMessage(timestamp=1000.0)

    def test_missing_timestamp_raises_error(self):
        """Test ValidationError is raised when timestamp field is missing"""
        with pytest.raises(ValidationError):
            FrameMessage(data="abc")

    def test_serializes_to_json_with_type(self, sample_frame_message_data):
        """Test model_dump_json includes type field"""
        msg = FrameMessage(**sample_frame_message_data)
        json_str = msg.model_dump_json()
        assert '"type":"frame"' in json_str or '"type": "frame"' in json_str


class TestServerMessageTypes:
    """Test suite for ServerMessageTypes enum"""

    def test_all_values(self):
        """Test all expected enum values exist"""
        assert ServerMessageTypes.ALERT == "alert"
        assert ServerMessageTypes.DETECTION == "detection"
        assert ServerMessageTypes.STATUS == "status"
        assert ServerMessageTypes.ERROR == "error"

    def test_is_string_enum(self):
        """Test ServerMessageTypes members are strings"""
        for member in ServerMessageTypes:
            assert isinstance(member, str)


class TestAlertSeverity:
    """Test suite for AlertSeverity enum"""

    def test_all_values(self):
        """Test all expected severity values exist"""
        assert AlertSeverity.INFO == "info"
        assert AlertSeverity.WARNING == "warning"
        assert AlertSeverity.CRITICAL == "critical"


class TestDetectionZone:
    """Test suite for DetectionZone enum"""

    def test_all_values(self):
        """Test all expected zone values exist"""
        assert DetectionZone.TOP == "top"
        assert DetectionZone.CENTER == "center"
        assert DetectionZone.BOTTOM == "bottom"


class TestCOCOSupercategory:
    """Test suite for COCOSupercategory enum"""

    def test_all_expected_values_exist(self):
        assert COCOSupercategory.PERSON == "person"
        assert COCOSupercategory.VEHICLE == "vehicle"
        assert COCOSupercategory.OUTDOOR == "outdoor"
        assert COCOSupercategory.ANIMAL == "animal"
        assert COCOSupercategory.ACCESSORY == "accessory"
        assert COCOSupercategory.SPORTS == "sports"
        assert COCOSupercategory.KITCHEN == "kitchen"
        assert COCOSupercategory.FOOD == "food"
        assert COCOSupercategory.FURNITURE == "furniture"
        assert COCOSupercategory.ELECTRONIC == "electronic"
        assert COCOSupercategory.APPLIANCE == "appliance"
        assert COCOSupercategory.INDOOR == "indoor"


class TestCalculateDetectionZone:
    """Test suite for detection zone calculation"""

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


class TestCalculateDetectionSupercategory:
    """Test suite for COCO supercategory resolution"""

    def test_vehicle_mapping(self):
        assert calculate_detection_supercategory("car") == COCOSupercategory.VEHICLE

    def test_kitchen_mapping(self):
        assert calculate_detection_supercategory("knife") == COCOSupercategory.KITCHEN

    def test_appliance_mapping(self):
        assert calculate_detection_supercategory("microwave") == COCOSupercategory.APPLIANCE

    def test_furniture_mapping(self):
        assert calculate_detection_supercategory("chair") == COCOSupercategory.FURNITURE

    def test_indoor_mapping(self):
        assert calculate_detection_supercategory("toothbrush") == COCOSupercategory.INDOOR

    def test_unknown_class_raises_error(self):
        with pytest.raises(ValueError):
            calculate_detection_supercategory("unknown-object")


class TestDetectedObject:
    """Test suite for DetectedObject model"""

    def test_valid_detected_object(self, sample_detected_object_data):
        """Test DetectedObject creation with valid data"""
        obj = DetectedObject(**sample_detected_object_data)
        assert obj.class_name == "car"
        assert obj.confidence == 0.92
        assert obj.bbox == [0.1, 0.2, 0.5, 0.8]
        assert obj.zone == DetectionZone.BOTTOM
        assert obj.supercategory == COCOSupercategory.VEHICLE

    def test_confidence_lower_bound(self):
        """Test confidence accepts 0.0"""
        obj = DetectedObject(
            class_name="person",
            confidence=0.0,
            bbox=[0.0, 0.0, 1.0, 1.0],
            zone="bottom",
            supercategory="person",
        )
        assert obj.confidence == 0.0

    def test_confidence_upper_bound(self):
        """Test confidence accepts 1.0"""
        obj = DetectedObject(
            class_name="person",
            confidence=1.0,
            bbox=[0.0, 0.0, 1.0, 1.0],
            zone="bottom",
            supercategory="person",
        )
        assert obj.confidence == 1.0

    def test_confidence_below_zero_raises_error(self):
        """Test ValidationError when confidence is below 0"""
        with pytest.raises(ValidationError):
            DetectedObject(class_name="person", confidence=-0.1, bbox=[0.0, 0.0, 1.0, 1.0], zone="bottom", supercategory="person")

    def test_confidence_above_one_raises_error(self):
        """Test ValidationError when confidence is above 1"""
        with pytest.raises(ValidationError):
            DetectedObject(class_name="person", confidence=1.1, bbox=[0.0, 0.0, 1.0, 1.0], zone="bottom", supercategory="person")

    def test_bbox_must_have_four_elements(self):
        """Test ValidationError when bbox has fewer than 4 elements"""
        with pytest.raises(ValidationError):
            DetectedObject(class_name="person", confidence=0.9, bbox=[0.0, 0.0, 1.0], zone="bottom", supercategory="person")

    def test_bbox_too_many_elements_raises_error(self):
        """Test ValidationError when bbox has more than 4 elements"""
        with pytest.raises(ValidationError):
            DetectedObject(class_name="person", confidence=0.9, bbox=[0.0, 0.0, 1.0, 1.0, 0.5], zone="bottom", supercategory="person")

    def test_missing_class_name_raises_error(self):
        """Test ValidationError when class_name is missing"""
        with pytest.raises(ValidationError):
            DetectedObject(confidence=0.9, bbox=[0.0, 0.0, 1.0, 1.0], zone="bottom", supercategory="person")

    def test_invalid_zone_raises_error(self):
        """Test ValidationError when zone is not a valid DetectionZone value"""
        with pytest.raises(ValidationError):
            DetectedObject(
                class_name="person",
                confidence=0.9,
                bbox=[0.0, 0.0, 1.0, 1.0],
                zone="invalid-zone",
                supercategory="person",
            )

    def test_invalid_supercategory_raises_error(self):
        """Test ValidationError when supercategory is not a valid COCOSupercategory value"""
        with pytest.raises(ValidationError):
            DetectedObject(
                class_name="person",
                confidence=0.9,
                bbox=[0.0, 0.0, 1.0, 1.0],
                zone="bottom",
                supercategory="invalid-supercategory",
            )


class TestAlertMessage:
    """Test suite for AlertMessage model"""

    def test_valid_alert_message(self, sample_alert_message_data):
        """Test AlertMessage creation with valid data"""
        msg = AlertMessage(**sample_alert_message_data)
        assert msg.type == "alert"
        assert msg.message == sample_alert_message_data["message"]
        assert msg.severity == AlertSeverity.CRITICAL
        assert len(msg.objects) == 1
        assert msg.timestamp == sample_alert_message_data["timestamp"]

    def test_type_is_always_alert(self, sample_alert_message_data):
        """Test that type field is always 'alert'"""
        msg = AlertMessage(**sample_alert_message_data)
        assert msg.type == "alert"

    def test_objects_defaults_to_empty_list(self):
        """Test objects field defaults to empty list when not provided"""
        msg = AlertMessage(message="Danger", severity="warning", timestamp=1000.0)
        assert msg.objects == []

    def test_invalid_severity_raises_error(self):
        """Test ValidationError when severity is not a valid AlertSeverity value"""
        with pytest.raises(ValidationError):
            AlertMessage(message="Danger", severity="extreme", timestamp=1000.0)

    def test_missing_message_raises_error(self):
        """Test ValidationError when message is missing"""
        with pytest.raises(ValidationError):
            AlertMessage(severity="warning", timestamp=1000.0)

    def test_missing_timestamp_raises_error(self):
        """Test ValidationError when timestamp is missing"""
        with pytest.raises(ValidationError):
            AlertMessage(message="Danger", severity="warning")

    def test_serializes_to_json_with_type(self, sample_alert_message_data):
        """Test model_dump_json includes type field"""
        msg = AlertMessage(**sample_alert_message_data)
        json_str = msg.model_dump_json()
        assert '"type":"alert"' in json_str or '"type": "alert"' in json_str


class TestDetectionMessage:
    """Test suite for DetectionMessage model"""

    def test_valid_detection_message_includes_zone_and_supercategory(self, sample_detected_object_data):
        msg = DetectionMessage(
            objects=[DetectedObject(**sample_detected_object_data)],
            frame_timestamp=1709827200000.0,
            procesing_ms=25.0,
        )

        assert msg.type == "detection"
        assert len(msg.objects) == 1
        assert msg.objects[0].zone == DetectionZone.BOTTOM
        assert msg.objects[0].supercategory == COCOSupercategory.VEHICLE


class TestStatusMessage:
    """Test suite for StatusMessage model"""

    def test_valid_status_message(self):
        """Test StatusMessage creation with valid data"""
        msg = StatusMessage(status="connected", message="Ready")
        assert msg.type == "status"
        assert msg.status == "connected"
        assert msg.message == "Ready"

    def test_message_is_optional(self):
        """Test message field is optional and defaults to None"""
        msg = StatusMessage(status="connected")
        assert msg.message is None

    def test_missing_status_raises_error(self):
        """Test ValidationError when status field is missing"""
        with pytest.raises(ValidationError):
            StatusMessage()

    def test_type_is_always_status(self):
        """Test that type field is always 'status'"""
        msg = StatusMessage(status="ready")
        assert msg.type == "status"


class TestErrorMessage:
    """Test suite for ErrorMessage model"""

    def test_valid_error_message(self):
        """Test ErrorMessage creation with valid data"""
        msg = ErrorMessage(message="Something went wrong", code="INTERNAL_ERROR")
        assert msg.type == "error"
        assert msg.message == "Something went wrong"
        assert msg.code == "INTERNAL_ERROR"

    def test_code_is_optional(self):
        """Test code field is optional and defaults to None"""
        msg = ErrorMessage(message="Something went wrong")
        assert msg.code is None

    def test_missing_message_raises_error(self):
        """Test ValidationError when message field is missing"""
        with pytest.raises(ValidationError):
            ErrorMessage()

    def test_type_is_always_error(self):
        """Test that type field is always 'error'"""
        msg = ErrorMessage(message="oops")
        assert msg.type == "error"

    def test_serializes_to_json_with_type(self):
        """Test model_dump_json includes type field"""
        msg = ErrorMessage(message="oops", code="SOME_CODE")
        json_str = msg.model_dump_json()
        assert '"type":"error"' in json_str or '"type": "error"' in json_str
