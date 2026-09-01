from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/palletways_ci")
    test_database_url: str = Field(default="postgresql+psycopg://postgres:postgres@localhost:5432/palletways_ci_test")
    ai_provider: str = Field(default="groq")
    gemini_api_key: str = Field(default="")
    gemini_model: str = Field(default="gemini-3.6-flash")
    ollama_base_url: str = Field(default="http://localhost:11434")
    ollama_model: str = Field(default="")
    groq_api_key: str = Field(default="")
    groq_model: str = Field(default="llama-3.1-70b-versatile")
    
    network_crawl_max_depth: int = Field(default=3)
    network_crawl_max_pages: int = Field(default=100)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
