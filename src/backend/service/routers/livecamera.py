"""
Live Session WebSocket Router

Handles real-time video/audio streaming from the mobile app.
Validates session on connection, receives frames and audio chunks,
and sends back alerts/detections/status messages.
"""


import json
import logging

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.databases.connection import get_db
from backend.service.dependencies import validate_session
from backend.models.websocket import (
    FrameMessage,
    StatusMessage,
    ErrorMessage,
)

logger = logging.getLogger(__name__)

router = APIRouter()

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

    #Validate session before accepting the websocket

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
                #TODO: Forward message to Yolov8
                logger.debug("Frame received correctly. Ts:%.0f len: %d", message.timestamp, len(message.data))
            
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


