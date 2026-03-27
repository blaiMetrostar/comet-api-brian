from fastapi import APIRouter
from starlette import status

from app.config import settings
import app.chat.services as service

router = APIRouter(
    prefix=f"{settings.API_PREFIX}/chat",
    tags=["Chat"],
)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_chat(prompt: str):
    """Retrieve & Generate response from Bedrock using a knowledge base.

    Args:
        prompt: User's input text (query/question).

    Returns:
        dict: {"text": <generated text>, "citations": [...]}.
    """
    return service.retrieve_and_generate(prompt)
