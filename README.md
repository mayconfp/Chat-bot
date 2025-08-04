# Chat com Leitura de Arquivos - Bluey

Sistema de chat com IA que lê arquivos PDF e salva conversas automaticamente.

## 📋 Pré-requisitos

- Python 3.8 ou superior
- Chave da API OpenAI

## 🚀 Instalação

### 1. Verificar Python
```bash
python --version
# ou
python3 --version
```

### 2. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd teste-bluey
```

### 3. Criar ambiente virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 4. Instalar dependências
```bash
pip install -r requirements.txt
```

### 5. Configurar variáveis de ambiente
Criar arquivo `.env` na raiz do projeto:
```bash
# Windows
echo OPENAI_API_KEY=sua_chave_aqui > .env

# Linux/Mac
echo "OPENAI_API_KEY=sua_chave_aqui" > .env
```

Ou criar manualmente o arquivo `.env` com:
```
OPENAI_API_KEY=sua_chave_aqui
```

### 6. Executar o projeto
```bash
cd Projeto
streamlit run conversation.py
```

## 📁 Estrutura do Projeto

```
teste-bluey/
├── .env                    # Chave da API OpenAI
├── requirements.txt        # Dependências
├── Projeto/
│   ├── conversation.py    # Aplicação principal
│   ├── criar_db.py       # Script para criar banco de dados
│   ├── mensagens/        # Conversas salvas
│   └── configuracoes/    # Configurações
├── banco_de_dados/       # Base de dados vetorial
└── base_conhecimento/    # Arquivos PDF para leitura
```

## 🔧 Funcionalidades

- ✅ Chat com IA baseado em documentos PDF
- ✅ Salvamento automático de conversas
- ✅ Lista de conversas no sidebar
- ✅ Botão para nova conversa
- ✅ Botão para excluir conversas antigas
- ✅ Persistência entre sessões

## 🚨 Solução de Problemas

### Erro de Chroma deprecated
```bash
pip install langchain-chroma
```

### Erro de chave da API
Verificar se o arquivo `.env` está na raiz e contém:
```
OPENAI_API_KEY=sua_chave_aqui
```

### Erro de dependências
```bash
pip install --upgrade -r requirements.txt
```

## 📝 Uso

1. Execute `streamlit run conversation.py`
2. Acesse http://localhost:8501
3. Faça perguntas sobre os documentos da empresa Bluey
4. As conversas são salvas automaticamente
5. Use o sidebar para gerenciar conversas

## 🔑 Obter Chave OpenAI

1. Acesse https://platform.openai.com
2. Crie uma conta ou faça login
3. Vá em "API Keys"
4. Crie uma nova chave
5. Copie a chave para o arquivo `.env` 