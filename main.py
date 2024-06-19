#!/usr/bin/env python
import logging
import pathlib
import sys
from datetime import datetime
from json import load
from logging.handlers import TimedRotatingFileHandler
from typing import List

from database import Database
from dtos import SlackConnectorConfigDTO, HealthCheckConfigDTO, HealthResultDTO
from health_check import HealthCheck
from slack_connector import SlackConnector
import to_checks_types as types

config_file_name = "configuration.json"
logs_file_name = "health_check_logs"
current_path = pathlib.Path(__file__).parent.resolve()


class Main:
    def __init__(
        self,
        *,
        repository,
        health_check: HealthCheck,
        slack_connector: SlackConnector,
    ):
        self.repository = repository
        self.slack_connector = slack_connector
        self.health_check = health_check

    def execute(self, *, to_checks: List[types.ToChecksTypedDict]):
        new_unhealthy = []
        back_to_healthy = []
        still_unhealthy = []
        current_unhealthy_urls = self.repository.current_unhealthy_urls
        for to_check in to_checks:
            health_check_dto = self.health_check.execute(
                params=to_check["params"],
                url_base=to_check["url_base"],
                current_unhealthy_urls=current_unhealthy_urls,
            )
            self.slack_connector.send_health_check_report(
                health_check_dto=health_check_dto
            )
            new_unhealthy.extend(health_check_dto.unhealthy)
            still_unhealthy.extend(health_check_dto.still_unhealthy)
            back_to_healthy.extend(health_check_dto.back_to_healthy)

        if not any([new_unhealthy, still_unhealthy]):
            self.slack_connector.send_if_there_no_unhealthy()

        self.repository.add_unhealthy(new_unhealthy=new_unhealthy)
        self.repository.update_still_unhealthy_last_send(
            still_unhealthy=still_unhealthy
        )
        self.repository.remove_unhealthy(back_to_healthy=back_to_healthy)

    def test(self):
        self.slack_connector.hello_message()


if __name__ == "__main__":
    try:
        param = sys.argv[1]
    except IndexError:
        param = ""

    logging.basicConfig(
        filename=f"{current_path}/{logs_file_name}",
        encoding="utf-8",
        level=logging.INFO,
        handlers=[
            TimedRotatingFileHandler(
                filename=f"{current_path}/{logs_file_name}", when="M", interval=1
            )
        ],
    )

    repository = Database(current_path=current_path)

    with open(f"{current_path}/{config_file_name}", "r") as config_file:
        config = load(config_file)

    try:
        to_checks: List[types.ToChecksTypedDict] = config["to_checks"]
    except KeyError:
        raise Exception("Missing 'to_check' list. Check configuration_example.")

    try:
        slack_webhook_url = config["slack_webhook_url"]
    except KeyError:
        raise Exception("Missing 'slack_webhook_url'. Check configuration_example.")

    slack_connector_config = SlackConnectorConfigDTO(
        **config.get("slack_connector_config", {})
    )
    health_check_config = HealthCheckConfigDTO(**config.get("health_check_config", {}))
    slack_connector = SlackConnector(
        repository=repository,
        slack_webhook_url=slack_webhook_url,
        slack_connector_config=slack_connector_config,
    )
    health_check = HealthCheck(
        health_check_config=health_check_config,
    )

    main = Main(
        repository=repository,
        slack_connector=slack_connector,
        health_check=health_check,
    )

    if param == "--test":
        main.test()
    else:
        main.execute(to_checks=to_checks)

    repository.commit()
