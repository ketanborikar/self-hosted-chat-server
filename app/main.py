from fastapi import FastAPI
from app.routes import router
from app.auth import router as auth_router
from app.chat import router as chat_router
from app.websockets import router as ws_router  # ✅ Fix the import
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db

app = FastAPI()

init_db()  # ✅ Runs database setup when the app starts

app.include_router(router)
app.include_router(ws_router)  # ✅ Ensure WebSocket routes are registered here
app.include_router(auth_router)
app.include_router(chat_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
