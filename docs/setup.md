# Setup

## Create A Virtual Environment With uv

Install `uv` first if you do not already have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Create and activate a virtual environment:

```bash
uv venv
source .venv/bin/activate
```

Install the Python packages:

```bash
uv pip install -r requirements.txt
```

Run the fake working demo:

```bash
python3 demo.py
```

## Ollama Setup

Install Ollama using the official instructions:

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

Pull a small local model:

```bash
ollama pull llama3.2:1b
```
