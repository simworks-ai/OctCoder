import os
import argparse
import traceback
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict

# Import your agent functions
from agents.chat_agent import chat_agent
from agents.interpreter import interpret_spec
from agents.codegen import codegen_agent
from agents.executor import executor_agent
from agents.summariser import summariser_agent

# Load environment variables (GOOGLE_API_KEY, etc.)
load_dotenv()

# Define the state for the graph
class SimulationState(TypedDict, total=False):
    user_input: str
    ack: str
    forwarded: str
    history: list
    spec: dict
    script: str
    stdout: str
    stderr: str
    frames: list
    gif: str
    response: str

# --- Build and Compile the LangGraph Pipeline ---
graph = StateGraph(SimulationState)
graph.add_node("chat", chat_agent)
graph.add_node("interpret", interpret_spec)
graph.add_node("codegen", codegen_agent)
graph.add_node("execute", executor_agent)
graph.add_node("summarise", summariser_agent)

graph.add_edge(START, "chat")
graph.add_edge("chat", "interpret")
graph.add_edge("interpret", "codegen")
graph.add_edge("codegen", "execute")
graph.add_edge("execute", "summarise")
graph.add_edge("summarise", END)

compiled_graph = graph.compile()

def run_cli_simulation(user_input: str) -> dict:
    """
    Runs the full agentic pipeline for CLI, returning the final state.
    """
    print(f"Starting simulation for: \"{user_input}\"")
    print("-" * 30)

    final_state = None
    try:
        # Stream the graph execution to show intermediate steps
        for i, chunk in enumerate(compiled_graph.stream({"user_input": user_input})):
            node_name = list(chunk.keys())[0]
            print(f"Step {i+1}: {node_name} completed.")
            final_state = list(chunk.values())[0]
            
        print("-" * 30)
        print("Simulation complete!")

    except Exception as e:
        error_message = f"An error occurred during the simulation:\n\n```\n{traceback.format_exc()}\n```"
        print(f"--- ERROR TRACEBACK ---\n{traceback.format_exc()}\n-----------------------")
        return {"response": error_message, "gif": None}
    
    return final_state


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run an Octave simulation agent from the command line.")
    parser.add_argument("query", type=str, help="The natural language request for the Octave simulation.")
    
    args = parser.parse_args()

    # Ensure the directory for runs exists
    os.makedirs("test_runs", exist_ok=True)

    final_results = run_cli_simulation(args.query)

    print("\n--- Final Results ---")
    response_summary = final_results.get("response", "No summary generated.")
    gif_output_path = final_results.get("gif", None)

    print(f"Summary:\n{response_summary}")
    
    if gif_output_path and os.path.exists(gif_output_path):
        print(f"GIF Generated: {gif_output_path}")
    elif gif_output_path:
        print(f"GIF Path was set to {gif_output_path}, but the file does not exist.")
    else:
        print("No GIF was generated.")

    print("---------------------") 