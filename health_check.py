# health_check.py
import logging
from datetime import datetime
from typing import List

import requests
from requests import ConnectTimeout

from dtos import HealthResultDTO, HealthCheckDTO, HealthCheckConfigDTO


class HealthCheck:
    HEALTHY_STATUS_CODE = 200

    def __init__(
        self,
        health_check_config: HealthCheckConfigDTO,
    ):
        self.config = health_check_config

    def execute(
        self,
        url_base: str,
        params: List[str],
    ) -> HealthCheckDTO:
        healthy = []
        unhealthy = []
        for param in params:
            health_result = self._health_check(
                url=url_base.format(param=param), param=param
            )
            if health_result.is_healthy:
                healthy.append(health_result)
            elif not health_result.is_healthy:
                unhealthy.append(health_result)
            logging.info(
                f"{datetime.now()} - url: {health_result.url} - param: {health_result.param} - status_code: {health_result.status_code} - is_healthy: {health_result.is_healthy}"
            )
        return HealthCheckDTO(
            healthy=healthy,
            unhealthy=unhealthy,
        )

    def _health_check(self, *, url: str, param: str) -> HealthResultDTO:
        try:
            response = requests.get(url=url, timeout=self.config.timeout)
            health_result = HealthResultDTO(
                is_healthy=response.status_code == self.HEALTHY_STATUS_CODE,
                status_code=response.status_code,
                param=param,
                url=url,
            )
        except ConnectTimeout:
            health_result = HealthResultDTO(
                is_healthy=False,
                status_code=408,
                param=param,
                url=url,
            )
        return health_result
