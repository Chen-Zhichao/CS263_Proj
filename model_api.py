import json
import os
import re
from typing import Any

from dotenv import load_dotenv
from openai import OpenAI, RateLimitError


load_dotenv()

OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
HF_MODEL = os.getenv("HF_MODEL", "meta-llama/Llama-3.1-8B-Instruct:cerebras")
HF_BASE_URL = os.getenv("HF_BASE_URL", "https://router.huggingface.co/v1")

SYSTEM_PROMPT = """
You are evaluating social acceptability across cultural contexts.
Return JSON only with these fields:
- label: one of "acceptable", "unacceptable", or "depends"
- explanation: a concise reason for the label
"""


def build_user_prompt(interaction: str, culture_context: str | None = None) -> str:
    prompt = f"Interaction:\n{interaction.strip()}\n"

    if culture_context:
        prompt += f"\nCultural context / policy:\n{culture_context.strip()}\n"
    else:
        prompt += "\nCultural context / policy:\nNone provided. Use general pretrained knowledge.\n"

    return prompt


def _parse_json_object(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "label": "parse_error",
            "explanation": cleaned,
        }


def call_gpt41_mini(interaction: str, culture_context: str | None = None) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing from .env")

    client = OpenAI(api_key=api_key)
    try:
        response = client.responses.create(
            model=OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            input=build_user_prompt(interaction, culture_context),
            temperature=0,
            max_output_tokens=200,
        )
    except RateLimitError as exc:
        if "insufficient_quota" in str(exc):
            raise RuntimeError(
                "OpenAI API quota is unavailable for this account/project. "
                "ChatGPT Pro does not include API credits. Add API billing or "
                "credits at https://platform.openai.com/account/billing/overview, "
                "then retry after a few minutes."
            ) from exc
        raise

    return _parse_json_object(response.output_text)


def call_llama31_8b(interaction: str, culture_context: str | None = None) -> dict[str, Any]:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is missing from .env")

    client = OpenAI(base_url=HF_BASE_URL, api_key=token)
    response = client.chat.completions.create(
        model=HF_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(interaction, culture_context)},
        ],
        temperature=0,
        max_tokens=200,
    )
    return _parse_json_object(response.choices[0].message.content or "")


def predict(
    model_name: str,
    interaction: str,
    culture_context: str | None = None,
) -> dict[str, Any]:
    if model_name == "openai":
        result = call_gpt41_mini(interaction, culture_context)
    elif model_name == "llama":
        result = call_llama31_8b(interaction, culture_context)
    else:
        raise ValueError("model_name must be 'openai' or 'llama'")

    return {
        "model": model_name,
        "interaction": interaction,
        "culture_context": culture_context,
        "prediction": result,
    }
