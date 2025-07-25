from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

from dotenv import load_dotenv

load_dotenv()

# Set Cache
set_llm_cache(InMemoryCache())

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
