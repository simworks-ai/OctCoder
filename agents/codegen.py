import os
import json
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI

# Load environment variables (GOOGLE_API_KEY, etc.)
load_dotenv()

# Load the external prompt for code generation
prompt_template = PromptTemplate.from_file("prompts/codegen_prompt.txt")

# Initialize the Gemini LLM for code generation
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash") # Using Pro for better coding ability

# Compose the prompt template and LLM into a runnable chain
codegen_chain = prompt_template | llm

def codegen_agent(state: dict) -> dict:
    """
    Code-Generator Agent: generates a GNU Octave .m script based on the JSON spec.
    Expects in state:
      - 'spec': a dict with keys 'task', 'want_gif', and 'params'
    Returns:
      - 'script': a string containing the complete .m file content
    """
    spec = state.get("spec")
    if spec is None:
        raise ValueError("No 'spec' found in state for code generation")
    
    # Serialize the specification to JSON for the prompt
    spec_json = json.dumps(spec)
    
    # Invoke the chain to generate the script
    result = codegen_chain.invoke({"spec": spec_json})
    llm_output = result.content if hasattr(result, "content") else result
    
    # Strip ```octave ... ``` or ``` ... ``` fences from LLM output
    script = llm_output.strip()
    if script.startswith("```"):
        # Find the first newline and take everything after it
        script = script.split('\n', 1)[-1]
        # Find the last ``` and take everything before it
        script = script.rsplit('```', 1)[0]
        script = script.strip()

    return {"script": script}