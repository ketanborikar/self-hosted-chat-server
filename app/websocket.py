from fastapi import WebSocket

async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("✅ WebSocket Connected")

    try:
        while True:
            data = await websocket.receive_text()
            print(f"📥 Received: {data}")
            await websocket.send_text(f"Echo: {data}")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        print("❌ WebSocket Closed")
