from langchain_ollama.embeddings import OllamaEmbeddings
from dotenv import load_dotenv

import os

load_dotenv()

embeddings = OllamaEmbeddings(model=os.getenv("OLLAMA_EMBEDDING_MODEL"))
