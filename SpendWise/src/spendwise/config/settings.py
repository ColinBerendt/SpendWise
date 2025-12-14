"""
Application settings loaded from environment variables
"""

import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass
class Settings:
    """Main application settings"""
    openai_api_key: str

    @classmethod
    def from_env(cls) -> "Settings":
        """Load settings from environment variables"""
        load_dotenv()

        return cls(
            openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
        )

    def validate(self) -> list[str]:
        """Validate settings and return list of errors"""
        errors = []
        if not self.openai_api_key:
            errors.append("OPENAI_API_KEY is not set")
        return errors


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings.from_env()
