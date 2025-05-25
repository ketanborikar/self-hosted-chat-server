from fastapi import APIRouter
from app.websocket import websocket_endpoint

router = APIRouter()

router.add_api_websocket_route("/ws", websocket_endpoint)
