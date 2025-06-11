import os
import json
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_google_genai.chat_models import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field, ValidationError
from typing import Any, Dict

# Load environment variables
load_dotenv()

class SimulationSpec(BaseModel):
    task: str = Field(..., description="Simulation type discriminator, e.g., 'plot_signal' or 'run_simulation'")
    want_gif: bool = Field(default=False, description="Whether to produce a GIF output")
    params: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the simulation")

# Initialize the Gemini-based LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
prompt_template = PromptTemplate.from_file("prompts/interpreter_prompt.txt")
interpreter_chain = prompt_template | llm

def interpret_spec(state: dict) -> dict:
    """
    Convert free-form user input in state into a dict with key 'spec'
    containing a validated SimulationSpec.
    """
    # Extract raw user input from state
    raw = state.get("forwarded", state.get("user_input", ""))
    # Clean up Markdown code fences if present
    raw_clean = raw.strip()
    if raw_clean.startswith("```"):
        lines = raw_clean.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_clean = "\n".join(lines)
    # Invoke the LLM chain
    result = interpreter_chain.invoke({"user_input": raw_clean})
    raw = result.content if hasattr(result, "content") else result
    # Strip ```json ... ``` or ``` ... ``` fences from LLM output if present
    raw_output = raw.strip()
    if raw_output.startswith("```"):
        lines = raw_output.splitlines()
        # Remove the opening fence
        if lines[0].startswith("```"):
            lines = lines[1:]
        # Remove closing fence if present
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        raw_output = "\n".join(lines)
    else:
        raw_output = raw_output
    try:
        spec_dict = json.loads(raw_output)
        spec = SimulationSpec(**spec_dict)
        return {"spec": spec.dict()}
    except (json.JSONDecodeError, ValidationError) as e:
        raise ValueError(f"Failed to parse simulation spec: {e}\nLLM output:\n{raw}")

if __name__ == "__main__":
    import sys
    user_text = " ".join(sys.argv[1:]) or input("Describe your simulation: ")
    result = interpret_spec({"forwarded": user_text})
    spec = result.get("spec")
    print(json.dumps(spec, indent=2))
