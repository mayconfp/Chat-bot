import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar a chave da API
openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    # Listar todos os modelos disponíveis
    models = openai.models.list()
    
    print("=== TODOS OS MODELOS DISPONÍVEIS ===")
    for model in models.data:
        print(f"- {model.id}")
    
    print("\n=== MODELOS DE EMBEDDING ===")
    embedding_models = [model.id for model in models.data if 'embedding' in model.id.lower()]
    for model in embedding_models:
        print(f"- {model}")
        
    if not embedding_models:
        print("❌ Nenhum modelo de embedding encontrado!")
        
    print("\n=== MODELOS DE CHAT ===")
    chat_models = [model.id for model in models.data if 'gpt' in model.id.lower() or 'chat' in model.id.lower()]
    for model in chat_models:
        print(f"- {model}")
        
except Exception as e:
    print(f"❌ Erro: {e}") 