# from langchain_ollama.chat_models import ChatOllama
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

# llm = ChatOllama(model="qwen3:4b", temperature=0.95)
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.95)
