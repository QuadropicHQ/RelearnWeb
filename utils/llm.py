"""
Quadropic OSS
https://oss.quadropic.com
Author: Mohamed Kamran
Date: Feb 18th 2025

This file contains the implementation of the LLM model using langchain-openai.
"""

from langchain.chat_models import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REQUIRED_ENV_VARS = {
    "LLM_ENDPOINT": "LLM endpoint URL",
    "LLM_API_KEY": "LLM API key",
    "LLM_MODEL_ID": "LLM model identifier"
}

def validate_environment():
    missing_vars = [var for var, description in REQUIRED_ENV_VARS.items() 
                   if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing required environment variables: {', '.join(missing_vars)}")

def generate_llm_response(system_prompt: str, user_prompt: str, 
                         streaming: bool = True, verbose: bool = False) -> str:
    validate_environment()
    
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt),
    ]
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL_ID"),
        base_url=os.getenv("LLM_ENDPOINT"),
        api_key=os.getenv("LLM_API_KEY"),
        streaming=streaming,
        verbose=verbose
    ) | StrOutputParser()
    
    return llm.invoke(messages)

if __name__ == "__main__":
    response = generate_llm_response(
        system_prompt="You're a helpful AI",
        user_prompt="Hello, how are you?",
        verbose=True
    )
    print(response)