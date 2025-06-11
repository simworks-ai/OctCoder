
## How It Works: The Agentic Pipeline

OctCoder utilizes a sophisticated agentic pipeline built with LangGraph to process user requests:

1.  **Chat Agent (`chat_agent.py`):**
    *   **Role:** The entry point for user interaction. It receives the initial natural language request.
    *   **Functionality:** Engages in a preliminary conversation, acknowledges the user's input, and forwards the cleaned-up request for interpretation.

2.  **Interpreter Agent (`interpreter.py`):**
    *   **Role:** Translates the user's natural language request into a structured, machine-readable simulation specification.
    *   **Functionality:** Uses an LLM to parse the request and generate a JSON object (`SimulationSpec`) detailing the simulation's task, desired outputs (e.g., GIF), and parameters.

3.  **Code Generation Agent (`codegen.py`):**
    *   **Role:** Creates the executable GNU Octave `.m` script based on the interpreted simulation specification.
    *   **Functionality:** Takes the JSON `spec` from the interpreter and generates a complete Octave script that performs the requested simulation.

4.  **Executor Agent (`executor.py`):**
    *   **Role:** Runs the generated GNU Octave script and captures all relevant outputs.
    *   **Functionality:** Executes the `.m` script in a dedicated environment, collects standard output, standard error, generated plot frames (if any), and optionally creates an animated GIF from the frames.

5.  **Summariser Agent (`summariser.py`):**
    *   **Role:** Provides a comprehensive and human-readable summary of the simulation results.
    *   **Functionality:** Analyzes the simulation specification, Octave's outputs, and any generated artifacts (like GIFs) to generate a detailed markdown response for the user.

This sequence of agents forms a robust chain, ensuring that each step of the simulation creation and execution process is handled intelligently and efficiently.

## Gradio App

The Gradio application provides an intuitive web interface to interact with the OctCoder agents.

### Running Locally

To run the Gradio app on your local machine:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-organization/OctCoder.git
    cd OctCoder
    ```
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up environment variables:**
    Create a `.env` file in the root directory and add your `GOOGLE_API_KEY`:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```
    You can obtain a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
4.  **Launch the Gradio app:**
    ```bash
    python gradio_app.py
    ```
    The application will typically be accessible at `http://127.0.0.1:7860` or similar.

### Deployment on Vercel

OctCoder is configured for seamless deployment on Vercel. The `vercel.json` file in the root directory handles the build and routing configurations.

1.  **Ensure `vercel.json` is present:**
    ```json
    {
      "builds": [
        {
          "src": "gradio_app.py",
          "use": "@vercel/python"
        }
      ],
      "routes": [
        {
          "src": "/(.*)",
          "dest": "gradio_app.py"
        }
      ]
    }
    ```
2.  **Connect your Git repository to Vercel.**
3.  **Add `GOOGLE_API_KEY` as an environment variable in Vercel:**
    Go to your project settings on Vercel, navigate to "Environment Variables," and add `GOOGLE_API_KEY` with your Gemini API key.
4.  **Deploy:** Vercel will automatically detect the configuration and deploy your Gradio application.

## Installation

### Prerequisites

*   Python 3.8+
*   pip
*   GNU Octave (must be installed and accessible in your system's PATH for the executor agent to function correctly)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-organization/OctCoder.git
    cd OctCoder
    ```
2.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Set up Google API Key:**
    Obtain a `GOOGLE_API_KEY` from [Google AI Studio](https://aistudio.google.com/app/apikey) and set it as an environment variable. You can do this by creating a `.env` file in the root of your project:
    ```
    GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"
    ```

## Usage

### Via Gradio Web Interface

Once the Gradio app is running (either locally or deployed on Vercel), simply open the URL in your browser. Enter your simulation request in the provided text box and click "Run Simulation." The results, including a summary and an animated GIF (if requested), will be displayed.

### Via Command Line (main.py)

You can also run the agentic pipeline directly from the command line:

```bash
python main.py "Animate a 2 Hz sine wave for 3 seconds and make a GIF"
```
