import os
from fastapi import FastAPI
from dotenv import load_dotenv

# Load environment variables from .env file before anything else
load_dotenv()

from backend.routers.whatsapp_webhook import router as whatsapp_router
from backend.routers.bid_copilot import router as bid_copilot_router

app = FastAPI(title="Terra")

app.include_router(whatsapp_router)
app.include_router(bid_copilot_router)


@app.get("/health")
def health():
    return {"status": "ok"}
