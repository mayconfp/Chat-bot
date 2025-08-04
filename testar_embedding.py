import openai
import os
from dotenv import load_dotenv

load_dotenv()

# Configurar a chave da API
openai.api_key = os.getenv('OPENAI_API_KEY')

try:
    # Testar embedding com modelo padrão
    response = openai.embeddings.create(
        input="Teste de embedding",
        model="text-embedding-ada-002"
    )
    print("✅ Embedding funcionou com text-embedding-ada-002!")
    print(f"Tamanho do embedding: {len(response.data[0].embedding)}")
    
except Exception as e:
    print(f"❌ Erro com text-embedding-ada-002: {e}")
    
    try:
        # Testar com outro modelo
        response = openai.embeddings.create(
            input="Teste de embedding",
            model="text-embedding-3-small"
        )
        print("✅ Embedding funcionou com text-embedding-3-small!")
        print(f"Tamanho do embedding: {len(response.data[0].embedding)}")
        
    except Exception as e2:
        print(f"❌ Erro com text-embedding-3-small: {e2}") 