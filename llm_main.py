
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from dotenv import load_dotenv
GOOGLE_API_KEYS = os.getenv("GOOGLE_API_KEY")

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.5,GOOGLE_API_KEYS=GOOGLE_API_KEYS)