#!/usr/bin/env python
import logging
import pathlib
import sys
import types
from json import load
from typing import List

from dtos import SlackConnectorConfigDTO, HealthCheckConfigDTO
from health_check import HealthCheck
from slack_connector import SlackConnector

config_file_name = "configuration.json"
logs_file_name = "health_check_logs"
logging.basicConfig(filename=logs_file_name, encoding="utf-8", level=logging.INFO)


class Main:

    def __init__(
        self,
        *,
        slack_connector: SlackConnector,
        health_check: HealthCheck,
    ):
        self.slack_connector = slack_connector
        self.health_check = health_check

    def execute(self, *, to_checks: List[types.ToChecksTypedDict]):
        for to_check in to_checks:
            health_check_dto = self.health_check.execute(
                url_base=to_check["url_base"], params=to_check["params"]
            )
            self.slack_connector.send_health_check_report(
                health_check_dto=health_check_dto
            )

    def test(self):
        self.slack_connector.hello_message()


if __name__ == "__main__":
    try:
        param = sys.argv[1]
    except IndexError:
        param = ""

    with open(
        f"{pathlib.Path(__file__).parent.resolve()}/{config_file_name}", "r"
    ) as config_file:
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
        slack_webhook_url=slack_webhook_url,
        slack_connector_config=slack_connector_config,
    )
    health_check = HealthCheck(
        health_check_config=health_check_config,
    )

    main = Main(
        slack_connector=slack_connector,
        health_check=health_check,
    )

    if param == "--test":
        main.test()
    else:
        main.execute(to_checks=to_checks)
