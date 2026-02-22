"""LLM provider abstractions for flexible natural language to SQL translation."""

import logging
import os
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    @abstractmethod
    async def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate a response from the LLM.
        
        Args:
            system_prompt: System instructions for the LLM
            user_message: User query to process
            
        Returns:
            Generated response text
        """
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the provider is properly configured."""
        pass


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, api_key: str | None = None, model: str = "claude-3-5-sonnet-20241022") -> None:
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
                logger.info(f"Anthropic provider initialized with model: {self.model}")
            except ImportError:
                logger.warning("anthropic package not installed. Install with: pip install anthropic")

    def is_configured(self) -> bool:
        return self.client is not None

    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("Anthropic provider not configured. Set ANTHROPIC_API_KEY environment variable.")
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                temperature=0,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
            return response.content[0].text.strip()
        except Exception as e:
            logger.error(f"Anthropic API call failed: {e}")
            raise Exception(f"Anthropic API error: {str(e)}")


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o") -> None:
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None
        
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self.client = AsyncOpenAI(api_key=self.api_key)
                logger.info(f"OpenAI provider initialized with model: {self.model}")
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")

    def is_configured(self) -> bool:
        return self.client is not None

    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("OpenAI provider not configured. Set OPENAI_API_KEY environment variable.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
                max_tokens=2000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")


class OllamaProvider(LLMProvider):
    """Ollama local LLM provider."""

    def __init__(self, model: str = "llama3.1", base_url: str = "http://localhost:11434") -> None:
        self.model = model
        self.base_url = base_url
        self.client = None
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(
                base_url=f"{base_url}/v1",
                api_key="ollama",  # Ollama doesn't require a real API key
            )
            logger.info(f"Ollama provider initialized with model: {self.model}")
        except ImportError:
            logger.warning("openai package not installed. Install with: pip install openai")

    def is_configured(self) -> bool:
        return self.client is not None

    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client:
            raise ValueError("Ollama provider not configured. Install openai package.")
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
                max_tokens=2000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Ollama API call failed: {e}")
            raise Exception(f"Ollama API error: {str(e)}")


class AzureOpenAIProvider(LLMProvider):
    """Azure OpenAI provider."""

    def __init__(
        self,
        api_key: str | None = None,
        endpoint: str | None = None,
        deployment: str | None = None,
        api_version: str = "2024-02-15-preview",
    ) -> None:
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = api_version
        self.client = None
        
        if self.api_key and self.endpoint:
            try:
                from openai import AsyncAzureOpenAI
                self.client = AsyncAzureOpenAI(
                    api_key=self.api_key,
                    api_version=self.api_version,
                    azure_endpoint=self.endpoint,
                )
                logger.info(f"Azure OpenAI provider initialized with deployment: {self.deployment}")
            except ImportError:
                logger.warning("openai package not installed. Install with: pip install openai")

    def is_configured(self) -> bool:
        return self.client is not None and self.deployment is not None

    async def generate(self, system_prompt: str, user_message: str) -> str:
        if not self.client or not self.deployment:
            raise ValueError(
                "Azure OpenAI provider not configured. Set AZURE_OPENAI_API_KEY, "
                "AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT environment variables."
            )
        
        try:
            response = await self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message},
                ],
                temperature=0,
                max_tokens=2000,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Azure OpenAI API call failed: {e}")
            raise Exception(f"Azure OpenAI API error: {str(e)}")


def create_provider(provider_type: str = "anthropic", **kwargs: Any) -> LLMProvider:
    """Factory function to create LLM providers.
    
    Args:
        provider_type: Type of provider ('anthropic', 'openai', 'ollama', 'azure')
        **kwargs: Provider-specific configuration
        
    Returns:
        Configured LLM provider instance
    """
    providers = {
        "anthropic": AnthropicProvider,
        "openai": OpenAIProvider,
        "ollama": OllamaProvider,
        "azure": AzureOpenAIProvider,
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(
            f"Unknown provider type: {provider_type}. "
            f"Available providers: {', '.join(providers.keys())}"
        )
    
    return provider_class(**kwargs)
