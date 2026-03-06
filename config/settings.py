"""Application settings using Pydantic Settings for configuration management."""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Central configuration for the enablemind research system."""

    # API Keys - support OpenAI, Groq, and Gemini
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    groq_api_key: Optional[str] = Field(default=None, description="Groq API key (FREE)")
    gemini_api_key: Optional[str] = Field(default=None, description="Google Gemini API key (FREE)")

    # LLM Provider selection
    llm_provider: str = Field(default="gemini", description="LLM provider: 'openai', 'groq', or 'gemini'")

    # Model configuration (Primary models - LLM manager handles fallbacks)
    openai_model: str = Field(default="gpt-4o-mini", description="OpenAI model to use")
    groq_model: str = Field(default="llama-3.1-8b-instant", description="Groq model to use (FREE, FASTEST)")
    gemini_model: str = Field(default="gemini-1.5-flash", description="Gemini model to use (FREE)")

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")

    # Agent workflow configuration
    max_research_iterations: int = Field(
        default=1,
        description="Maximum feedback loop iterations between analysis and research",
    )
    max_search_results: int = Field(
        default=5,
        description="Maximum search results per query",
    )

    # Output configuration
    output_dir: str = Field(default="outputs", description="Directory for generated reports")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }

    def get_api_key(self) -> str:
        """Get the appropriate API key based on provider."""
        if self.llm_provider == "gemini":
            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in .env file. Get one free at https://aistudio.google.com/app/apikey")
            return self.gemini_api_key
        elif self.llm_provider == "groq":
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY not set in .env file. Get one free at https://console.groq.com/")
            return self.groq_api_key
        else:
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY not set in .env file")
            return self.openai_api_key

    def get_model(self) -> str:
        """Get the appropriate model based on provider."""
        if self.llm_provider == "gemini":
            return self.gemini_model
        elif self.llm_provider == "groq":
            return self.groq_model
        else:
            return self.openai_model

    def get_api_base(self) -> Optional[str]:
        """Get API base URL for the provider."""
        if self.llm_provider == "groq":
            return "https://api.groq.com/openai/v1"
        # Gemini and OpenAI use their default base URLs
        return None


def get_settings() -> Settings:
    """Create and return a Settings instance."""
    return Settings()
