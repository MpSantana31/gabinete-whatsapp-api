from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from app.db.session import get_db
from app.crud.crud_message import crud_message
from sqlalchemy.orm import Session

router = APIRouter()

@router.websocket("/history/{session_id}")
async def websocket_history(websocket: WebSocket, session_id: str):
    await websocket.accept()
    db = next(get_db())
    try:
        # Busca todas as mensagens do usuário (session_id)
        messages = crud_message.get_by_session(db, session_id)
        # Envia o histórico como lista de dicts (serializável)
        history = [
            {
                "id": msg.id,
                "sender": msg.sender,
                "content": msg.content,
                "created_at": msg.created_at.isoformat() if msg.created_at else None,
                "metadata": msg.message_metadata,
            }
            for msg in messages
        ]
        await websocket.send_json({"history": history})

        # (Opcional) Mantenha o socket aberto para enviar novas mensagens em tempo real
        while True:
            await websocket.receive_text()  # Apenas para manter a conexão aberta
            # Aqui você pode implementar lógica para push de novas mensagens

    except WebSocketDisconnect:
        print(f"WebSocket desconectado para session_id: {session_id}")