from fastapi import FastAPI
from app.api.v1.endpoints import webhooks, contacts, ws, conversations

app = FastAPI(title="API do Gabinete do Deputado",
             description="API para atendimento virtual do gabinete do deputado",
             version="1.0.0")

app.include_router(
    webhooks.router,
    prefix="/api/v1",
    tags=["webhooks"]
)

app.include_router(
    contacts.router,
    prefix="/api/v1/contacts",
    tags=["contacts"]
)

app.include_router(
    ws.router,
    prefix="/api/v1/ws",
    tags=["ws"]
)

app.include_router(
    conversations.router,
    prefix="/api/v1/conversations",
    tags=["conversations"]
)

@app.get("/")
async def root():
    return {"message": "API do Gabinete do Deputado - Webhook WhatsApp"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)