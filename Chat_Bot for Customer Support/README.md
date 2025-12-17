# Customer Support Chatbot

Minimal customer-support chatbot using OpenAI + Streamlit + Telegram.

Quickstart

1. Create a Python venv and install requirements:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

2. Set environment variables (replace with your keys):

```
OPENAI_API_KEY=sk-...
TELEGRAM_TOKEN=...
```

3. Run the web UI (Streamlit):

```bash
streamlit run app/web_app.py
```

4. Run the Telegram bot (optional):

```bash
python app/telegram_bot.py
```

Notes

- The chatbot uses OpenAI (if provided) for smart responses and an FAQ fallback.
- If no OpenAI key is provided, the bot will use a TF-IDF based FAQ search and simple rules.
- If the bot cannot answer, users can create a support ticket from the web UI or via `/ticket` on Telegram; tickets are stored in CSV by default.

Kaggle dataset ingestion

- Use the Kaggle CLI to download datasets and generate FAQs from conversation data.
- Example:

```bash
# ensure kaggle credentials at ~/.kaggle/kaggle.json or set KAGGLE_USERNAME/KAGGLE_KEY
pip install -r requirements.txt
python scripts/download_kaggle.py owner/dataset-name --file "*.csv" --out data/raw
# this will call scripts/extract_faqs.py on each CSV and write to data/derived_faqs.csv
```
