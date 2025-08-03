import chunk
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


load_dotenv()
CAMINHO_BANCO_DE_DADOS = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'banco_de_dados'))
print(f"DEBUG - CAMINHO_BANCO_DE_DADOS: {CAMINHO_BANCO_DE_DADOS}")

def pagina_chat():
    #nosso title da page do chat
    st.header("Chat com Leitura de Arquivos", divider=True) #linha abaixo do nosso titulo

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

        db = Chroma(persist_directory=CAMINHO_BANCO_DE_DADOS, embedding_function=OpenAIEmbeddings())

        # Busca similaridade
        resultados = db.similarity_search_with_relevance_scores(entrada_usuario, k=3)
        if len(resultados) == 0 or resultados[0][1] < 0.7:
            print("Não conseguiu encontrar nenhuma informação relevante na base")
            return "Desculpe, não encontrei informações relevantes sobre esse assunto na base de dados."

        textos_resultado = []
        for resultado in resultados:
            texto = resultado[0].page_content
            textos_resultado.append(texto)

        base_conhecimentos = "\n".join(textos_resultado)

        prompt_resposta_da_ia = f"""
            Você é um assistente da empresa Bluey e se chama Vitória.
            responda a pergunta do usuário: {entrada_usuario}

            com base nessas informações: {base_conhecimentos}
            """



        model = ChatOpenAI(
            openai_api_key=os.getenv('OPENAI_API_KEY'),
            model='gpt-4o-mini',
            temperature=0.5,
            max_tokens=2000
        )

        # vai receber o prompt e todas as mensagens usuário + IA para manter contexto
        resposta = model.invoke([prompt_resposta_da_ia]+mensagens)
        return resposta.content

    # caso tenha mensagem do user ele criar a respost chamando a func gerar resposta
    if mensagens:
        resposta_ia = gerar_resposta(mensagens, entrada_usuario)

        #exibe a resposta da IA
        st.chat_message('assistant').markdown(resposta_ia)

        #vai adc a resp da Ia a lista de msgs
        mensagens.append({'role': 'assistant', 'content': resposta_ia})

        #repetimos para guardar para qd user enviar mensagem de novo
        st.session_state.mensagens = mensagens


     
# sidebar por enquanto so pega o arquivo
def sidebar_pdf_e_conversas():
    st.sidebar.header("Arquivo")
    st.sidebar.file_uploader("Carregar Arquivo", type=["pdf"])




#dentro de main rodamos a page de chat e o sidebar
def main():
    pagina_chat()
    sidebar_pdf_e_conversas()





#para rodar o arquivo
if __name__ == "__main__":
    main() 
