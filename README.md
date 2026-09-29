# AI Marketing Content Generator

A Gradio web app that creates marketing drafts from product details using the Hugging Face Inference API. The model runs remotely, so the app container stays small and does not download model weights. Hugging Face usage limits or charges may apply to the selected model/provider.

## Run locally on Windows

1. Install Python 3.12.
2. Open PowerShell in this folder and create/activate a virtual environment:

   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Create a Hugging Face access token with permission to use Inference Providers. Add it to a local `.env` file:

   ```text
   HUGGINGFACE_API_KEY=hf_your_token_here
   MARKETING_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
   ```

5. Start the app and open the local address printed in the terminal:

   ```powershell
   python app.py
   ```

The app defaults to port 7860 locally. Do not commit `.env` or share its token.

## Deploy to Google Cloud Run

You need a Google Cloud project with billing enabled, the Google Cloud CLI installed, and a Hugging Face token. Sign in with `gcloud auth login`, then set the project and region in PowerShell:

```powershell
$PROJECT_ID = "your-project-id"
$REGION = "us-central1"
$SERVICE = "ai-marketing-content-generator"
gcloud config set project $PROJECT_ID
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com
```

Create a Secret Manager secret named `huggingface-api-key` in the Google Cloud Console and add your Hugging Face token as its value. Grant the Cloud Run runtime service account access to that secret. For the default Compute Engine service account, run:

```powershell
$PROJECT_NUMBER = gcloud projects describe $PROJECT_ID --format="value(projectNumber)"
$RUNTIME_SA = "$PROJECT_NUMBER-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding huggingface-api-key --project=$PROJECT_ID --member="serviceAccount:$RUNTIME_SA" --role="roles/secretmanager.secretAccessor"
```

If your service uses a custom runtime service account, grant access to that account instead. Deploy from the project folder:

```powershell
gcloud run deploy $SERVICE `
  --source . `
  --region $REGION `
  --allow-unauthenticated `
  --set-secrets HUGGINGFACE_API_KEY=huggingface-api-key:latest `
  --set-env-vars MARKETING_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct `
  --memory 1Gi `
  --cpu 1 `
  --min 0 `
  --max 3 `
  --timeout 300
```

The command prints the deployed service URL. `--allow-unauthenticated` makes the web UI public; remove it if the app should require Google authentication. Cloud Run injects its `PORT`, and the app binds to that port on `0.0.0.0`.

## Container build

The included Dockerfile uses the locked `uv` dependencies. If Docker is installed, build and run locally with:

```powershell
docker build -t ai-marketing-content-generator .
docker run --rm -p 8080:8080 -e HUGGINGFACE_API_KEY=your_token_here ai-marketing-content-generator
```

Open `http://localhost:8080`. For local testing, prefer setting the token in your shell rather than putting it in a committed file.

Generated copy is a draft. Verify claims and brand requirements before publishing.