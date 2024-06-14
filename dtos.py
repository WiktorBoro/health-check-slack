# dtos.py
from typing import List

from attr import frozen


@frozen(kw_only=True)
class SlackConnectorConfigDTO:
    send_healthy: bool = False
    send_unhealthy: bool = True
    send_if_there_no_unhealthy: bool = False
    hello_message: str = ""
    healthy_message: str = ""
    unhealthy_message: str = ""
    no_unhealthy_message: str = ""


@frozen(kw_only=True)
class HealthCheckConfigDTO:
    timeout: int = 3


@frozen(kw_only=True)
class HealthResultDTO:
    is_healthy: bool
    status_code: int
    url: str
    param: str


@frozen(kw_only=True)
class HealthCheckDTO:
    healthy: List[HealthResultDTO]
    unhealthy: List[HealthResultDTO]
