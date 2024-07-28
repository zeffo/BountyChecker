import tomllib
from .core import BountyChecker, DefaultLogFileHandler
from .config import Config

if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
    config = Config(**data)
    checker = BountyChecker(config, DefaultLogFileHandler)
    checker.run()
