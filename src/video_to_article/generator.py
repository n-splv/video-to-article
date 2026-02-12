from typing import Protocol

from dotenv import load_dotenv
from openai import OpenAI

from video_to_article.logging_config import logger

load_dotenv()


class Generator(Protocol):
    """
    Protocol for text generation backends.

    Implementations accept **kwargs at two levels:
    - Instantiation: stored as instance defaults (e.g., temperature=0.7)
    - generate() call: per-call overrides, merged with instance defaults
    """

    def generate(self, messages: list[dict], **kwargs) -> str: ...


class OpenAIGenerator:
    default_kwargs: dict = {}
    _client: OpenAI | None = None
    _available_models: set[str] | None = None

    def __init__(self, model: str, **kwargs):
        self.model = model
        self.kwargs = {**self.default_kwargs, **kwargs}

    @classmethod
    def get_client(cls) -> OpenAI:
        if cls._client is None:
            cls._client = OpenAI()
        return cls._client

    @classmethod
    def get_available_models(cls) -> set[str]:
        if cls._available_models is None:
            cls._available_models = {m.id for m in cls.get_client().models.list()}
        return cls._available_models

    def generate(self, messages: list[dict], **kwargs) -> str:
        merged_kwargs = {**self.kwargs, **kwargs}

        response = self.get_client().chat.completions.create(
            model=self.model,
            messages=messages,
            **merged_kwargs,
        )
        return response.choices[0].message.content


class MLXGenerator:
    default_kwargs: dict = {"max_tokens": -1, "verbose": False}
    default_chat_template_kwargs: dict = {"enable_thinking": False}

    def __init__(self, model_path: str, **kwargs):
        try:
            from mlx_lm import load
        except ImportError:
            raise ImportError(
                "mlx-lm is not installed. Install with: pip install v2a[mlx-lm]"
            )

        self.model, self.tokenizer = load(model_path)
        self.kwargs = {**self.default_kwargs, **kwargs}

    def generate(self, messages: list[dict], **kwargs) -> str:
        from mlx_lm import generate

        merged_kwargs = {**self.kwargs, **kwargs}
        prompt = self.tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, **self.default_chat_template_kwargs
        )
        response = generate(
            self.model, self.tokenizer, prompt, **merged_kwargs
        )
        if "</think>" in response:
            response = response.split("</think>")[1].strip()

        return response


def get_generator(model: str, **kwargs) -> Generator:
    """
    :raises ImportError: if mlx-lm is not installed and model is not an OpenAI model
    """
    logger.info("Getting generator for %s", model)
    if model in OpenAIGenerator.get_available_models():
        return OpenAIGenerator(model, **kwargs)
    return MLXGenerator(model, **kwargs)
