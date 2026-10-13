
import os
from urllib.parse import urlparse

import gradio as gr
from dotenv import load_dotenv
from groq import (
    Groq,
    APIConnectionError,
    APIStatusError,
    RateLimitError,
)

load_dotenv()

GROQ_API_KEY = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")
MODEL_ID = (os.getenv("GROQ_MODEL_ID") or "").strip().strip('"').strip("'")
GROQ_BASE_URL = (os.getenv("GROQ_BASE_URL") or "https://api.groq.com/openai/v1").strip()

# Keep a preference order, but do not assume that one model ID will remain
# available forever.  The client resolves the first model that Groq currently
# exposes for the account.
PREFERRED_MODELS = (
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-20b",
)


def normalize_base_url(value):
    """Return the OpenAI-compatible API root expected by the Groq SDK."""
    value = value.rstrip("/")
    if not value:
        return "https://api.groq.com/openai/v1"

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(
            "GROQ_BASE_URL must be a full URL such as "
            "https://api.groq.com/openai/v1."
        )

    for suffix in ("/chat/completions", "/models"):
        if value.endswith(suffix):
            value = value[: -len(suffix)]
    return value.rstrip("/")


def get_client():
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")

    if not api_key or api_key.lower() in {
        "your_real_groq_key",
        "your_actual_groq_api_key",
        "your_groq_api_key",
    }:
        raise ValueError(
            "GROQ_API_KEY is missing or still a placeholder. Create a key at "
            "https://console.groq.com/keys and set it in .env or Render "
            "Environment settings. Do not include quotes or spaces."
        )

    return Groq(
        api_key=api_key,
        base_url=normalize_base_url(GROQ_BASE_URL),
        timeout=60.0,
        max_retries=2,
    )


def resolve_model(client):
    """Return a model currently available to this Groq account.

    GROQ_MODEL_ID remains supported as an explicit override.  When it is not
    set, models are discovered through Groq's models endpoint so a retired or
    account-incompatible default cannot cause a permanent HTTP 404.
    """
    available = client.models.list().data
    available_ids = {model.id for model in available}

    if MODEL_ID:
        if MODEL_ID not in available_ids:
            sample = ", ".join(sorted(available_ids)[:8])
            raise ValueError(
                f"GROQ_MODEL_ID '{MODEL_ID}' is not available for this Groq key. "
                f"Available models include: {sample or 'none'}. "
                "Remove GROQ_MODEL_ID to enable automatic selection."
            )
        return MODEL_ID

    for preferred in PREFERRED_MODELS:
        if preferred in available_ids:
            return preferred

    # Last resort: choose a non-speech, non-embedding model exposed by the API.
    candidates = sorted(
        model_id
        for model_id in available_ids
        if not any(word in model_id.lower() for word in ("whisper", "guard", "embed"))
    )
    if candidates:
        return candidates[0]

    raise ValueError(
        "Groq returned no usable chat models for this API key. "
        "Check the key's project permissions and account limits."
    )


def build_prompt(
    product_name,
    product_details,
    platform,
    content_format,
    audience,
    tone,
    language,
    length,
    call_to_action,
):
    length_guide = {
        "Short": "Write around 50-80 words.",
        "Medium": "Write around 100-150 words.",
        "Long": "Write around 200-300 words.",
    }

    return (
        "You are an expert marketing content writer.\n"
        "Create useful, engaging marketing content based on the "
        "information provided.\n"
        "Do not invent product features, statistics, testimonials, "
        "or unsupported claims.\n"
        "Follow the requested language, platform, format, tone, "
        "and length.\n"
        "Return only the finished marketing content.\n\n"
        f"Product or service: {product_name.strip()}\n"
        f"Product details: {product_details.strip() or 'Not provided'}\n"
        f"Platform: {platform}\n"
        f"Content format: {content_format}\n"
        f"Target audience: {audience.strip() or 'General audience'}\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n"
        f"Length: {length_guide.get(length, length_guide['Medium'])}\n"
        "Call to action: "
        f"{call_to_action.strip() or 'Choose a relevant, low-pressure call to action.'}\n\n"
        "Make the content clear, natural, and ready to use."
    )


def generate_content(
    product_name,
    product_details,
    platform,
    content_format,
    audience,
    tone,
    language,
    length,
    call_to_action,
):
    if not product_name or not product_name.strip():
        return "Please enter a product or service name."

    try:
        client = get_client()

        prompt = build_prompt(
            product_name,
            product_details or "",
            platform,
            content_format,
            audience or "",
            tone,
            language,
            length,
            call_to_action or "",
        )

        model_id = resolve_model(client)
        print(f"Using Groq model: {model_id}")
        response = client.chat.completions.create(
            model=model_id,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a professional marketing copywriter. "
                        "Write accurate, audience-focused content."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=700,
            temperature=0.7,
            top_p=0.9,
        )

        content = response.choices[0].message.content

        if not content:
            return "The model returned an empty response. Please try again."

        return content.strip()

    except ValueError as error:
        print(f"Configuration error: {error}")
        return str(error)

    except RateLimitError as error:
        print(f"Groq rate limit error: {error!r}")
        return (
            "Groq rate limit or quota reached. Please check your "
            "Groq account limits and try again later."
        )

    except APIConnectionError as error:
        # Log technical details for Render troubleshooting.
        # Do not print the API key.
        print(
            f"Groq connection error: {type(error).__name__}: {error!r}"
        )
        cause = getattr(error, "__cause__", None)
        if cause:
            print(
                f"Underlying connection cause: "
                f"{type(cause).__name__}: {cause!r}"
            )

        detail = str(error).splitlines()[0][:180] or type(error).__name__
        return (
            "Could not connect to Groq. "
            f"Connection detail: {detail}"
        )

    except APIStatusError as error:
        print(
            f"Groq API status error: HTTP {error.status_code}; "
            f"{type(error).__name__}: {error!r}"
        )
        response = getattr(error, "response", None)
        response_detail = ""
        if response is not None:
            try:
                payload = response.json()
                response_detail = str(payload.get("error", payload))[:300]
            except Exception:
                response_detail = (getattr(response, "text", "") or "")[:300]

        if error.status_code == 401:
            message = "GROQ_API_KEY is invalid or expired. Create a new key and update .env/Render."
        elif error.status_code == 404:
            message = (
                "Groq returned 404. The configured endpoint or model is not available. "
                "Remove GROQ_MODEL_ID and leave GROQ_BASE_URL as "
                "https://api.groq.com/openai/v1 so the app can discover a valid model."
            )
        elif error.status_code == 429:
            message = "Groq rate limit or quota reached. Check your Groq account limits."
        else:
            message = f"Groq returned HTTP {error.status_code}."

        if response_detail:
            message += f" Details: {response_detail}"
        return message

    except Exception as error:
        print(
            f"Unexpected generation error: "
            f"{type(error).__name__}: {error!r}"
        )
        return f"Unexpected error: {type(error).__name__}. Check Render logs."


with gr.Blocks(title="AI Marketing Content Generator") as demo:
    gr.Markdown("# AI Marketing Content Generator")
    gr.Markdown(
        "Generate marketing content for different platforms "
        "using Python, Gradio, and the Groq API."
    )

    with gr.Row():
        with gr.Column():
            product_name = gr.Textbox(
                label="Product or Service Name",
                placeholder="Example: Organic skincare products",
            )

            product_details = gr.Textbox(
                label="Product Details",
                placeholder="Describe the product, benefits, and features",
                lines=3,
            )

            audience = gr.Textbox(
                label="Target Audience",
                placeholder="Example: Young adults interested in skincare",
            )

            call_to_action = gr.Textbox(
                label="Call to Action",
                placeholder="Example: Shop now",
            )

            platform = gr.Dropdown(
                choices=[
                    "Instagram",
                    "LinkedIn",
                    "Facebook",
                    "X",
                    "Email",
                    "Website",
                ],
                value="Instagram",
                label="Platform",
            )

            content_format = gr.Dropdown(
                choices=[
                    "Social media post",
                    "Advertisement",
                    "Email",
                    "Product description",
                    "Blog outline",
                ],
                value="Social media post",
                label="Content Format",
            )

            tone = gr.Dropdown(
                choices=[
                    "Friendly",
                    "Professional",
                    "Playful",
                    "Confident",
                    "Minimal",
                    "Warm",
                ],
                value="Friendly",
                label="Tone",
            )

            language = gr.Dropdown(
                choices=[
                    "English",
                    "Spanish",
                    "French",
                    "Hindi",
                    "Tamil",
                ],
                value="English",
                label="Language",
            )

            length = gr.Radio(
                choices=["Short", "Medium", "Long"],
                value="Medium",
                label="Content Length",
            )

            generate_button = gr.Button(
                "Generate Content",
                variant="primary",
            )

        with gr.Column():
            output = gr.Textbox(
                label="Generated Marketing Content",
                lines=18,
                show_copy_button=True,
                placeholder="Your generated content will appear here.",
            )

    generate_button.click(
        fn=generate_content,
        inputs=[
            product_name,
            product_details,
            platform,
            content_format,
            audience,
            tone,
            language,
            length,
            call_to_action,
        ],
        outputs=output,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7860))

    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
    )
