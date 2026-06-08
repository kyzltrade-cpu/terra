from fastapi import FastAPI

from backend.routers.whatsapp_webhook import router as whatsapp_router

app = FastAPI(title="TerraClean.OS")

app.include_router(whatsapp_router)


@app.get("/health")
def health():
    return {"status": "ok"}
