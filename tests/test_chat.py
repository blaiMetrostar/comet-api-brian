from unittest.mock import patch


def test_chat_endpoint(client):
    # Stub Bedrock client
    class StubBedrockClient:
        def retrieve_and_generate(self, **kwargs):  # noqa: D401
            return {
                "output": {"text": "Stubbed answer"},
                "citations": [
                    {"source": "doc1", "text": "Example citation"},
                ],
            }

    with patch("app.chat.services.boto3.client", return_value=StubBedrockClient()):
        response = client.get("/chat", params={"prompt": "Hello"})

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == "Stubbed answer"
    assert isinstance(body["citations"], list)
