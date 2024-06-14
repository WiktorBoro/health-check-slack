# slack_connector.py
from datetime import datetime
from typing import List

from slack_sdk.webhook import WebhookClient
import logging

from dtos import SlackConnectorConfigDTO, HealthCheckDTO, HealthResultDTO


class SlackConnector:
    DEFAULT_HELLO_MESSAGE = ":wave: Hi, we are connected! Let's go! :tada:"
    DEFAULT_HEALTHY_MESSAGE = "URL {url} is fine :heart:"
    DEFAULT_UNHEALTHY_MESSAGE = (
        "URL {url} is dead :firecracker::skull_and_crossbones::firecracker:"
    )
    DEFAULT_NO_UNHEALTHY_MESSAGE = "Everything is fine :green_heart:"

    def __init__(
        self,
        slack_webhook_url: str,
        slack_connector_config: SlackConnectorConfigDTO,
    ):
        self.connector = WebhookClient(url=slack_webhook_url)
        self.config = slack_connector_config

    def send_health_check_report(self, health_check_dto: HealthCheckDTO):
        if self.config.send_healthy:
            self._send_results(health_results=health_check_dto.healthy)
        if self.config.send_unhealthy:
            self._send_results(health_results=health_check_dto.unhealthy)

    def hello_message(self):
        self._send(text=self.config.hello_message or self.DEFAULT_HELLO_MESSAGE)

    def send_if_there_no_unhealthy(self):
        if self.config.send_if_there_no_unhealthy:
            self._send(
                text=self.config.no_unhealthy_message
                or self.DEFAULT_NO_UNHEALTHY_MESSAGE
            )

    def _send_results(self, *, health_results: List[HealthResultDTO]):
        for health_result in health_results:
            text = {
                True: self.DEFAULT_HEALTHY_MESSAGE or self.config.healthy_message,
                False: self.DEFAULT_UNHEALTHY_MESSAGE or self.config.unhealthy_message,
            }[health_result.is_healthy].format(
                url=health_result.url,
                param=health_result.param,
                status_code=health_result.status_code,
                is_healthy=health_result.is_healthy,
            )
            self._send(text=text)

    def _send(self, *, text: str):
        try:
            response = self.connector.send(text=text)
            assert response.status_code == 200
            logging.info(f"{datetime.now()} - send to slack: success - text: {text}")
        except AssertionError:
            logging.info(f"{datetime.now()} - send to slack: failed - text: {text}")
