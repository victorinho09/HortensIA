"""
Live Session WebSocket Router

Handles real-time video/audio streaming from the mobile app.
Validates session on connection, receives frames and audio chunks,
and sends back alerts/detections/status messages.
"""


import json
import logging
import os
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.databases.connection import get_db
from backend.service.dependencies import validate_session
from backend.models.websocket import (
    DetectionTelemetry,
    FrameMessage,
    StatusMessage,
    ErrorMessage,
    DetectionMessage,
)
from backend.ai.yolo.detector import YOLODetector

logger = logging.getLogger(__name__)

router = APIRouter()


def _is_demo_mode() -> bool:
    """
    Whether the server runs in demo mode (e.g. inside Docker for the TFG jury).
    In demo mode the WebSocket session validation against PostgreSQL is skipped,
    so the detection pipeline can be exercised without a database or real auth.
    Controlled by the HORTENSIA_DEMO_MODE environment variable.
    """
    return os.getenv("HORTENSIA_DEMO_MODE", "").strip().lower() in {"1", "true", "yes", "on"}

async def _send_message(websocket: WebSocket, message) -> None:
    """
    Send a Pydantic model as JSON through the WebSocket.
    model_dump_json() is a method that Pydantic includes inside all the models to convert any object into JSON
    """
    await websocket.send_text(message.model_dump_json())

def _parse_client_message(raw: str) -> FrameMessage | None:
    """
    Parse a raw JSON string into the appropiate client message model.
    Returns None if the message type is unknown or invalid.
    """
    try: 
        data = json.loads(raw)
    except json.JSONDecodeError:
        return None
    
    msg_type = data.get("type")

    if msg_type == "frame":
        return FrameMessage(**data)
    
    return None

@router.websocket("/live/{session_id}")
async def live_session(websocket: WebSocket, session_id: str):
    """
    Main WebSocket endpoint for live camera sessions.
    
    Flow:
    1. Validate session_id against the database
    2. Accept connection
    3. Receive loop: parse messages by type, handle accordingly
    4. Clean up on disconnect
    """
    detector = YOLODetector()

    if _is_demo_mode():
        # Demo mode (Docker/TFG): skip database-backed session validation entirely
        # so the detection pipeline can be tested with stored sample images.
        logger.warning("DEMO MODE active: skipping session validation for session_id=%s", session_id)
    else:
        # In REST endpoints, FastAPI handles the db session lifecycle automatically via Depends(get_db).
        # WebSockets are not managed by FastAPI's dependency injection after the connection is established,
        # so we must manually obtain the session with next() and close it ourselves in the finally block.
        db = next(get_db())

        try: 
            user = await validate_session(session_id, db)
            if not user: 
                await websocket.close(code=4001, reason="Invalid or expired session id")
                return
        finally:
            db.close()
    
    #Accept connection
    await websocket.accept()
    logger.info("Live session connected: session_id=%s", session_id)

    await _send_message(websocket,StatusMessage(
        status="connected",
        message="Session validated, ready to receive frames"
    ))

    #Receive loop
    try:
        while True:
            raw = await websocket.receive_text()
            message = _parse_client_message(raw)

            if message is None:
                await _send_message(websocket, ErrorMessage(
                    message="Invalid message format or unknown type",
                    code="INVALID_MESSAGE"
                ))
                continue

            if isinstance(message, FrameMessage):
                try:
                    server_received_at = int(time.time() * 1000)
                    process_started_at = time.perf_counter()

                    frame_timestamp_ms = (message.telemetry.capture_finished_at if message.telemetry is not None else message.timestamp)
                    detections, processing_ms, scene_risk, frame_width, frame_height = detector.detect(message.data,frame_timestamp_ms=frame_timestamp_ms)

                    server_responded_at = int(time.time() * 1000)
                    telemetry = DetectionTelemetry(
                        frame_id=message.telemetry.frame_id if message.telemetry else None,
                        capture_started_at=message.telemetry.capture_started_at if message.telemetry else None,
                        capture_finished_at=message.telemetry.capture_finished_at if message.telemetry else None,
                        encode_finished_at=message.telemetry.encode_finished_at if message.telemetry else None,
                        sent_at=message.telemetry.sent_at if message.telemetry else None,
                        server_received_at=server_received_at,
                        server_responded_at=server_responded_at,
                        processing_ms=round((time.perf_counter() - process_started_at) * 1000, 1),
                    )
                    logger.debug(
                        "Detections (%.1fms): %s | scene_risk=%.3f smoothed=%.3f severity=%s",
                        processing_ms,
                        [(d.class_name, round(d.confidence, 2)) for d in detections],
                        scene_risk.instant,
                        scene_risk.smoothed,
                        scene_risk.severity,
                    )
                    await _send_message(websocket,DetectionMessage(
                        objects= detections,
                        frame_timestamp= message.timestamp,
                        frame_width=frame_width,
                        frame_height=frame_height,
                        procesing_ms=processing_ms,
                        telemetry=telemetry,
                        scene_risk=scene_risk,
                    ))
                    logger.debug("Frame received correctly. Ts:%.0f len: %d", message.timestamp, len(message.data))
                except ValueError as e:
                    logger.warning("Invalid frame data: {%s}", str(e))
            
    except WebSocketDisconnect:
        logger.info("Live session disconnected: session_id=%s", session_id)
    except Exception as e:
        logger.error("Live session error session_id=%s: %s",session_id,str(e))
        try:
            await _send_message(websocket, ErrorMessage(
                message="Internal Server Error",
                code="INTERNAL_ERROR"
            ))
        except Exception:
            pass


