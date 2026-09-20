from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default to local SQLite so it runs out-of-the-box without needing PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./nodehunt.db"
    ADMIN_SECRET: str = "changeme"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: str) -> str:
        if isinstance(v, str):
            if v.startswith("postgres://"):
                return v.replace("postgres://", "postgresql+asyncpg://", 1)
            if v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
                return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    # Volunteer verification passcodes (MPL model)
    VOLUNTEER_SUCCESS_CODES: str = "VERIFIED26,SOLVED,SunSunSunday,nodehunt"
    VOLUNTEER_STRIKE_CODES: str = "STRIKE26,RETRY,WRONG"

    @property
    def success_passcodes(self) -> set[str]:
        return {c.strip().lower() for c in self.VOLUNTEER_SUCCESS_CODES.split(",") if c.strip()}

    @property
    def strike_passcodes(self) -> set[str]:
        return {c.strip().lower() for c in self.VOLUNTEER_STRIKE_CODES.split(",") if c.strip()}

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()