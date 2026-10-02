
from dotenv import load_dotenv
import os

import gradio as gr
from huggingface_hub import InferenceClient


load_dotenv()

HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = os.getenv(
    "MARKETING_MODEL_ID",
    "Qwen/Qwen2.5-0.5B-Instruct"
)


def get_client():
    if not HUGGINGFACE_API_KEY:
        raise ValueError(
            "HUGGINGFACE_API_KEY is missing. Add it to your .env file."
        )

    return InferenceClient(
        provider="auto",
        api_key=HUGGINGFACE_API_KEY,
    )


def build_prompt(
    product_name,
    product_details,
    audience,
    platform,
    format_type,
    tone,
    language,
    call_to_action,
    length,
):
    return (
        f"Create {length.lower()} {format_type.lower()} for {platform}.\n"
        f"Product or brand: {product_name.strip()}\n"
        f"Product details: {product_details.strip()}\n"
        f"Target audience: {audience.strip() or 'General audience'}\n"
        f"Tone: {tone}\n"
        f"Language: {language}\n"
        f"Call to action: "
        f"{call_to_action.strip() or 'Choose a relevant, low-pressure call to action.'}\n\n"
        "Write polished, specific marketing copy that fits the platform "
        "and format. Use only claims supported by the supplied product "
        "details; do not invent prices, features, statistics, or guarantees. "
        "Return only the finished content, without analysis or a preamble."
    )


def generate_content(
    product_name,
    product_details,
    audience,
    platform,
    format_type,
    tone,
    language,
    call_to_action,
    length,
):
    if not product_name or not product_name.strip():
        return "Add a product or brand name to generate content."

    if not product_details or not product_details.strip():
        return "Add a few product details so the copy stays specific and accurate."

    prompt = build_prompt(
        product_name,
        product_details,
        audience,
        platform,
        format_type,
        tone,
        language,
        call_to_action,
        length,
    )

    try:
        client = get_client()

        response = client.chat_completion(
            model=MODEL_ID,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a careful, creative marketing copywriter."
                    ),
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            max_tokens=450,
            temperature=0.7,
            top_p=0.9,
        )

        return response.choices[0].message.content.strip()

    except Exception as error:
        return (
            f"Could not generate content "
            f"({type(error).__name__}: {error}). "
            "Check your Hugging Face API key, model ID, "
            "internet connection, and model availability."
        )


with gr.Blocks(
    title="AI Marketing Content Generator",
    theme=gr.themes.Soft(),
) as demo:

    gr.Markdown(
        "# AI Marketing Content Generator\n"
        "Create marketing content using the Hugging Face Inference API."
    )

    with gr.Row():

        with gr.Column(scale=1):

            product_name = gr.Textbox(
                label="Product or brand",
                placeholder="e.g. Northstar Coffee",
            )

            product_details = gr.Textbox(
                label="Product details",
                placeholder=(
                    "What it does, notable features, "
                    "and facts the copy can safely mention"
                ),
                lines=5,
            )

            audience = gr.Textbox(
                label="Target audience",
                placeholder=(
                    "e.g. Busy commuters who enjoy specialty coffee"
                ),
            )

            call_to_action = gr.Textbox(
                label="Call to action",
                placeholder="e.g. Explore the new collection",
            )

        with gr.Column(scale=1):

            platform = gr.Dropdown(
                [
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

            format_type = gr.Dropdown(
                [
                    "Social media post",
                    "Advertisement",
                    "Email",
                    "Product description",
                    "Blog outline",
                ],
                value="Social media post",
                label="Content format",
            )

            tone = gr.Dropdown(
                [
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
                [
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
                ["Short", "Medium", "Long"],
                value="Short",
                label="Length",
            )

    generate_button = gr.Button(
        "Generate content",
        variant="primary",
    )

    output = gr.Textbox(
        label="Generated content",
        lines=10,
        interactive=False,
    )

    gr.Markdown(
        "Review generated copy for accuracy and brand fit before publishing."
    )

    generate_button.click(
        fn=generate_content,
        inputs=[
            product_name,
            product_details,
            audience,
            platform,
            format_type,
            tone,
            language,
            call_to_action,
            length,
        ],
        outputs=output,
    )


if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port
    )

