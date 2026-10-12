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

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL_ID = os.getenv("GROQ_MODEL_ID", "openai/gpt-oss-20b")


def get_client():
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is missing. Add it to your .env file."
        )

    return Groq(api_key=GROQ_API_KEY)


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
        f"Call to action: "
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
        return str(error)

    except RateLimitError:
        return (
            "Groq rate limit or quota reached. Please wait, check your "
            "Groq account limits, and try again."
        )

    except APIConnectionError:
        return (
            "Could not connect to Groq. Check your internet connection "
            "and try again."
        )

    except APIStatusError as error:
        return (
            f"Groq API error (HTTP {error.status_code}). "
            "Check your model ID, API key, and Groq account access."
        )

    except Exception as error:
        return f"Unexpected error: {type(error).__name__}: {error}"


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
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
    )
