import tkinter as tk
from pathlib import Path
from catppuccin import PALETTE
from .core import BaseLogFileHandler, BountyChecker, LogFileEventHandler
from .config import Config
from .bounties import Bounty, BountyCondition

from typing import Any

colors = PALETTE.mocha.colors


class GUILogFileHandler(
    LogFileEventHandler,
    BaseLogFileHandler,
):

    def __init__(self, path: Path, *, bounty_checker: "GUIBountyChecker"):
        super().__init__(path, bounty_checker=bounty_checker)

        self.tk_root = tk.Tk()
        self.tk_label = tk.Label(
            self.tk_root,
            text="Bounty Checker",
            fg=colors.text.hex,
            bg=colors.base.hex,
            font=("Roboto", 15, ""),
        )
        self.tk_root.overrideredirect(True)
        self.tk_root.attributes("-topmost", True)  # type: ignore
        self.tk_root.geometry("300x50")
        self.tk_root.configure(bg=colors.base.hex)
        self.tk_label.pack(fill="both", expand=True)

    def on_bounty(self, bounty: Bounty) -> Any:
        self.tk_update(text="Started bounty...")

    def on_good_bounty(self, bounty: Bounty) -> Any:
        self.tk_update(text=f"{bounty}\nGood Bounty!", fg=colors.green.hex)

    def on_bad_bounty(self, bounty: Bounty, conditions: list[BountyCondition]) -> Any:
        reasons = ", ".join(" ".join(c.name.split("_")[1:]).title() for c in conditions)
        self.tk_update(text=f"{bounty}\nBad Bounty ({reasons})", fg=colors.red.hex)

    def tk_update(self, **options: Any):
        self.tk_label.config(**options)
        self.tk_root.update_idletasks()
        padding = 30
        width = self.tk_label.winfo_reqwidth() + padding  # Add some padding
        height = self.tk_label.winfo_reqheight() + padding
        self.tk_root.geometry(f"{width}x{height}")


class GUIBountyChecker(BountyChecker):
    event_handler: GUILogFileHandler

    def __init__(self, config: Config, event_handler: type[GUILogFileHandler]):
        super().__init__(config, event_handler)

    def run(self):
        self.schedule()
        self.observer.start()
        print("Watchdog started")
        self.event_handler.tk_root.mainloop()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        finally:
            self.observer.stop()
            self.observer.join()
