"""Configuration management - load environment variables via pydantic-settings."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Text generation (text-to-text)
    llm_main_base_url: str = "http://localhost:8000/v1"
    llm_main_model: str = "Qwen/Qwen2.5-7B"
    llm_main_model_api_key: str = "not-needed"

    # Text generation (text+image-to-text)
    vlm_text_gen_base_url: str | None = None
    vlm_text_gen_model: str | None = None
    vlm_text_gen_model_api_key: str | None = None

    # Image generation (text-to-image)
    llm_image_gen_base_url: str | None = None
    llm_image_gen_model: str | None = None
    llm_image_gen_model_api_key: str | None = None

    # Safety check
    forbidden_words_file: str | None = None
    safety_use_llm: bool = True
    safety_llm_model: str | None = None

    # Modular extension
    skills_dirs: str | None = None
    config_dir: str = "config"

    # Service
    log_level: str = "INFO"
    max_concurrent_jobs: int = 10

    @property
    def config_path(self) -> Path:
        return Path.cwd() / self.config_dir  # type: ignore[arg-type]

    @property
    def stage_contexts_path(self) -> Path:
        return self.config_path / "stage_contexts.yaml"

    @property
    def mcp_servers_path(self) -> Path:
        return self.config_path / "mcp_servers.yaml"

    @property
    def extra_skills_dirs(self) -> list[Path]:
        if not self.skills_dirs:
            return []
        return [Path(p.strip()) for p in self.skills_dirs.split(",") if p.strip()]

    # Resolved config for text-to-text (LLM_MAIN_*)
    @property
    def main_model_url(self) -> str:
        return self.llm_main_base_url

    @property
    def main_model(self) -> str:
        return self.llm_main_model

    @property
    def main_model_api_key(self) -> str:
        return self.llm_main_model_api_key

    # Resolved config for text+image-to-text (VLM_TEXT_GEN_* or LLM_MAIN_*)
    @property
    def vlm_text_gen_url(self) -> str:
        return self.vlm_text_gen_base_url or self.llm_main_base_url

    @property
    def vlm_text_gen_resolved_model(self) -> str:
        return self.vlm_text_gen_model or self.llm_main_model

    @property
    def vlm_text_gen_resolved_api_key(self) -> str:
        return self.vlm_text_gen_model_api_key or self.llm_main_model_api_key

    # Resolved config for image generation (LLM_IMAGE_GEN_* or LLM_MAIN_*)
    @property
    def image_gen_url(self) -> str:
        return self.llm_image_gen_base_url or self.llm_main_base_url

    @property
    def image_gen_model(self) -> str:
        return self.llm_image_gen_model or self.llm_main_model

    @property
    def image_gen_api_key(self) -> str:
        return self.llm_image_gen_model_api_key or self.llm_main_model_api_key

    @property
    def image_gen_enabled(self) -> bool:
        """Image generation enabled when LLM_IMAGE_GEN_BASE_URL or LLM_IMAGE_GEN_MODEL is set."""
        return bool(self.llm_image_gen_base_url or self.llm_image_gen_model)

    @property
    def image_gen_size(self) -> str:
        """Default image size for API request (e.g. 1024x1024). From config/model_deployment/image_gen.yaml."""
        try:
            from model_deployment.config import get_agent_image_config
            return get_agent_image_config().get("default_size", "1024x1024")
        except ImportError:
            return "1024x1024"


settings = Settings()
