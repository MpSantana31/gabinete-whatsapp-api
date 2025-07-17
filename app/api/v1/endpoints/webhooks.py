from fastapi import APIRouter, Request, Response, HTTPException
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any

# Importe os serviços necessários
from app.services.ai_service import AIAssistant
from app.services.whatsapp_service import enviar_resposta_padrao, enviar_template
from app.core.config import VERIFY_TOKEN
from app.db.session import get_db
from app.schemas.contact import ContactUpdate
from app.crud.crud_contact import crud_contact


# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/webhook")
async def verify_webhook(request: Request):
    """
    Endpoint de verificação do webhook do WhatsApp.
    
    Este endpoint é chamado pelo WhatsApp para verificar a autenticidade do webhook.
    """
    logger.info("Iniciando verificação do webhook...")
    
    # Log dos cabeçalhos para depuração
    logger.debug(f"Headers recebidos: {dict(request.headers)}")
    
    query_params = request.query_params
    mode = query_params.get("hub.mode")
    token = query_params.get("hub.verify_token")
    challenge = query_params.get("hub.challenge")
    
    logger.info(f"Parâmetros recebidos - Mode: {mode}, Token: {'****' if token else 'não fornecido'}, Challenge: {challenge}")
    
    if mode == "subscribe" and token == VERIFY_TOKEN:
        logger.info("Webhook verificado com sucesso!")
        logger.debug(f"Retornando challenge: {challenge}")
        return Response(content=challenge, media_type="text/plain", status_code=200)
    else:
        error_msg = "Falha na verificação do webhook"
        if mode != "subscribe":
            error_msg += f" - Modo inválido: {mode}"
        if token != VERIFY_TOKEN:
            error_msg += " - Token de verificação inválido"
        
        logger.warning(error_msg)
        logger.debug(f"Token esperado: {VERIFY_TOKEN}, Token recebido: {token}")
        logger.debug(f"Modo esperado: 'subscribe', Modo recebido: {mode}")
        
        raise HTTPException(status_code=403, detail="Falha na verificação do token.")

async def process_message(message_data: Dict[str, Any], type: str):
    """
    Processa uma mensagem de texto:
    1. Obtém a instância correta do assistente para o usuário.
    2. Passa o controle para a função 'enviar_resposta_padrao'.
    """
    sender_id = message_data.get('from')

    if not sender_id:
        logger.warning(f"Mensagem inválida ou sem remetente: {message_data}")
        return
    
    logger.info(f"Processando mensagem de {sender_id}")

    try:
        db = next(get_db())

        contact = crud_contact.get_or_create(db, sender_id)
        
        now = datetime.now(contact.updated_at.tzinfo) if contact.updated_at else datetime.utcnow()
        
        if contact.updated_at is None or contact.updated_at < now - timedelta(hours=24):
            updated_contact = crud_contact.update(db, contact, ContactUpdate(
                updated_at=now,
                status=True
            ))
            await enviar_template(updated_contact.phone_number, "boas_vindas_deputado_oseas", {})

            return True

    
        updated_contact = crud_contact.update(db, contact, ContactUpdate(
            updated_at=now,
            status=True
        ))

        if not contact.ia_active:
            return False

        assistant = AIAssistant.get_instance(session_id=sender_id)

        if type == "text":
            text_body = message_data.get('text', {}).get('body')
        elif type == "button":
            text_body = message_data.get('button', {}).get('payload')
        else:
            return False
        
        await enviar_resposta_padrao(
            numero_destino=sender_id,
            mensagem_recebida=text_body,
            assistant=assistant
        )
        
        logger.info(f"Envio finalizado para {sender_id}")

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
                                if await process_message(message, 'text'):
                                    continue
                            elif message.get('type') == 'button':
                                payload = message.get('button').get('payload')
                                if payload:
                                    await process_message(message, 'button')
                                    continue
            
            return JSONResponse(content={"status": "ok"}, status_code=200)
        else:
            raise HTTPException(status_code=404, detail="Evento não é do WhatsApp.")

    except Exception as e:
        logger.error(f"Erro inesperado no webhook: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"error": "Internal server error"})