import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()
PASTA_BASE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'base_conhecimento')


def criar_db():
    documentos = carregar_documentos()
    print(documentos)
    chunks = dividir_chuncks(documentos)
    vetorizar_chuncks(chunks)

def carregar_documentos():
    carregador = PyPDFDirectoryLoader(PASTA_BASE)
    documentos = carregador.load() 
    return documentos


#recebe a lista de documentos e divide em chunks
def dividir_chuncks(documentos):

    #separa o documento em chunks
    separador_documentos = RecursiveCharacterTextSplitter(
        chunk_size=2000, # definir o tamanho do chunk
        chunk_overlap=500, #caso perca algum contexto vai pegar o contexto de antes e o de depois 
        length_function= len,
        add_start_index=True, # saber onde comeca o chunck e onde termina

)
    # separar todos os documentos caso tenha 1 ou mais pdfs
    chuncks = separador_documentos.split_documents(documentos)
    print(len(chuncks))

    return chuncks


def vetorizar_chuncks(chuncks):
    CAMINHO_BANCO_DE_DADOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'banco_de_dados')
    db = Chroma.from_documents(
        documents=chuncks,           # ✅ Primeiro: documentos
        embedding=OpenAIEmbeddings(), # ✅ Segundo: embedding function
        persist_directory=CAMINHO_BANCO_DE_DADOS  # ✅ Terceiro: caminho (RAIZ)
    )
    print('banco de dados criado')
    return db

criar_db()