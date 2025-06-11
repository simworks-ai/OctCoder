import os
import json
from typing import Any, Dict, List
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
import base64

# Load environment variables (GOOGLE_API_KEY, etc.)
load_dotenv()

# Load the external prompt for summarization
prompt_template = PromptTemplate.from_file("prompts/summariser_prompt.txt")

# Initialize the Gemini LLM for summarization
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

# Compose the prompt template and LLM into a runnable chain
summariser_chain = prompt_template | llm

def summariser_agent(state: dict) -> dict:
    """
    Summariser Agent: generates a human-readable summary of the simulation results.
    Expects in state:
      - 'spec': dict with simulation parameters
      - 'stdout': str from Octave execution
      - 'stderr': str from Octave execution
      - 'frames': list of file paths to PNG frames
      - 'gif': file path to the output GIF (or None)
    Returns:
      - 'response': a string containing markdown-formatted summary
    """
    spec = state.get("spec", {})
    stdout = state.get("stdout", "")
    stderr = state.get("stderr", "")
    frames = state.get("frames", [])
    gif_path_from_executor = state.get("gif") # Renamed for clarity

    # Include the user's original request for context
    history = state.get("history", [])
    user_query = history[-1]["user"] if history else ""

    # Calculate boolean for gif production and integer for frames generated
    gif_produced = bool(gif_path_from_executor and os.path.exists(gif_path_from_executor))
    frames_generated = len(frames)

    # Build context for the prompt
    context = {
        "spec": spec,
        "user_query": user_query,
        "stdout": stdout,
        "stderr": stderr,
        "frames_generated": frames_generated, # Pass as integer
        "gif_produced": gif_produced # Pass as boolean
    }
    context_str = json.dumps(context)

    # Invoke the summarization chain
    result = summariser_chain.invoke({"context": context_str})
    response = result.content if hasattr(result, "content") else result

    # # If a GIF was produced, embed it as a base64 data URI in the response
    # if gif:
    #     with open(gif, "rb") as f:
    #         b64 = base64.b64encode(f.read()).decode("ascii")
    #     image_md = f"![](data:image/gif;base64,{b64})"
    #     response = response + "\n\n" + image_md

    return {"response": response, "gif": gif_path_from_executor}