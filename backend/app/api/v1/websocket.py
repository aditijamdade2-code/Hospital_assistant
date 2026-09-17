import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.services.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(tags=["WebSocket"])

@router.websocket("/ws/staff")
async def staff_dashboard_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for the staff dashboard.
    Receives real-time events:
    - NEW_ENCOUNTER
    - PATIENT_MESSAGE
    - RED_FLAG_DETECTED
    - PRIORITY_CHANGED
    - ESCALATION_TRIGGERED
    - STAFF_ACKNOWLEDGED
    - ENCOUNTER_UPDATED
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep-alive / incoming ping handling from staff dashboard
            data = await websocket.receive_text()
            # Optional ping response
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.warning(f"WebSocket client error: {e}")
        ws_manager.disconnect(websocket)
