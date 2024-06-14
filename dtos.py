# dtos.py
from typing import List

from attr import frozen


@frozen(kw_only=True)
class SlackConnectorConfigDTO:
    send_healthy: bool
    send_unhealthy: bool
    send_if_there_no_unhealthy: bool


@frozen(kw_only=True)
class HealthResultDTO:
    is_healthy: bool
    status_code: int
    url: str
    param: str


@frozen(kw_only=True)
class HealthCheckerDTO:
    healthy: List[HealthResultDTO]
    unhealthy: List[HealthResultDTO]
