import os
from typing import Optional
from openai import OpenAI


class ConfigurationError(Exception):
    pass


class Config:
    """
    Lightweight config reader that reads from environment variables.
    Works both with a local .env file (loaded by app.py via python-dotenv)
    and Railway's injected environment variables (no .env file needed).
    """

    def __init__(self):
        self._llm_client: Optional[OpenAI] = None
        self._validate_configuration()

    def _validate_configuration(self) -> None:
        errors = []

        llm_provider = os.getenv("LLM_PROVIDER", "").lower()
        if llm_provider != "ollama":
            errors.append(f"Invalid LLM_PROVIDER: '{llm_provider}'. Must be: ollama")

        if llm_provider == "ollama":
            if not os.getenv("OLLAMA_BASE_URL"):
                errors.append("Missing required configuration: OLLAMA_BASE_URL")
            if not os.getenv("OLLAMA_API_KEY"):
                errors.append("Missing required API key: OLLAMA_API_KEY")
            if not os.getenv("OLLAMA_MODEL"):
                errors.append("Missing required configuration: OLLAMA_MODEL")

        if not os.getenv("PEXELS_API_KEY"):
            errors.append("Missing required API key: PEXELS_API_KEY")

        if errors:
            msg = "Configuration validation failed:\n\n"
            for e in errors:
                msg += f"  - {e}\n"
            msg += "\nPlease ensure all required environment variables are set."
            raise ConfigurationError(msg)

    def get_llm_provider(self) -> str:
        return os.getenv("LLM_PROVIDER", "").lower()

    def get_llm_model(self) -> str:
        return os.getenv("OLLAMA_MODEL", "qwen3.5:cloud")

    def get_llm_client(self) -> OpenAI:
        if self._llm_client is not None:
            return self._llm_client

        base_url = os.getenv("OLLAMA_BASE_URL", "https://ollama.com/api")
        if not base_url.endswith("/v1"):
            base_url = base_url.rstrip("/") + "/v1"

        api_key = os.getenv("OLLAMA_API_KEY", "")
        self._llm_client = OpenAI(base_url=base_url, api_key=api_key)
        return self._llm_client

    def get_pexels_api_key(self) -> str:
        key = os.getenv("PEXELS_API_KEY")
        if not key:
            raise ConfigurationError("PEXELS_API_KEY not found in environment variables")
        return key

    def get_video_orientation(self) -> bool:
        """Returns True for landscape, False for portrait."""
        orientation = os.getenv("VIDEO_ORIENTATION", "portrait").lower()
        if orientation not in ["portrait", "landscape"]:
            raise ConfigurationError(
                f"Invalid VIDEO_ORIENTATION: '{orientation}'. Must be 'portrait' or 'landscape'"
            )
        return orientation == "landscape"

    def get_captions_enabled(self) -> bool:
        return os.getenv("CAPTIONS_ENABLED", "true").lower() == "true"

    def get_caption_font_size(self) -> int:
        return int(os.getenv("CAPTION_FONT_SIZE", "100"))

    def get_caption_font_color(self) -> str:
        return os.getenv("CAPTION_FONT_COLOR", "white").lower()

    def get_caption_stroke_width(self) -> int:
        return int(os.getenv("CAPTION_STROKE_WIDTH", "3"))

    def get_caption_stroke_color(self) -> str:
        return os.getenv("CAPTION_STROKE_COLOR", "black").lower()

    def get_caption_position(self) -> str:
        position = os.getenv("CAPTION_POSITION", "bottom_center").lower()
        valid = ["center", "top", "bottom", "bottom_center", "bottom_left", "bottom_right"]
        if position not in valid:
            raise ConfigurationError(
                f"Invalid CAPTION_POSITION: '{position}'. Must be one of: {', '.join(valid)}"
            )
        return position

    def get_caption_font_face(self) -> str:
        return os.getenv("CAPTION_FONT_FACE", "Arial-Bold")


def get_config() -> Config:
    try:
        return Config()
    except ConfigurationError as e:
        print(f"\n{'='*70}")
        print("ERROR: Configuration Failed")
        print("=" * 70)
        print(f"\n{str(e)}\n")
        print("Please fix these issues and try again.")
        print("=" * 70 + "\n")
        raise
