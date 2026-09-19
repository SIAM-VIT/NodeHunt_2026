from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Default to local SQLite so it runs out-of-the-box without needing PostgreSQL
    DATABASE_URL: str = "sqlite+aiosqlite:///./nodehunt.db"
    ADMIN_SECRET: str = "changeme"

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