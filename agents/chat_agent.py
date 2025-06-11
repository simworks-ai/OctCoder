import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

# Load environment vars
load_dotenv()

# Load prompt template
prompt_template = PromptTemplate.from_file("prompts/chat_prompt.txt")

# Gemeni model
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Compose prompt + LLM
chat_chain = prompt_template | llm

def chat_agent(state: dict) -> dict:
    """
    state expects:
      - 'user_input': str
      - 'history': List[Dict[str,str]] (optional)
    Returns:
      - 'ack': str
      - 'forwarded': str
      - 'history': updated list
    """
    user_text = state["user_input"]
    result = chat_chain.invoke({"user_input": user_text})
    ack = result.content if hasattr(result, "content") else result
    history = state.get("history", []) + [{"user": user_text, "assistant": ack}]
    return {"ack": ack, "forwarded": user_text, "history": history}