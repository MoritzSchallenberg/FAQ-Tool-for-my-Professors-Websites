from dataclasses import dataclass
import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if load_dotenv is not None:
    load_dotenv(ENV_PATH)


@dataclass(frozen=True)
class Settings:
    db_host: str = os.getenv("DB_HOST", "127.0.0.1")
    db_port: int = int(os.getenv("DB_PORT", "3306"))
    db_user: str = os.getenv("DB_USER", "faq_user")
    db_password: str = os.getenv("DB_PASSWORD", "change-me")
    db_name: str = os.getenv("DB_NAME", "faq_tool")

    admin_username: str = os.getenv("ADMIN_USERNAME", "admin")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "change-me-now")

    token_secret: str = os.getenv("TOKEN_SECRET", "please-change-this-token-secret")
    token_hours: int = int(os.getenv("TOKEN_HOURS", "12"))
    ip_hash_salt: str = os.getenv("IP_HASH_SALT", "please-change-this-ip-salt")

    course_slug: str = os.getenv("COURSE_SLUG", "et")
    course_name: str = os.getenv("COURSE_NAME", "Elektrotechnik/Elektronik")

    # Comma-separated origins, for example: https://prof.example.de,https://faq.example.de
    allowed_origins: str = os.getenv("ALLOWED_ORIGINS", "*")

    max_question_length: int = int(os.getenv("MAX_QUESTION_LENGTH", "2000"))
    max_questions_per_hour: int = int(os.getenv("MAX_QUESTIONS_PER_HOUR", "5"))


_settings = Settings()


def get_settings() -> Settings:
    return _settings
