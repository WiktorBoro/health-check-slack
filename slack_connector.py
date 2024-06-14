# slack_connector.py
from typing import List

from slack_sdk.webhook import WebhookClient
import logging

from dtos import SlackConnectorConfigDTO, HealthCheckerDTO, HealthResultDTO


class SlackConnector:
    DEFAULT_HELLO_MESSAGE = "Hi, we are connected! Let's go!"

    def __init__(
        self, slack_webhook_url: str, slack_connector_config: SlackConnectorConfigDTO
    ):
        self.connector = WebhookClient(url=slack_webhook_url)
        self.config = slack_connector_config

    def send_(self, health_checker_dto: HealthCheckerDTO):
        if self.config.send_healthy:
            self._send_results(health_results=health_checker_dto.healthy)
        if self.config.send_unhealthy:
            self._send_results(health_results=health_checker_dto.unhealthy)
        if self.config.send_if_there_no_unhealthy and not health_checker_dto.unhealthy:
            self._send()

    def _send_results(self, health_results: List[HealthResultDTO]):
        for health_result in health_results:
            self._send()

    def _send(self):
        response = self.connector.send(text="hello_message")
        logging.info("")

    def hello_message(self, *, hello_message: str = DEFAULT_HELLO_MESSAGE):
        try:
            response = self.connector.send(text=hello_message)
            assert response.status_code == 200
        except AssertionError:
            logging.info("")
