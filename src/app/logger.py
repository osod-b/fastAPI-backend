from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import logging
import os

from pathlib import Path, PurePath

class Logger(logging.Logger):
    def __init__(self, name, level=logging.INFO):
        super().__init__(name, level)

        self.path = self._init_fol()
        self.date = self._init_date()
        self._init_file()

    def _init_fol(self) -> str:
        current = Path(__file__).parent.parent.parent.resolve()
        base = Path('logs')

        destination = PurePath.joinpath(current, base)

        if not Path(destination).exists():
            Path.mkdir(destination, exist_ok=True)

        return destination

    def _init_date(self) -> str:
        region = ZoneInfo("Europe/London")
        time = datetime.now(region).strftime("%d-%m-%y")

        return time

    def _init_file(self):
        filename = self.date + '.log'

        formatter = logging.Formatter(
                    "%(asctime)s - %(levelname)s - %(message)s",
                    datefmt="%m/%d/%Y",
                )

        handler = logging.FileHandler(self.path / filename)
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def __str__(self):
        return f'path: {self.path} \ncurrent filename: {self.date}.log'
    

log = Logger("log_app")

