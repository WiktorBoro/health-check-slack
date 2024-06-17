# database.py
from datetime import datetime, timedelta
from json import load, dumps
from pathlib import Path
from typing import List

from dtos import HealthResultDTO, SlackConnectorConfigDTO


class Database:
    DATABASE_FILE_NAME = "database.json"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(
        self,
        *,
        config: SlackConnectorConfigDTO,
        current_path: Path,
    ):
        self.config = config
        self.current_path = current_path
        self.data = self._open()

    def _open(self):
        with open(
            f"{self.current_path}/{self.DATABASE_FILE_NAME}", "w"
        ) as database_file:
            return load(database_file)

    def commit(self):
        with open(
            f"{self.current_path}/{self.DATABASE_FILE_NAME}", "w"
        ) as database_file:
            database_file.write(dumps(self.data))

    @property
    def current_unhealthy_urls(self) -> List[str]:
        return [
            current_unhealthy
            for current_unhealthy in self.data.get("to_checks", {}).keys()
        ]

    def add_unhealthy(self, *, new_unhealthy: List[HealthResultDTO]):
        current_unhealthy_urls = self.current_unhealthy_urls
        for unhealthy in new_unhealthy:
            if unhealthy.url not in current_unhealthy_urls:
                self.data["to_checks"][unhealthy.url]["unhealthy_at"] = str(
                    datetime.now()
                )
                self.data["to_checks"][unhealthy.url]["last_send_at"] = str(
                    datetime.now()
                )

    def update_still_unhealthy_last_send(
        self, *, still_unhealthy: List[HealthResultDTO]
    ):
        current_unhealthy_urls = self.current_unhealthy_urls
        for unhealthy in still_unhealthy:
            if unhealthy.url in current_unhealthy_urls:
                self.data["to_checks"][unhealthy.url]["last_send_at"] = str(
                    datetime.now()
                )

    def remove_unhealthy(self, *, back_to_healthy: List[HealthResultDTO]):
        for healthy in back_to_healthy:
            self.data["to_checks"].pop(healthy, None)

    def get_how_long_was_unhealthy(self, *, url: str) -> float:
        return (
            datetime.now()
            - datetime.strptime(
                self.data["to_checks"][url].get("unhealthy_at", str(datetime.now())),
                self.DATE_FORMAT,
            )
        ).total_seconds() / 60

    def is_send_still_unhealthy_required(self, *, url: str) -> bool:
        return (
            datetime.now()
            - datetime.strptime(
                self.data["to_checks"][url].get("last_send_at", str(datetime.now())),
                self.DATE_FORMAT,
            )
        ) > timedelta(minutes=self.config.send_still_unhealthy_delay)
