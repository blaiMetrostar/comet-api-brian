"""Service layer for Chat / RAG interactions with AWS Bedrock.

Provides a thin wrapper around the Bedrock Agent Runtime `retrieve_and_generate`
API to perform Retrieval Augmented Generation against a configured knowledge base.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict

import boto3
from botocore.exceptions import BotoCoreError, ClientError
from fastapi import HTTPException

from app.config import settings

logger = logging.getLogger(__name__)

def _get_bedrock_client():
    """Create a Bedrock Agent Runtime client.

    Uses explicit credentials only if set in settings; otherwise falls back to
    default provider chain (env, shared config, IAM role, etc.).
    """
    client_kwargs: Dict[str, Any] = {"service_name": "bedrock-agent-runtime"}
    if settings.AWS_DEFAULT_REGION:
        client_kwargs["region_name"] = settings.AWS_DEFAULT_REGION
    if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
        client_kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
        client_kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
    return boto3.client(**client_kwargs)  # type: ignore[arg-type]


def retrieve_and_generate(prompt: str) -> dict:
    """Send a prompt to Bedrock using Retrieve & Generate against a knowledge base.

    Args:
        prompt: User's natural language question or instruction.

    Returns:
        dict: Simplified response containing generated text and any citations.

    Raises:
        HTTPException: On configuration problems or AWS errors.
    """
    if not prompt or not prompt.strip():
        raise HTTPException(status_code=400, detail="Prompt must not be empty")

    if not settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID or not settings.AWS_BEDROCK_MODEL_ARN:
        raise HTTPException(
            status_code=500,
            detail="Bedrock knowledge base or model ARN not configured",
        )

    client = _get_bedrock_client()

    # Build generation config using optional tuning parameters when provided.
    inference_config: Dict[str, Any] = {"textInferenceConfig": {}}
    inner = inference_config["textInferenceConfig"]
    if settings.AWS_BEDROCK_MAX_TOKENS:
        inner["maxTokens"] = settings.AWS_BEDROCK_MAX_TOKENS
    if settings.AWS_BEDROCK_TEMPERATURE is not None:
        inner["temperature"] = settings.AWS_BEDROCK_TEMPERATURE
    if settings.AWS_BEDROCK_TOP_P is not None:
        inner["topP"] = settings.AWS_BEDROCK_TOP_P

    vector_search_cfg: Dict[str, Any] = {}
    if settings.AWS_BEDROCK_NUM_RESULTS:
        vector_search_cfg["numberOfResults"] = settings.AWS_BEDROCK_NUM_RESULTS

    retrieve_config: Dict[str, Any] = {
        "vectorSearchConfiguration": vector_search_cfg or {"numberOfResults": 5}
    }

    kb_config: Dict[str, Any] = {
        "knowledgeBaseId": settings.AWS_BEDROCK_KNOWLEDGE_BASE_ID,
        "modelArn": settings.AWS_BEDROCK_MODEL_ARN,
        "retrievalConfiguration": retrieve_config,
        "generationConfiguration": {
            "inferenceConfig": inference_config,
        },
    }

    request_kwargs: Dict[str, Any] = {
        "input": {"text": prompt},
        "retrieveAndGenerateConfiguration": {
            "type": "KNOWLEDGE_BASE",
            "knowledgeBaseConfiguration": kb_config,
        }
    }
    if settings.AWS_BEDROCK_KMS_KEY_ARN:
        request_kwargs["sessionConfiguration"] = {
            "kmsKeyArn": settings.AWS_BEDROCK_KMS_KEY_ARN
        }

    try:
        logger.debug("Calling Bedrock retrieve_and_generate: %s", request_kwargs)
        response = client.retrieve_and_generate(**request_kwargs)
        logger.info("Bedrock RAG call succeeded")
    except (BotoCoreError, ClientError) as e:
        logger.exception("Bedrock RAG call failed")
        raise HTTPException(status_code=502, detail=f"Bedrock error: {e}") from e

    output_text = (
        response.get("output", {}).get("text")
        if isinstance(response.get("output"), dict)
        else None
    )
    citations = response.get("citations", [])

    return {"text": output_text, "citations": citations}
