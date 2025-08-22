"""
Career Copilot Agent - Portia SDK Configuration
Built with Portia AI SDK following official documentation patterns
"""
import os
from dotenv import load_dotenv
from portia import Config, StorageClass, LogLevel, LLMProvider

# Load environment variables
load_dotenv()

class CareerCopilotConfig:
    """Configuration for Career Copilot Agent using official Portia SDK patterns"""
    
    def __init__(self):
        # API Keys (automatically loaded from environment)
        self.portia_api_key = os.getenv("PORTIA_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        
        # Application settings
        self.app_name = "Career Copilot Agent"
        self.version = "1.0.0"
        
        # Portia configuration using official from_default() method
        self.portia_config = self._create_portia_config()
    
    def _create_portia_config(self) -> Config:
        """Create Portia configuration following official documentation"""
        # Prefer OpenAI if available, otherwise fall back to Google Gemini
        # Portia expects certain types (e.g., SecretStr) for keys; to avoid runtime
        # errors when the env format is incompatible, we can selectively fall back.
        if os.getenv("FORCE_GEMINI", "").lower() in {"1", "true", "yes"}:
            use_openai = False
        else:
            use_openai = bool(self.openai_api_key)
        llm_provider = LLMProvider.OPENAI if use_openai else LLMProvider.GOOGLE
        default_model = (
            "openai/gpt-4o-mini" if use_openai else "google/gemini-1.5-flash"
        )

        try:
            cfg = Config.from_default(
                llm_provider=llm_provider,
                default_model=default_model,
                storage_class=StorageClass.CLOUD if self.portia_api_key else StorageClass.MEMORY,
                default_log_level=LogLevel.DEBUG if self.portia_api_key else LogLevel.INFO,
            )
        except Exception:
            # Fallback to Gemini if OpenAI setup is invalid for the SDK
            cfg = Config.from_default(
                llm_provider=LLMProvider.GOOGLE,
                default_model="google/gemini-1.5-flash",
                storage_class=StorageClass.CLOUD if self.portia_api_key else StorageClass.MEMORY,
                default_log_level=LogLevel.DEBUG if self.portia_api_key else LogLevel.INFO,
            )

        # Prefer stable/safe model family across all roles when using Gemini
        try:
            if getattr(cfg, "llm_provider", None) == LLMProvider.GOOGLE and hasattr(cfg, "models"):
                for attr in (
                    "planning_model",
                    "execution_model",
                    "introspection_model",
                    "summarizer_model",
                ):
                    if hasattr(cfg.models, attr):
                        setattr(cfg.models, attr, "google/gemini-1.5-flash")
        except Exception:
            pass

        return cfg

    def is_configured(self) -> bool:
        """Check if all required configurations are set"""
        # Either OpenAI or Google key should be present; Portia API key enables cloud storage & tools
        return bool(self.openai_api_key or self.google_api_key)

    # ----- New helpers for UI status -----
    def has_portia_cloud(self) -> bool:
        return bool(self.portia_api_key)

    def google_oauth_ready(self) -> bool:
        return all([
            os.getenv("GOOGLE_CLIENT_ID"),
            os.getenv("GOOGLE_CLIENT_SECRET"),
            os.getenv("GOOGLE_REDIRECT_URI"),
        ])

    def sheet_target_ready(self) -> bool:
        return bool(os.getenv("SHEET_ID"))

    def status_summary(self) -> dict:
        """Return a structured status block the UI can leverage."""
        provider = getattr(self.portia_config, "llm_provider", None)
        provider_name = getattr(provider, "name", str(provider)) if provider else "unknown"
        return {
            "llm_provider": provider_name,
            "has_llm_key": self.is_configured(),
            "has_portia_api_key": self.has_portia_cloud(),
            "google_oauth_ready": self.google_oauth_ready(),
            "sheet_target_ready": self.sheet_target_ready(),
        }

# Global configuration instance
config = CareerCopilotConfig()
