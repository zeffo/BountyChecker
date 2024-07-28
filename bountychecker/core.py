import json
from pathlib import Path
from typing import Any, Protocol
from watchdog.observers import Observer
from watchdog.events import (
    FileModifiedEvent,
    FileSystemEvent,
    FileSystemEventHandler,
)
from .config import Config
from .bounties import BountyCondition, BOUNTY_START, Bounty


class BaseLogFileHandler(Protocol):
    config: Config
    path: Path

    def __init__(self, path: Path, *, config: Config):
        self.path = path

    def parse(self) -> Any:
        raise NotImplementedError

    def on_bounty(self, bounty: Bounty) -> Any:
        raise NotImplementedError

    def on_good_bounty(self, bounty: Bounty) -> Any:
        raise NotImplementedError

    def on_bad_bounty(self, bounty: Bounty, conditions: list[BountyCondition]) -> Any:
        raise NotImplementedError


class LogFileEventHandler(FileSystemEventHandler):

    def __init__(self, path: Path, *, config: Config) -> None:
        self.config = config
        self.path = path
        self._seek_settings = (
            0,
            2,
        )  # initially, seek to end. After, seek to (offset, 0)
        super().__init__()

    def on_modified(self, event: FileSystemEvent):
        if isinstance(event, FileModifiedEvent):
            if Path(event.src_path) == self.path:
                self.parse()

    def parse(self):
        with open(self.path) as f:
            f.seek(*self._seek_settings)
            data = f.read()
            _old_seek_settings = self._seek_settings
            self._seek_settings = (f.tell(), 0)
        if matches := BOUNTY_START.findall(data):
            try:
                bounty = Bounty(**json.loads(matches[-1]))
            except json.JSONDecodeError:
                # Sometimes watchdog calls on_modified during a partial write.
                # In that event, we should preserve the old seek settings so we can read the correct data on the complete write.
                self._seek_settings = _old_seek_settings
            else:
                self.handle_bounty(bounty)

    def check_bounty_conditions(self, bounty: Bounty) -> list[BountyCondition]:
        conditions: list[BountyCondition] = []
        if bounty.is_steel_path():
            conditions.append(BountyCondition.IS_STEEL_PATH)
        if not all(job in self.config.wanted_bounties for job in bounty.jobStages):
            conditions.append(BountyCondition.HAS_INCORRECT_STAGES)
        if bounty.tier != 4:
            conditions.append(BountyCondition.IS_WRONG_TIER)

        return conditions

    def handle_bounty(self, bounty: Bounty):
        self.on_bounty(bounty)
        if conditions := self.check_bounty_conditions(bounty):
            self.on_bad_bounty(bounty, conditions)
        else:
            self.on_good_bounty(bounty)

    def on_bounty(self, bounty: Bounty) -> Any:
        raise NotImplementedError

    def on_good_bounty(self, bounty: Bounty) -> Any:
        raise NotImplementedError

    def on_bad_bounty(self, bounty: Bounty, conditions: list[BountyCondition]) -> Any:
        raise NotImplementedError


class DefaultLogFileHandler(LogFileEventHandler):
    def on_bounty(self, bounty: Bounty) -> Any:
        print(f"Bounty started:\n{bounty}")

    def on_good_bounty(self, bounty: Bounty) -> Any:
        print("Bounty is good!")

    def on_bad_bounty(self, bounty: Bounty, conditions: list[BountyCondition]) -> Any:
        reasons = ", ".join(
            " ".join(c.name.split("_")).capitalize() for c in conditions
        )
        print(f"Bounty is bad ({reasons})")


class BountyChecker:
    def __init__(self, config: Config, event_handler: type[BaseLogFileHandler]):
        self.config = config
        self.observer = Observer()
        self.event_handler = event_handler(self.config.log_path, config=config)

    def schedule(self):
        self.observer.schedule(self.event_handler, self.config.log_path)  # type: ignore

    def run(self):
        self.schedule()
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        finally:
            self.observer.stop()
            self.observer.join()
