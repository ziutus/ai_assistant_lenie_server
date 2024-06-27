import library.api.aws.bedrock_embedding as amazon_bedrock
import library.api.openai.openai_embedding as openai_embedding
from library.embedding_result import EmbeddingResult


def embedding_need_translation(model: str) -> bool:
    if model in ["amazon_bedrock", "amazon.titan-embed-text-v1"]:
        return True
    elif model in ["amazon.titan-embed-text-v2:0"]:
        return False
    elif model in ["openai_embedding", "text-embedding-ada-002"]:
        return True
    else:
        raise f"DEBUG: Error, no model info for text {model}"


def get_embedding(model: str, text: str) -> EmbeddingResult:
    if model in ["amazon_bedrock", "amazon.titan-embed-text-v1"]:
        return amazon_bedrock.get_embedding(text)
    elif model in ["amazon.titan-embed-text-v2:0"]:
        return amazon_bedrock.get_embedding2(text)
    elif model in ["openai_embedding", "text-embedding-ada-002"]:
        return openai_embedding.get_embedding(text)
    else:
        raise f"DEBUG: Error, not supported model {model}"
