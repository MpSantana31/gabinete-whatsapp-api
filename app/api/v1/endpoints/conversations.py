# app/api/v1/endpoints/webhooks.py

from fastapi import APIRouter

# Importe os serviços necessários
from app.services.whatsapp_service import enviar_resposta_padrao
from app.crud.crud_message import crud_message
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from datetime import datetime

router = APIRouter()

# QUERO O ENDPOINT PARA enviar mensagem personalizada

@router.post("/send")
def send_message(phone_number: str, message: str):
    response = enviar_resposta_padrao(phone_number, message)
    return response

@router.get("/messages/{phone_number}")
def get_messages(phone_number: str, db: Session = Depends(get_db)):
    return crud_message.get_by_session(phone_number, db)

@router.get("/messages/")
def get_messages(db: Session = Depends(get_db)):
    try:
        result = crud_message.get_all(db)
    except Exception as e:
        return {
            "message": "Erro ao buscar mensagens",
            "code": 500,
            "success": False,
            "result": str(e)
        }

    response = {
        "total": len(result),
        "message": "Lista de todas as mensagens",
        "code": 200,
        "success": True,
        "result": result
    }
    return response

@router.get("/messages/user/")
def get_messages_user(db: Session = Depends(get_db)):
    try:
        result = crud_message.get_all(db)
    except Exception as e:
        return {
            "message": "Erro ao buscar mensagens",
            "code": 500,
            "success": False,
            "result": str(e)
        }

    result = [message for message in result if message.sender == "user"]

    response = {
        "total": len(result),
        "message": "Lista de todas as mensagens do usuário  ",
        "code": 200,
        "success": True,
        "result": result
    }
    return response

@router.get("/messages/ia/")
def get_messages_ia(db: Session = Depends(get_db)):
    try:
        result = crud_message.get_all(db)
    except Exception as e:
        return {
            "message": "Erro ao buscar mensagens",
            "code": 500,
            "success": False,
            "result": str(e)
        }

    result = [message for message in result if message.sender == "ia"]

    response = {
        "total": len(result),
        "message": "Lista de todas as mensagens do IA",
        "code": 200,
        "success": True,
        "result": result
    }
    return response

@router.get("/messages/mean-time/ia")
def get_messages_mean_time_ia(db: Session = Depends(get_db)):
    try:
        # Busca todas as mensagens ordenadas por data de criação
        messages = crud_message.get_all(db)
        
        messages_sorted = sorted(messages, key=lambda x: x.created_at)
        
        response_times = []
        user_message_time = None


        for message in messages_sorted:
            if message.sender == "user":
                # Armazena o horário da mensagem do usuário
                user_message_time = message.created_at
            elif user_message_time is not None and message.sender == "ai":
                # Calcula a diferença em segundos entre a resposta e a mensagem do usuário
                response_time = (message.created_at - user_message_time).total_seconds()
                response_times.append(response_time)
                user_message_time = None  # Reseta para a próxima mensagem

        
        # Calcula a média dos tempos de resposta em segundos
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Converte para minutos e segundos para melhor legibilidade
        avg_minutes = int(avg_response_time // 60)
        avg_seconds = int(avg_response_time % 60)
        
        response = {
            "total_messages": len(messages),
            "total_responses": len(response_times),
            "average_response_time_seconds": round(avg_response_time, 2),
            "average_response_time_formatted": f"{avg_minutes} minutos e {avg_seconds} segundos",
            "message": "Tempo médio de resposta calculado com sucesso",
            "code": 200,
            "success": True
        }
    except Exception as e:
        return {
            "message": "Erro ao buscar mensagens",
            "code": 500,
            "success": False,
            "result": str(e)
        }
    return response
