"""
Live Session WebSocket Message Models

Defines the message protocol for real-time communication between
the mobile app and the backend during a live camera session.

Client → Server: frame (JPEG base64), audio_chunk (PCM base64)
Server → Client: alert, detection, status, error
"""

from enum import Enum
from typing import Literal, Optional
from pydantic import BaseModel, Field
from backend.ai.yolo.coco_taxonomy import COCOSupercategory

# Client -> Server messages

class ClientMessageType(str,Enum):
    """
    Types of messages the client can send
    """
    FRAME = "frame"

class FrameMessage(BaseModel):
    """
    A single video frame captured by the device camera.
    Data is a JPEG imgage encoded as base64 string.
    Yolov26 expects JPEG/PNG input - base64 JPEG is the transport format.
    """
    type: Literal["frame"] ="frame"
    data: str = Field(..., description="Base64-encoded JPEG image")
    timestamp: float = Field(..., description="Unix timestamp (ms) when the frame was captured")


# Server -> Client messages

class ServerMessageTypes(str, Enum):
    """
    Types of messages the server can send
    """
    ALERT = "alert"
    DETECTION = "detection"
    STATUS = "status"
    ERROR = "error"

class AlertSeverity(str,Enum):
    """
    Severity levels for danger alerts
    """
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

class DetectionZone(str,Enum):
    """
    Vertical risk zones for a detection inside the image
    """
    TOP = "top"
    CENTER = "center"
    BOTTOM = "bottom"

def calculate_detection_zone(bbox: list[float]) -> DetectionZone:
    """
    Classify a detection into a vertical zone using the bottom edge of the
    bbox. Remember that the bbox format is: [x1, y1, x2, y2], normalized
    between 0-1
    """

    y2 = bbox[3]

    if y2 < (1/3):
        return DetectionZone.TOP
    if y2 < (2/3):
        return DetectionZone.CENTER
    return DetectionZone.BOTTOM

class DetectedObject(BaseModel):
    """
    A single object detected in the frame
    """
    class_name: str = Field(..., description= "COCO class name")
    confidence: float = Field(..., ge=0.0, le= 1.0, description="Detection confidence 0-1")
    bbox: list[float] = Field(..., min_length=4, max_length=4, description="Bounding box [x1, y1, x2, y2] normalized 0-1")
    zone: DetectionZone = Field(..., description="Vertical risk zone for detection")
    supercategory: COCOSupercategory = Field(..., description="Official COCO supercategory for the detected class")


class AlertMessage(BaseModel):
    """
    Danger alert sent to the client when a hazardous object is detected.
    The client should notify the user.
    """
    type: Literal["alert"] = "alert"
    message: str = Field(..., description="Human-readable alert message")
    severity: AlertSeverity = Field(..., description="Alert severity level")
    objects: list[DetectedObject] = Field(default_factory=list, description="Objects that triggered the alert")
    timestamp: float = Field(..., description="Server unix timestamp (ms)")

class DetectionMessage(BaseModel):
    """
    Raw detection results for a processed frame.
    Useful for debugging / visualization on the client
    """
    type: Literal["detection"] = "detection"
    objects: list[DetectedObject] = Field(default_factory=list, description="Objects detected in the frame")
    frame_timestamp: float = Field(..., description="Original frame timestamp")
    procesing_ms: float = Field(..., description="Time taken to process the frame in ms")

class StatusMessage(BaseModel):
    """
    Connection or processing status update
    """
    type: Literal["status"] = "status"
    status: str = Field(..., description="Status indentifier (connected, processing, ready)")
    message: Optional[str] = Field(default=None, description="Optional human-readable detail")

class ErrorMessage(BaseModel):
    """
    Error message sent to the client
    """
    type: Literal["error"] = "error"
    message: str = Field(..., description="Error description")
    code: Optional[str] = Field(default=None, description="Error code for programmatic handling")

    