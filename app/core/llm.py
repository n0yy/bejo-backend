from langchain_ollama.chat_models import ChatOllama
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

import os
from dotenv import load_dotenv

load_dotenv()

# Set Cache
set_llm_cache(InMemoryCache())

llm = ChatOllama(model=os.getenv("OLLAMA_LLM_MODEL"), cache=True, reasoning=False)
