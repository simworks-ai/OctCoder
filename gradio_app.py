import os
import traceback
from dotenv import load_dotenv
import gradio as gr
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
# This part of your code was already correct.
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


def run_simulation(user_input: str, progress=gr.Progress(track_tqdm=True)):
    """
    Runs the full agentic pipeline on the user's request as a generator,
    yielding updates to the Gradio UI for a better user experience.
    """
    # 1. Immediately clear previous outputs and show the progress bar
    yield {
        output_text: gr.update(value="", visible=False),
        output_image: gr.update(value=None, visible=False)
    }

    try:
        # Define the sequence of steps for progress tracking
        steps = ["Interpreting...", "Generating Code...", "Executing Simulation...", "Summarizing..."]
        
        # Use a generator to stream intermediate results and update progress
        # Note: LangGraph's .stream() method is perfect for this.
        # Each agent's output is yielded as it completes.
        
        result = None
        for i, chunk in enumerate(compiled_graph.stream({"user_input": user_input})):
            # Update progress bar for each step in the graph
            if i < len(steps):
                progress(i / len(steps), desc=steps[i])
            
            # The final result is the last chunk yielded
            result = chunk

        progress(1.0, desc="Done!")

        # Extract final results from the last state of the graph
        final_state = list(result.values())[0]
        summary = final_state.get("response", "No summary was generated.")
        gif_path = final_state.get("gif", None)

        # 4. Yield the final results, making the components visible
        yield {
            output_text: gr.update(value=summary, visible=True),
            output_image: gr.update(value=gif_path, visible=bool(gif_path))
        }

    except Exception as e:
        # 5. In case of any error, format it and display it to the user
        error_message = f"**An error occurred:**\n\n```\n{str(e)}\n```"
        print("--- ERROR TRACEBACK ---")
        traceback.print_exc()
        print("-----------------------")
        yield {
            output_text: gr.update(value=error_message, visible=True),
            output_image: gr.update(value=None, visible=False)
        }


# --- Create the Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft(), css="footer {display: none !important}") as demo:
    gr.Markdown("<h1>Octave Simulation Agent</h1>")
    gr.Markdown("Enter a natural language request to generate and run a GNU Octave simulation. The agent will interpret your request, write the code, execute it, and provide a summary with an animated GIF if requested.")
    
    with gr.Row():
        input_box = gr.Textbox(
            label="Your Request",
            placeholder="e.g., Animate a 2 Hz sine wave for 3 seconds and make a GIF",
            scale=4
        )
        run_button = gr.Button("Run Simulation", variant="primary", scale=1)

    # Output components are hidden initially
    output_text = gr.Markdown(visible=False)
    output_image = gr.Image(type="filepath", label="Simulation Output (GIF)", visible=False)

    # Link the button to the function
    run_button.click(
        fn=run_simulation,
        inputs=[input_box],
        outputs=[output_text, output_image]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()