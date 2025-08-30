# app/utils/llm.py
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature: float = 0.1, model: str = "gpt-3.5-turbo"):
    """Get configured LLM instance"""
    return ChatOpenAI(
        temperature=temperature,
        model=model,
        api_key=os.getenv("OPENAI_API_KEY")
    )

def create_prompt_template(template: str) -> ChatPromptTemplate:
    """Create a chat prompt template"""
    return ChatPromptTemplate.from_template(template)
