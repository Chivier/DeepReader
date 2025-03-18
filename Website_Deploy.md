# Website Deploy

## Deploy with streamlit

### Install streamlit

```bash
pip install streamlit
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
source .env && streamlit run website/chatbot.py
```