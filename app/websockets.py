from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import store_message, get_offline_messages
import logging

logging.basicConfig(filename="/home/ubuntu/Project/log_websocket_errors.log", level=logging.ERROR)

router = APIRouter()
active_connections = {}

def validate_user(username):
    # ✅ Replace this with actual authentication logic
    return username in allowed_users  # Example validation

from app.database import validate_user  # ✅ Import authentication function

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    await websocket.accept()  # ✅ Accept WebSocket first

    # ✅ Authenticate user from the database
    if not validate_user(username):
        await websocket.send_text("❌ Authentication failed! Invalid user.")
        await websocket.close()
        return

    active_connections[username] = websocket

    # ✅ Broadcast online status
    for user in active_connections.values():
        await user.send_text(f"{username} is now online!")

    try:
        while True:
            data = await websocket.receive_text()
            if ":" not in data:
                await websocket.send_text("❌ Invalid message format! Use 'recipient:message'.")
                continue

            recipient, message = data.split(":", 1)
            store_message(username, recipient, message)

            if recipient in active_connections:
                await active_connections[recipient].send_text(f"{username}: {message}")
            else:
                await websocket.send_text(f"User {recipient} is offline.")
    except Exception as e:
        logging.error(f"WebSocket error for {username}: {str(e)}")
