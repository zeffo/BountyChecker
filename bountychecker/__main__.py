import tomllib

# import sys
# from .core import BountyChecker, DefaultLogFileHandler
from .gui import GUILogFileHandler, GUIBountyChecker
from .config import Config

if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        data = tomllib.load(f)
    config = Config(**data)
    checker = GUIBountyChecker(config, GUILogFileHandler)
    checker.run()
