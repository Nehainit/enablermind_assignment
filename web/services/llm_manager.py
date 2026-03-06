"""LLM Manager with automatic fallback for rate limits."""

import structlog
from typing import Optional, List, Dict, Any
from crewai import LLM

logger = structlog.get_logger("llm_manager")


class LLMConfig:
    """Configuration for a single LLM provider."""

    def __init__(
        self,
        name: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        priority: int = 0,
    ):
        self.name = name
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.priority = priority  # Lower = higher priority

    def create_llm(self) -> LLM:
        """Create a CrewAI LLM instance."""
        return LLM(
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
        )


class LLMManager:
    """Manages multiple LLM providers with automatic fallback."""

    def __init__(self):
        self.providers: List[LLMConfig] = []
        self.current_provider_index = 0

    def add_provider(
        self,
        name: str,
        model: str,
        api_key: str,
        base_url: Optional[str] = None,
        priority: int = 0,
    ):
        """Add an LLM provider to the fallback chain."""
        if not api_key:
            logger.warning("skipping_provider_no_key", name=name)
            return

        config = LLMConfig(
            name=name,
            model=model,
            api_key=api_key,
            base_url=base_url,
            priority=priority,
        )
        self.providers.append(config)
        logger.info("added_llm_provider", name=name, model=model, priority=priority)

    def setup_providers_from_settings(self, settings):
        """Setup providers from application settings with fallback order.

        Using ONLY Groq models for all fallbacks.
        """
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY is required. Get one free at https://console.groq.com/")

        # All providers use the same Groq API key
        # Using ONLY TESTED & VERIFIED Groq models (tested 2026-03-07)
        groq_base = "https://api.groq.com/openai/v1"

        # Priority 0: Kimi K2 (Moonshot AI's 1T MoE, 256k context) ✅ TESTED
        self.add_provider(
            name="groq-kimi-k2",
            model="moonshotai/kimi-k2-instruct",
            api_key=settings.groq_api_key,
            base_url=groq_base,
            priority=0,
        )

        # Priority 1: Llama 3.1 8B Instant (fastest, ~1000 tokens/sec) ✅ TESTED
        self.add_provider(
            name="groq-8b-instant",
            model="llama-3.1-8b-instant",
            api_key=settings.groq_api_key,
            base_url=groq_base,
            priority=1,
        )

        # Priority 2: Llama 3.3 70B (latest large model, 128k context) ✅ TESTED
        self.add_provider(
            name="groq-3.3-70b",
            model="llama-3.3-70b-versatile",
            api_key=settings.groq_api_key,
            base_url=groq_base,
            priority=2,
        )

        # Sort by priority
        self.providers.sort(key=lambda p: p.priority)

        if not self.providers:
            raise ValueError("No LLM providers configured. Please set at least one API key.")

        logger.info(
            "llm_fallback_chain_configured",
            primary=self.providers[0].name if self.providers else None,
            total_providers=len(self.providers),
            chain=[f"{p.name}({p.model})" for p in self.providers],
        )

    def get_current_llm(self) -> LLM:
        """Get the current active LLM."""
        if not self.providers:
            raise ValueError("No LLM providers available")

        provider = self.providers[self.current_provider_index]
        logger.info(
            "using_llm_provider",
            name=provider.name,
            model=provider.model,
            index=self.current_provider_index,
            total=len(self.providers),
        )
        return provider.create_llm()

    def fallback_to_next_provider(self) -> bool:
        """Switch to the next provider in the fallback chain.

        Returns:
            True if there's a next provider, False if we've exhausted all providers.
        """
        if self.current_provider_index >= len(self.providers) - 1:
            logger.error(
                "no_fallback_providers_available",
                exhausted=len(self.providers),
            )
            return False

        old_provider = self.providers[self.current_provider_index]
        self.current_provider_index += 1
        new_provider = self.providers[self.current_provider_index]

        logger.warning(
            "falling_back_to_next_provider",
            from_provider=old_provider.name,
            to_provider=new_provider.name,
            remaining_fallbacks=len(self.providers) - self.current_provider_index - 1,
        )
        return True

    def reset_to_primary(self):
        """Reset to the primary (highest priority) provider."""
        if self.current_provider_index > 0:
            logger.info("resetting_to_primary_provider")
            self.current_provider_index = 0

    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about current and available providers."""
        if not self.providers:
            return {"current": None, "available": []}

        current = self.providers[self.current_provider_index]
        return {
            "current": {
                "name": current.name,
                "model": current.model,
                "priority": current.priority,
            },
            "available": [
                {
                    "name": p.name,
                    "model": p.model,
                    "priority": p.priority,
                }
                for p in self.providers
            ],
            "has_fallback": self.current_provider_index < len(self.providers) - 1,
        }


# Singleton instance
_llm_manager: Optional[LLMManager] = None


def get_llm_manager() -> LLMManager:
    """Get or create the singleton LLM manager."""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = LLMManager()
    return _llm_manager


def initialize_llm_manager(settings):
    """Initialize the LLM manager with settings."""
    manager = get_llm_manager()
    manager.setup_providers_from_settings(settings)
    return manager
