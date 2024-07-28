from pathlib import Path
from pydantic_settings import BaseSettings


class Config(BaseSettings):
    wanted_bounties: set[str]
    log_path: Path
