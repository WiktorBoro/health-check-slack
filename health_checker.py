# health_checker.py
from typing import List

import requests
from requests import ConnectTimeout

from dtos import HealthResultDTO, HealthCheckerDTO


class HealthChecker:
    HEALTHY_STATUS_CODE = 200

    def __init__(self, timeout: int = 3):
        self.timeout = timeout

    def execute(
        self,
        url_base: str,
        url_params: List[str],
    ) -> HealthCheckerDTO:
        healthy = []
        unhealthy = []
        for url_param in url_params:
            health_result = self._health_check(
                url=url_base.format(param=url_param), param=url_param
            )
            if health_result.is_healthy:
                healthy.append(health_result)
            elif not health_result.is_healthy:
                unhealthy.append(health_result)
        return HealthCheckerDTO(healthy=healthy, unhealthy=unhealthy)

    def _health_check(self, *, url: str, param: str) -> HealthResultDTO:
        try:
            response = requests.get(url=url, timeout=self.timeout)
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
