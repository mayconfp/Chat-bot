import streamlit as st
import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma, chroma
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pathlib import Path
import pickle
import re
from unidecode import unidecode

load_dotenv()

# Função para obter a API key com fallback para diferentes fontes
def get_openai_api_key():
    # 1. Primeiro tenta variável de ambiente
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and api_key != "sua_chave_aqui":
        return api_key
    
    # 2. Se não encontrar, tenta secrets do Streamlit
    try:
        api_key = st.secrets.get("OPENAI_API_KEY")
        if api_key and api_key != "sua_chave_aqui":
            return api_key
    except:
        pass
    
    # 3. Se ainda não encontrar, retorna None
    return None

# Verifica se a API key está disponível
OPENAI_API_KEY = get_openai_api_key()
if not OPENAI_API_KEY:
    st.error("⚠️ OPENAI_API_KEY não encontrada! Configure a variável de ambiente OPENAI_API_KEY ou adicione no arquivo .streamlit/secrets.toml")
    st.stop()


PASTA_MENSAGENS = Path(__file__).parent / 'mensagens'
PASTA_MENSAGENS.mkdir(exist_ok=True)
CACHE_DESCONVERTE = {}

CAMINHO_BANCO_DE_DADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'banco_de_dados'))
print(f"DEBUG - CAMINHO_BANCO_DE_DADOS: {CAMINHO_BANCO_DE_DADOS}")

def pagina_chat():
    #nosso title da page do chat
    st.header("ChatBot da Bluey", divider=True) #linha abaixo do nosso titulo

    #se nao ter mensagem ele retorna apenas vazia
    mensagens = st.session_state.get('mensagens', [])

    #para cada mensagem ele mostra a mensagens 
    for mensagem in mensagens:
        # caso a msg seja do usuario ele vai mostrar ao lado como usuario se nao como a IA
        chat = st.chat_message('user' if mensagem['role'] == 'user' else 'assistant')
        chat.markdown(mensagem['content'])

    entrada_usuario = st.chat_input("Escreva sua mensagem aqui")

    #guarda a lista d msgs do user

    st.session_state.mensagens = mensagens

    if entrada_usuario:
    
        
        # adiciona a mensagem dele a uma lista de mensagens 
        mensagens.append({'role':  'user', 'content': entrada_usuario})

        #exibir a mensagem sua
        st.chat_message('user').markdown(entrada_usuario)

        #atualiza a lista de mensagens e guarda nessse session state
        st.session_state.mensagens = mensagens


    #gerar resposta para IA com base no contexto e na pergunta do usuario
    def gerar_resposta(mensagens, entrada_usuario):

        openai_api_key = get_openai_api_key()
        db = Chroma(persist_directory=CAMINHO_BANCO_DE_DADOS, embedding_function=OpenAIEmbeddings(openai_api_key=openai_api_key, model='text-embedding-3-small'))

        # Busca similaridade
        resultados = db.similarity_search_with_relevance_scores(entrada_usuario, k=4)# o k é a qtd dos resultadados que vc qr qt mais aumenta mais contexto ele vai usar
        if len(resultados) == 0 or resultados[0][1] < 0.5:
            print("Não conseguiu encontrar nenhuma informação relevante na base")
            # return "Desculpe, não encontrei informações relevantes sobre esse assunto na base de dados."

        textos_resultado = []
        if len(resultados) > 0:
            for resultado in resultados:
                texto = resultado[0].page_content
                textos_resultado.append(texto)

        base_conhecimentos = "\n".join(textos_resultado) if textos_resultado else "Informações gerais sobre a empresa Bluey."

        prompt_resposta_da_ia = f"""
            Você é a Vitória, assistente da empresa Bluey.
            
            Informações da empresa extraídas dos documentos: {base_conhecimentos}
            
            Responda à pergunta: {entrada_usuario}
            
            IMPORTANTE: Sempre cite a origem das informações quando possível, mencionando que os dados vêm dos documentos da empresa Bluey.
            
            Se não houver informações específicas, seja amigável e ofereça ajuda.
            """


        model = ChatOpenAI(
            openai_api_key=get_openai_api_key(),
            model='gpt-4o',
            temperature=0.5,
            max_tokens=2000
        )

        # vai receber o prompt e todas as mensagens usuário + IA para manter contexto
        resposta = model.invoke([prompt_resposta_da_ia]+mensagens)
        return resposta.content

    # caso tenha mensagem do user ele criar a respost chamando a func gerar resposta
    if entrada_usuario:
        resposta_ia = gerar_resposta(mensagens, entrada_usuario)

        #exibe a resposta da IA
        st.chat_message('assistant').markdown(resposta_ia)

        #vai adc a resp da Ia a lista de msgs
        mensagens.append({'role': 'assistant', 'content': resposta_ia})

        #repetimos para guardar para qd user enviar mensagem de novo
        st.session_state.mensagens = mensagens

        if len(mensagens) >= 2:  # Só salva se tiver pelo menos uma pergunta e uma resposta
            salvar_mensagens(mensagens)

        

#SALVAMENTO E LEITURA DE CONVERSAS =================================================
def converte_nome_mensagem(nome_mensagem):
    nome_arquivo = unidecode(nome_mensagem)
    nome_arquivo = re.sub('\\W+', '', nome_arquivo).lower()
    return nome_arquivo


def desconverte_nome_mensagem(nome_arquivo):
    if not nome_arquivo in CACHE_DESCONVERTE:
        
        nome_mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo, key='nome_mensagem')
        
        CACHE_DESCONVERTE[nome_arquivo] = nome_mensagem
        
    return CACHE_DESCONVERTE[nome_arquivo]
    


def retorna_nome_da_mensagem(mensagens):
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    return nome_mensagem
          


def salvar_mensagens(mensagens):
    if len(mensagens) == 0:
        return False
    nome_mensagem = ''
    
    for mensagem in mensagens:
        if mensagem['role'] == 'user':
            nome_mensagem = mensagem['content'][:30]
            break
    
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    arquivo_salvar = {'nome_mensagem': nome_mensagem,
                      'nome_arquivo': nome_arquivo,
                      'mensagem': mensagens}
    
    with open(PASTA_MENSAGENS / nome_arquivo, 'wb') as f:
        pickle.dump(arquivo_salvar, f)
    
    
def ler_mensagem_por_nome_arquivo(nome_arquivo, key='mensagem'):
    with open (PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
    return mensagens[key]
    


def ler_mensagens(mensagens, key='mensagem'):
    if len (mensagens) == 0:
        return []
    
    nome_mensagem = retorna_nome_da_mensagem(mensagens)
    nome_arquivo = converte_nome_mensagem(nome_mensagem)
    with open (PASTA_MENSAGENS / nome_arquivo, 'rb') as f:
        mensagens = pickle.load(f)
        
    return mensagens[key]



def listar_conversas():
    conversas = list(PASTA_MENSAGENS.glob('*'))    
    conversas = sorted(conversas, key=lambda item: item.stat().st_mtime_ns, reverse=True)
    return [c.stem for c in conversas]

def excluir_conversa(nome_arquivo):
    if (PASTA_MENSAGENS / nome_arquivo).exists():
        os.remove(PASTA_MENSAGENS / nome_arquivo)
        st.session_state['mensagens'] = []
        st.session_state['conversa_atual'] = ''
    else:
        st.error('Conversa não encontrada!')


def tab_conversas(tab):
    tab.button('➕ Nova conversa',
               on_click=seleciona_conversa, 
               args=('',),
               use_container_width=True)
    tab.markdown('')
    conversas = listar_conversas()
    
    for nome_arquivo in conversas:
        nome_mensagem = desconverte_nome_mensagem(nome_arquivo).capitalize()
        if len (nome_mensagem) == 30:
            nome_mensagem += '...'
            
        col1, col2 = tab.columns([0.85, 0.15])
        
        col1.button(
            label=nome_mensagem,
            on_click=seleciona_conversa,
            args=(nome_arquivo,),
            key=f'conversa_{nome_arquivo}',
            disabled = nome_arquivo==st.session_state['conversa_atual'],
            use_container_width=True,                  
        )
        col2.button(
            label='🗑️',
            on_click=excluir_conversa,
            args=(nome_arquivo,),
            key=f'deletar_{nome_arquivo}',
            use_container_width=True,
        )
            
        
def seleciona_conversa(nome_arquivo):
    if nome_arquivo == '':
        st.session_state.mensagens = []
    else:
        mensagem = ler_mensagem_por_nome_arquivo(nome_arquivo, key='mensagem')
        st.session_state.mensagens = mensagem
    st.session_state['conversa_atual'] = nome_arquivo

#inicializacao das conversas e da conversa atual
def inicializacao():
    if not 'mensagens' in st.session_state:
        st.session_state.mensagens = []
    if not 'conversa_atual' in st.session_state:
        st.session_state.conversa_atual = ''

    

def sidebar_conversas():
    st.sidebar.header("Conversas")
    tab_conversas(st.sidebar)

#dentro de main rodamos a page de chat e o sidebar
def main():
    inicializacao()
    pagina_chat()
    sidebar_conversas()
   





#para rodar o arquivo
if __name__ == "__main__":
    main() 