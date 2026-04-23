import base64
import re
import os
from google import genai
from google.genai import types as genai_types
from prompt import JSON_SCHEMA_PROMPT, CSV_GENERATOR_PROMPT
import json

DATA_URL_PATTERN = re.compile(r"^data:(?P<mime>[^;]+);base64,(?P<data>.+)$", re.IGNORECASE | re.DOTALL)


def _guess_mime_type(image_bytes: bytes) -> str:
    if image_bytes.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if image_bytes.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if image_bytes.startswith(b"GIF87a") or image_bytes.startswith(b"GIF89a"):
        return "image/gif"
    if image_bytes.startswith(b"RIFF") and image_bytes[8:12] == b"WEBP":
        return "image/webp"
    return "image/jpeg"


def _normalize_image_input(image_input: bytes | str) -> tuple[bytes, str]:
    """Normalize bytes/base64/data-url input into raw bytes and mime type."""
    if isinstance(image_input, bytes):
        image_bytes = image_input
        return image_bytes, _guess_mime_type(image_bytes)

    candidate = image_input.strip()

    # data:image/png;base64,...
    data_url_match = DATA_URL_PATTERN.match(candidate)
    if data_url_match:
        mime_type = data_url_match.group("mime")
        encoded = data_url_match.group("data")
        return base64.b64decode(encoded), mime_type

    # Plain base64 string
    image_bytes = base64.b64decode(candidate)
    return image_bytes, _guess_mime_type(image_bytes)

def generate_json_schema(image_input: bytes | str) -> dict:
    image_bytes, mime_type = _normalize_image_input(image_input)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        config=genai_types.GenerateContentConfig(
            system_instruction=JSON_SCHEMA_PROMPT,
        ),
        contents=[
            genai_types.Part.from_text(
                text="Analyze this table image and return ONLY the JSON object.",
            ),
            genai_types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
        ],
    )
    
    text_response = (response.text or "").strip()
    if text_response.startswith("```"):
        text_response = text_response.strip("`").removeprefix("json").strip()
        
    return json.loads(text_response)


def generate_csv_sample(image_input: bytes | str, schema: dict) -> str:
    image_bytes, mime_type = _normalize_image_input(image_input)
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model=os.getenv("GEMINI_MODEL"),
        config=genai_types.GenerateContentConfig(
            system_instruction=CSV_GENERATOR_PROMPT,
        ),
        contents=[
            genai_types.Part.from_text(
                text="Using the provided JSON schema and the table image, generate a flattened CSV sample.",
            ),
            genai_types.Part.from_text(
                text=json.dumps(schema),
            ),
            genai_types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type,
            ),
        ],
    )
    
    return response.text.strip()