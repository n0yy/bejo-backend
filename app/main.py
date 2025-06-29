from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.api import chat, upload, health

app = FastAPI(
    title="BEJO - Backend",
    version="1.0.0",
)

# ✅ Tambahkan CORS middleware dengan cara ini:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers (pastikan chat, upload, health, collection sudah di-import)
app.include_router(chat.router)
app.include_router(upload.router)
app.include_router(health.router)
