# AI Marketing Content Generator

A Gradio web app that creates marketing drafts from product details using the Hugging Face Inference API. The model runs remotely, so the app container stays small and does not download model weights. Hugging Face usage limits or charges may apply to the selected model/provider.

## Live demo

The app is currently deployed at: https://ai-marketing-content-generator-7syh.onrender.com/

## Deploy to Render

This project is ready to deploy on Render as a web service.

1. Push the repository to GitHub.
2. In Render, create a new Web Service and connect the GitHub repo.
3. Use the following settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python app.py`
   - Environment Variables:
     - `HUGGINGFACE_API_KEY` = your Hugging Face access token
     - `MARKETING_MODEL_ID` = `Qwen/Qwen2.5-0.5B-Instruct`
     - `PORT` = `10000` (Render sets this automatically; keep the app compatible with it)
4. Deploy the service and open the generated Render URL.

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

### Fix "Write access to project was denied"

This message usually means the project has no active billing account, its billing account is suspended/closed, or your Google account cannot view or link billing. In Google Cloud Console, select the exact project ID, open **Billing**, and check **My projects**. If it is not linked, a billing administrator must link it to an active billing account with a valid payment method. Linking a billing account can incur charges.

With the Google Cloud CLI installed and authenticated, inspect the project's billing state:

```powershell
gcloud billing projects describe $PROJECT_ID
```

If `billingEnabled` is false or there is no `billingAccountName`, ask the billing account administrator to link the project. If you are that administrator and are authorized to use the account:

```powershell
$BILLING_ACCOUNT_ID = "000000-000000-000000"
gcloud billing projects link $PROJECT_ID --billing-account=$BILLING_ACCOUNT_ID
```

If linking is denied, the administrator must grant your account **Billing Account User** (`roles/billing.user`) on the billing account and **Project Billing Manager** (`roles/billing.projectManager`) on the project, or perform the link for you. If billing is already enabled and active, ask the project or organization administrator to check your project IAM permissions and organization policies. Do not paste billing IDs, payment details, or access tokens into chat.

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