# Week 1 — Prompting Techniques

You will practice multiple prompting techniques by crafting prompts to complete specific tasks. Each task’s instructions are at the top of its corresponding source file.

## Installation
Make sure you have first done the installation described in the top-level `README.md`. 

## ENV creation
create .env in week1 folder. add below lines
``` bash
OLLAMA_HOST=http://10.23.38.9:11434
```
or add below into launch.json
``` json
"env": {
                "OLLAMA_HOST": "http://10.23.38.9:11434"
            }
```

## Ollama installation
We will be using a tool to run different state-of-the-art LLMs locally on your machine called [Ollama](https://ollama.com/). Use one of the following methods:

- macOS (Homebrew):
  ```bash
  brew install --cask ollama 
  ollama serve
  ```

- Linux (recommended):
  ```bash
  curl -fsSL https://ollama.com/install.sh | sh
  ```

- Windows:
  Download and run the installer from [ollama.com/download](https://ollama.com/download).

Verify installation:
```bash
ollama -v
```

Before running the test scripts, make sure you have the following models pulled. You only need to do this once (unless you remove the models later):
```bash
ollama run mistral-nemo:12b
ollama run llama3.1:8b
```

non-interactive mode:
```
ollama pull llama3.1:8b
ollama pull mistral-nemo:12b

OLLAMA_HOST=0.0.0.0 ollama serve
OLLAMA_HOST=0.0.0.0 nohup ollama serve > ollama.log 2>&1 &
```

### Running with Remote Ollama
If your Ollama server is running on a remote machine (e.g., a Linux server with GPUs), follow these steps:

1. **Configure Remote Server:**
   Ensure Ollama is listening on all interfaces. By default, it only listens on `127.0.0.1`.
   - **Directly:** Set the environment variable: `export OLLAMA_HOST=0.0.0.0` before running `ollama serve`.
   - **Systemd (Linux service):**
     1. Run `sudo systemctl edit ollama.service`.
     2. Add the following lines:
        ```ini
        [Service]
        Environment="OLLAMA_HOST=0.0.0.0"
        ```
     3. Restart the service: `sudo systemctl daemon-reload && sudo systemctl restart ollama`.
   - **Firewall:** Ensure port `11434` is open on the remote machine.
   - to test connection: `curl -v http://10.23.38.9:11434/api/tags`

2. **Run Local Scripts:**
   Pass the `OLLAMA_HOST` environment variable pointing to your remote server when running your scripts:
   ```bash
   OLLAMA_HOST=http://<REMOTE_IP>:11434 uv run week1/chain_of_thought.py
   OLLAMA_HOST=http://10.23.38.9:11434 uv run week1/chain_of_thought.py
   ```
## Techniques and source files
- K-shot prompting — `week1/k_shot_prompting.py`
- Chain-of-thought — `week1/chain_of_thought.py`
- Tool calling — `week1/tool_calling.py`
- Self-consistency prompting — `week1/self_consistency_prompting.py`
- RAG (Retrieval-Augmented Generation) — `week1/rag.py`
- Reflexion — `week1/reflexion.py`

## Deliverables
- Read the task description in each file.
- Design and run prompts (look for all the places labeled `TODO` in the code). That should be the only thing you have to change (i.e. don't tinker with the model). 
- Iterate to improve results until the test script passes.
- Save your final prompt(s) and output for each technique.
- Make sure to include in your submission the completed code for each prompting technique file. ***Double check that all `TODO`s have been resolved.***

## Evaluation rubric (60 pts total)
- 10 for each completed prompt across the 6 different prompting techniques