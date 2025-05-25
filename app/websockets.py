from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import store_message, get_offline_messages, validate_user
import logging
import asyncio

logging.basicConfig(filename="/home/ubuntu/Project/log_websocket_debug.log", level=logging.DEBUG)

router = APIRouter()
active_connections = {}

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    logging.debug(f"Attempting WebSocket connection for: {username}")
    
    try:
        await websocket.accept()
        logging.info(f"WebSocket connected for: {username}")

        # ✅ Explicitly log authentication attempt
        if not validate_user(username):
            logging.warning(f"Authentication failed for {username}!")
            await websocket.send_text("❌ Authentication failed!")
            await websocket.close(code=1000)
            return

        active_connections[username] = websocket  
        logging.info(f"User {username} authenticated successfully.")

        # ✅ Log offline message retrieval process
        offline_messages = get_offline_messages(username)
        logging.debug(f"Offline messages for {username}: {offline_messages}")
        
        for sender, message in offline_messages:
            await websocket.send_text(f"{sender}: {message}")

        logging.info(f"User {username} received offline messages.")

        # ✅ WebSocket should stay open with inactivity handling
        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=120)  # ✅ Prevents automatic closure
                
                logging.debug(f"Received data from {username}: {data}")

                if ":" not in data:
                    await websocket.send_text("❌ Invalid message format! Use 'recipient:message'.")
                    continue

                recipient, message = data.split(":", 1)
                store_message(username, recipient, message)
                logging.info(f"Stored message from {username} to {recipient}: {message}")

                if recipient in active_connections:
                    await active_connections[recipient].send_text(f"{username}: {message}")
                else:
                    await websocket.send_text(f"User {recipient} is offline.")

            except asyncio.TimeoutError:
                logging.warning(f"User {username} inactive—keeping connection alive.")
                continue  # ✅ Ensures inactivity doesn’t close connection
                
            except WebSocketDisconnect:
                logging.info(f"User {username} disconnected.")
                del active_connections[username]
                await websocket.close(code=1000)
                logging.info(f"WebSocket properly closed for {username}.")
                break
                
            except Exception as e:
                logging.error(f"WebSocket error for {username}: {str(e)}")
                await websocket.close(code=1000)
                break

    except Exception as e:
        logging.critical(f"Critical WebSocket error for {username}: {str(e)}")
        await websocket.close(code=1000)
