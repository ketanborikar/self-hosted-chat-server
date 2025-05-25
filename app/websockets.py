from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.database import store_message, get_offline_messages, validate_user
import logging
import asyncio

logging.basicConfig(filename="/home/ubuntu/Project/log_websocket_debug.log", level=logging.DEBUG)

router = APIRouter()
active_connections = {}
default_recipients = {}  # ✅ Store last recipient per user

@router.websocket("/ws/{username}")
async def websocket_endpoint(websocket: WebSocket, username: str):
    logging.debug(f"Attempting WebSocket connection for: {username}")

    try:
        await websocket.accept()
        logging.info(f"WebSocket connected for: {username}")

        # ✅ Authenticate user
        if not validate_user(username):
            logging.warning(f"Authentication failed for {username}!")
            await websocket.send_text("❌ Authentication failed!")
            await websocket.close(code=1000)
            return

        active_connections[username] = websocket  
        default_recipients[username] = None  # ✅ Initialize default recipient

        # ✅ Retrieve offline messages
        offline_messages = get_offline_messages(username)
        for sender, message in offline_messages:
            await websocket.send_text(f"{sender}: {message}")

        while True:
            try:
                data = await asyncio.wait_for(websocket.receive_text(), timeout=120)  
                logging.debug(f"Received data from {username}: {data}")

                if ":" in data:  
                    recipient, message = data.split(":", 1)
                    default_recipients[username] = recipient  # ✅ Store last recipient
                else:
                    recipient = default_recipients.get(username)
                    if not recipient:
                        await websocket.send_text("❌ No recipient set! Please specify one.")
                        continue
                    message = data  

                store_message(username, recipient, message)
                logging.info(f"Stored message from {username} to {recipient}: {message}")

                if recipient in active_connections:
                    await active_connections[recipient].send_text(f"{username}: {message}")
                else:
                    await websocket.send_text(f"User {recipient} is offline.")

            except asyncio.TimeoutError:
                logging.warning(f"User {username} inactive—keeping connection alive.")
                continue  
                
            except WebSocketDisconnect:
                logging.info(f"User {username} disconnected.")
                del active_connections[username]
                del default_recipients[username]  # ✅ Cleanup recipient tracking
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
