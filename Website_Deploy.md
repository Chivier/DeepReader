# Website Deploy

## Deploy with streamlit

### Install streamlit

```bash
pip install -r requirements.txt
```

### Run streamlit app

environment variables(Store in `.env` file):
```text
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=...
DEEPREADER_MODEL_NAME=...
CARD_MODEL_NAME=...
```
Example:
```text
OPENAI_API_KEY=sk-...
OPENAI_BASE_URL=https://router.ss.chat/v1
DEEPREADER_MODEL_NAME=deepseek-v3
CARD_MODEL_NAME=deepseek-v3
```

```bash
python -m streamlit run website/Home.py
```