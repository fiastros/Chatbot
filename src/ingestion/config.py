"""
This ensures the app crashes instantly and safely if any credentials or URLs are missing.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    neo4j_uri: str
    neo4j_user: str
    neo4j_password: str
    chroma_db_path: str
    log_level: str = "INFO"
    docling_mcp_url: str
    chunker_mcp_url: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()