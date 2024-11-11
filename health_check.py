# health_check.py
import logging
from datetime import datetime
from typing import List

import requests
from requests.exceptions import ConnectTimeout, ReadTimeout

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
        current_unhealthy_urls: List[str],
    ) -> HealthCheckDTO:
        healthy = []
        unhealthy = []
        still_unhealthy = []
        back_to_healthy = []
        for param in params:
            health_result = self._health_check(
                url=url_base.format(param=param),
                param=param,
            )
            self._add_result_to_group(
                health_result=health_result,
                healthy=healthy,
                unhealthy=unhealthy,
                back_to_healthy=back_to_healthy,
                still_unhealthy=still_unhealthy,
                current_unhealthy_urls=current_unhealthy_urls,
            )
        return HealthCheckDTO(
            healthy=healthy,
            unhealthy=unhealthy,
            still_unhealthy=still_unhealthy,
            back_to_healthy=back_to_healthy,
        )

    def _add_result_to_group(
        self,
        health_result: HealthResultDTO,
        healthy: List[HealthResultDTO],
        unhealthy: List[HealthResultDTO],
        back_to_healthy: List[HealthResultDTO],
        still_unhealthy: List[HealthResultDTO],
        current_unhealthy_urls: List[str],
    ):
        is_current_unhealthy = health_result.url in current_unhealthy_urls
        is_healthy = health_result.is_healthy
        if is_healthy:
            {
                True: back_to_healthy,
                False: healthy,
            }[
                is_current_unhealthy
            ].append(health_result)
        elif not is_healthy:
            {
                True: still_unhealthy,
                False: unhealthy,
            }[
                is_current_unhealthy
            ].append(health_result)

    def _health_check(self, *, url: str, param: str) -> HealthResultDTO:
        try:
            response = requests.get(url=url, timeout=self.config.timeout)
            health_result = HealthResultDTO(
                is_healthy=response.status_code == self.HEALTHY_STATUS_CODE,
                status_code=response.status_code,
                param=param,
                url=url,
            )
        except (ConnectTimeout, ReadTimeout):
            health_result = HealthResultDTO(
                is_healthy=False,
                status_code=408,
                param=param,
                url=url,
            )
        logging.info(
            f"{datetime.now()} - url: {health_result.url} - param: {health_result.param} - status_code: {health_result.status_code} - is_healthy: {health_result.is_healthy}"
        )
        return health_result
