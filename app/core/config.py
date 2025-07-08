import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações da API do WhatsApp
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN").strip()
PHONE_ID = os.getenv("PHONE_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")

# Configurações da API do OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY").strip()
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://api.openai.com/v1")

# Configurações do Assistente
ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "gpt-4o-mini-2024-07-18")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SETTINGS = os.getenv("SETTINGS")