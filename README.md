<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://ai.google.dev/static/site-assets/images/share-ais-513315318.png" />
</div>

# Run and deploy your AI Studio app

This contains everything you need to run your app locally.

View your app in AI Studio: https://ai.studio/apps/ced92dbd-addc-457f-9aba-046e85f6027a

## Run Locally

**Prerequisites:** Python 3.11 or Python 3.14 on Windows

1. Install dependencies:
   `python -m pip install --upgrade pip`
   `python -m pip install -r requirements.txt`
2. Create a `.env` file and add any API keys you want to use, for example:
   ```
   GEMINI_API_KEY=your_gemini_key
   GROQ_API_KEY=your_groq_key
   GITHUB_TOKEN=your_github_token
   OPENROUTER_API_KEY=your_openrouter_key
   MISTRAL_API_KEY=your_mistral_key
   ```
3. Run the app:
   `python main.py`

> If you do not set API keys, the UI can still start locally, but AI OCR calls will fail until valid keys are provided.
