
import os

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
MODEL_ID = os.getenv("GROQ_MODEL_ID", "llama-3.3-70b-versatile").strip()
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()


def get_client():
    api_key = (os.getenv("GROQ_API_KEY") or "").strip().strip('"').strip("'")

    if not api_key:
        raise ValueError(
            "GROQ_API_KEY is missing. Configure it in Render "
            "Environment settings or your local .env file."
        )

    return Groq(
        api_key=api_key,
        base_url=GROQ_BASE_URL,
        timeout=60.0,
        max_retries=2,
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

        response = client.chat.completions.create(
            model=MODEL_ID,
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
            f"Model: {MODEL_ID}. Connection detail: {detail}"
        )

    except APIStatusError as error:
        print(
            f"Groq API status error: HTTP {error.status_code}; "
            f"{type(error).__name__}: {error!r}"
        )
        return (
            f"Groq API error (HTTP {error.status_code}). "
            "Check the API key, model ID, and Groq account limits."
        )

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
