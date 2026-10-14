# AI Marketing Content Generator

Generate ready-to-use marketing copy with Gradio and the Groq API.

## Live demo

[Open the deployed app](https://ai-marketing-content-generator-7syh.onrender.com/)

> The Render free service may sleep after inactivity. The first request can take a minute while the service wakes up.

## Run locally

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env` and set a valid Groq key:

   ```env
   GROQ_API_KEY=your_groq_api_key
   GROQ_MODEL_ID=
   GROQ_BASE_URL=https://api.groq.com/openai/v1
   ```

4. Start the app:

   ```bash
   python app.py
   ```

Open `http://localhost:7860`.

## Render deployment

1. Push the latest changes to the GitHub repository connected to Render.
2. In Render, open the Web Service and choose **Manual Deploy > Deploy latest commit** (or enable automatic deploys).
3. In **Environment**, add `GROQ_API_KEY` with the key from the Groq Console. Do not commit the key to Git.
4. Leave `GROQ_MODEL_ID` blank so the app discovers a model available to your Groq key, and set `GROQ_BASE_URL` to `https://api.groq.com/openai/v1`.
5. Confirm the service uses the repository `Dockerfile`, or use:

   - Build command: `pip install -r requirements.txt`
   - Start command: `python app.py`

6. Save the environment variables and redeploy. Check **Logs** for startup or Groq API errors.
7. Open the live URL, wait for Render to wake the service, enter a product name, and click **Generate Content**.

## Troubleshooting

- `GROQ_API_KEY is missing`: add the variable in Render Environment settings and redeploy.
- `Groq API error (HTTP 401)`: the key is invalid, expired, or includes an accidental extra value.
- `Groq API error (HTTP 400)`: verify `GROQ_MODEL_ID` is an active model ID.
- Connection error after a cold start: refresh once after Render reports that the service is live, then inspect the Render runtime logs.
- Never paste the API key into source code, README files, or screenshots.

## Project files

- `app.py` — Gradio UI and Groq request handling.
- `requirements.txt` — Python dependencies.
- `Dockerfile` — container setup for deployment.
- `.env.example` — local environment variable template.
