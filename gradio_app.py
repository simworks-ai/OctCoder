# In gradio_app.py
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
    Runs the full agentic pipeline, yielding UI updates for a responsive experience.
    """
    # 1. Immediately clear previous outputs and show placeholder visibility
    yield {
        results_group: gr.update(visible=True),
        output_text: gr.update(value="Starting simulation...", visible=True),
        output_image: gr.update(value=None, visible=False)
    }

    final_state = None
    try:
        steps = {
            "interpret": "Interpreting request...",
            "codegen": "Generating Octave script...",
            "execute": "Running simulation...",
            "summarise": "Creating summary..."
        }
        
        # Stream the graph execution
        for chunk in compiled_graph.stream({"user_input": user_input}):
            # The key of the chunk is the name of the node that just finished
            node_name = list(chunk.keys())[0]
            if node_name in steps:
                progress(list(steps.keys()).index(node_name) / len(steps), desc=steps[node_name])
            
            # The final result is the last chunk yielded from the graph
            final_state = list(chunk.values())[0]

        progress(1.0, desc="Done!")

        # Extract final results from the last state of the graph
        summary = final_state.get("response", "No summary was generated.")
        gif_path = final_state.get("gif", None)

        # Debugging: Print the gif_path
        print(f"Debug: gif_path is {gif_path}")

        # Ensure gif_path is valid and the file exists before updating Gradio component
        display_gif = False
        if gif_path and os.path.exists(gif_path):
            display_gif = True

        # 4. Yield the final results
        yield {
            output_text: gr.update(value=summary, visible=True),
            output_image: gr.update(value=gif_path if display_gif else None, visible=display_gif)
        }

    except Exception as e:
        error_message = f"**An error occurred during the simulation:**\n\n```\n{traceback.format_exc()}\n```"
        print(f"--- ERROR TRACEBACK ---\n{traceback.format_exc()}\n-----------------------")
        yield {
            output_text: gr.update(value=error_message, visible=True),
            output_image: gr.update(value=None, visible=False)
        }


# --- Create the Gradio Interface ---
with gr.Blocks(theme=gr.themes.Soft(), css="""
footer {display: none !important}
.hero-img {display: flex; justify-content: center; margin: 0 auto 24px auto;}
.hero-img img {max-width: 550px; height: auto; border-radius: 12px; box-shadow: 0 4px 24px #0001; object-fit: contain;}
.results-box {border: 2px solid #e0e0e0; border-radius: 16px; padding: 24px; margin-top: 24px; background: #fafbfc; box-shadow: 0 2px 12px #0001;}
.results-gif {display: flex; justify-content: center; align-items: center;}
.results-gif img {max-width: 400px; width: 100%; border-radius: 8px;}
""") as demo:
    gr.Markdown("# Octave Simulation Agent", elem_id="hero-title", elem_classes="hero-title")
    # Hero image directly below the title, controlled by CSS for size
    with gr.Row(elem_classes="hero-img"):
        gr.Image("public/octcoder.png", show_label=False, container=False)
    gr.Markdown("Enter a natural language request to generate and run a GNU Octave simulation. The agent will interpret your request, write the code, execute it, and provide a summary with an animated GIF if requested.")
    with gr.Row():
        input_box = gr.Textbox(
            label="Your Request",
            placeholder="e.g., Animate a 2 Hz sine wave for 3 seconds and make a GIF",
            scale=4,
            lines=2
        )
        run_button = gr.Button("Run Simulation", variant="primary", scale=1)
    # Results section in a visually distinct box
    with gr.Group(visible=False, elem_classes="results-box") as results_group:
        with gr.Row():
            with gr.Column(scale=1):
                output_text = gr.Markdown(label="Summary", elem_id="output-summary")
            with gr.Column(scale=1, elem_classes="results-gif"):
                output_image = gr.Image(type="filepath", label="Simulation Output (GIF)", interactive=False)
    run_button.click(
        fn=run_simulation,
        inputs=[input_box],
        outputs=[results_group, output_text, output_image]
    )

# --- CRUCIAL CHANGE FOR SERVING THE GIF ---
# Launch the app, allowing Gradio to serve files from the 'test_runs' directory.
if __name__ == "__main__":
    # Ensure the directory for runs exists
    os.makedirs("test_runs", exist_ok=True)
    demo.launch(allowed_paths=["test_runs", "public"])