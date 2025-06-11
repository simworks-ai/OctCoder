

from langgraph.graph import StateGraph, START, END
from typing_extensions import TypedDict
from agents.chat_agent import chat_agent
from agents.interpreter import interpret_spec
from agents.codegen import codegen_agent
from agents.executor import executor_agent
from agents.summariser import summariser_agent

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

def main():
    # Initialize the graph with the state schema
    graph = StateGraph(SimulationState)

    # Register agent nodes
    graph.add_node("chat", chat_agent)
    graph.add_node("interpret", interpret_spec)
    graph.add_node("codegen", codegen_agent)
    graph.add_node("execute", executor_agent)
    graph.add_node("summarise", summariser_agent)

    # Define execution order
    graph.add_edge(START, "chat")
    graph.add_edge("chat", "interpret")
    graph.add_edge("interpret", "codegen")
    graph.add_edge("codegen", "execute")
    graph.add_edge("execute", "summarise")
    graph.add_edge("summarise", END)

    # Command-line interface
    import sys
    if len(sys.argv) > 1:
        user_input = " ".join(sys.argv[1:])
    else:
        user_input = input("Enter your simulation request: ")

    # Run the graph
    result = graph.run({"user_input": user_input})

    # Output the final summary
    summary = result.get("response", "")
    print(summary)

if __name__ == "__main__":
    main()