# app/api/v1/endpoints/webhooks.py

from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import json
import logging
from typing import Dict, Any

# Importe os serviços necessários
from app.services.ai_service import AIAssistant
from app.services.whatsapp_service import enviar_resposta_padrao
from app.core.config import VERIFY_TOKEN
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.contact import ContactCreate
from app.crud.crud_contact import crud_contact


# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint de verificação do webhook do WhatsApp (Challenge-Response check)."""
    query_params = request.query_params
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso!")
        return Response(content=challenge, media_type="text/plain", status_code=200)
    else:
        logger.warning("Falha na verificação do webhook.")
        raise HTTPException(status_code=403, detail="Falha na verificação do token.")

async def process_text_message(message_data: Dict[str, Any]):
    """
    Processa uma mensagem de texto:
    1. Obtém a instância correta do assistente para o usuário.
    2. Passa o controle para a função 'enviar_resposta_padrao'.
    """
    sender_id = message_data.get('from')
    text_body = message_data.get('text', {}).get('body')

    if not sender_id or not text_body:
        logger.warning(f"Mensagem inválida ou sem texto/remetente: {message_data}")
        return
    
    logger.info(f"Processando mensagem de {sender_id}: '{text_body}'")

    try:
        db = next(get_db())

        contact = crud_contact.get_or_create(db, sender_id)
        
        # Se IA desativada, responde padrão
        if not contact.ia_active:
            return False

        # 1. Obtém ou cria a instância do assistente para este usuário.
        assistant = AIAssistant.get_instance(session_id=sender_id)

        # 2. CHAMA A SUA FUNÇÃO 'enviar_resposta_padrao' DO JEITO QUE ELA ESPERA.
        #    Passamos a mensagem original e o objeto do assistente.
        #    A geração da resposta vai acontecer DENTRO de 'enviar_resposta_padrao'.
        await enviar_resposta_padrao(
            numero_destino=sender_id,
            mensagem_recebida=text_body,
            assistant=assistant
        )
        
        logger.info(f"Função de envio finalizada para {sender_id}")

    except Exception as e:
        logger.error(f"Erro inesperado ao processar mensagem de {sender_id}: {str(e)}", exc_info=True)
        # Não enviamos resposta de erro aqui, pois a própria função de envio pode já ter tratado.

@router.post("/webhook")
async def webhook_handler(request: Request):
    """Webhook principal que recebe todos os eventos da conta do WhatsApp."""
    try:
        data = await request.json()
        logger.debug(f"Dados recebidos: {json.dumps(data, indent=2)}")

        if data.get('object') == 'whatsapp_business_account':
            for entry in data.get('entry', []):
                for change in entry.get('changes', []):
                    value = change.get('value', {})
                    if 'messages' in value:
                        for message in value['messages']:
                            if message.get('type') == 'text':
                                await process_text_message(message)
            
            return JSONResponse(content={"status": "ok"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Evento não é do WhatsApp.")

    except Exception as e:
        logger.error(f"Erro inesperado no webhook: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})