# database.py
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import List

from dtos import HealthResultDTO, SlackConnectorConfigDTO


class Database:
    DATABASE_BASE_FILE_NAME = "database_base.json"
    DATABASE_FILE_NAME = "database.json"
    DATE_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"

    def __init__(
        self,
        *,
        current_path: Path,
    ):
        self.current_path = current_path
        self._init()
        self.data = self._open()

    def _init(self):
        if not os.path.isfile(f"{self.current_path}/{self.DATABASE_FILE_NAME}"):
            with open(
                f"{self.current_path}/{self.DATABASE_BASE_FILE_NAME}", "r"
            ) as database_base_file:
                database_base_data = json.load(database_base_file)
            with open(
                f"{self.current_path}/{self.DATABASE_FILE_NAME}", "w"
            ) as database_file:
                json.dump(database_base_data, database_file)

    def _open(self):
        with open(
            f"{self.current_path}/{self.DATABASE_FILE_NAME}", "r"
        ) as database_file:
            return json.load(database_file)

    def commit(self):
        with open(
            f"{self.current_path}/{self.DATABASE_FILE_NAME}", "w"
        ) as database_file:
            json.dump(self.data, database_file)

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
                self.data["to_checks"][unhealthy.url] = {}
                self.data["to_checks"][unhealthy.url][
                    "unhealthy_at"
                ] = datetime.now().isoformat()
                self.data["to_checks"][unhealthy.url][
                    "last_send_at"
                ] = datetime.now().isoformat()

    def update_still_unhealthy_last_send(
        self, *, still_unhealthy: List[HealthResultDTO]
    ):
        current_unhealthy_urls = self.current_unhealthy_urls
        for unhealthy in still_unhealthy:
            if unhealthy.is_sent_to_slack and unhealthy.url in current_unhealthy_urls:
                self.data["to_checks"][unhealthy.url][
                    "last_send_at"
                ] = datetime.now().isoformat()

    def remove_unhealthy(self, *, back_to_healthy: List[HealthResultDTO]):
        for healthy in back_to_healthy:
            self.data["to_checks"].pop(healthy, None)

    def get_how_long_was_unhealthy(self, *, url: str) -> float:
        return round(
            (
                datetime.now()
                - datetime.strptime(
                    self.data["to_checks"]
                    .get(url, {})
                    .get("unhealthy_at", datetime.now().isoformat()),
                    self.DATE_FORMAT,
                )
            ).total_seconds()
            / 60,
            0,
        )

    def is_send_still_unhealthy_required(
        self,
        *,
        url: str,
        config: SlackConnectorConfigDTO,
    ) -> bool:
        return (
            datetime.now()
            - datetime.strptime(
                self.data["to_checks"]
                .get(url, {})
                .get("last_send_at", datetime.now().isoformat()),
                self.DATE_FORMAT,
            )
        ) > timedelta(minutes=config.send_still_unhealthy_delay)
