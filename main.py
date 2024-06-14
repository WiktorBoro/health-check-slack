# main.py
import logging
import pathlib
from json import load
from typing import List, Dict

from health_checker import HealthChecker
from slack_connector import SlackConnector

logging.basicConfig(filename="health_check_logs", encoding="utf-8", level=logging.INFO)

config_file_name = "configuration.json"

if __name__ == "__main__":
    with open(
        f"{pathlib.Path(__file__).parent.resolve()}/{config_file_name}", "r"
    ) as config_file:
        config = load(config_file)

    try:
        to_check: List[Dict[str, str]] = config["to_check"]
    except KeyError:
        raise Exception("Missing 'to_check' list. Check configuration_example.")

    try:
        slack_webhook_url = config["slack_webhook_url"]
    except KeyError:
        raise Exception("Missing 'slack_webhook_url'. Check configuration_example.")

    health_checker_config = {}
    if timeout := config.get("timeout"):
        health_checker_config.update({"timeout": timeout})

    health_checker = HealthChecker(**health_checker_config)
    SlackConnector()

    for url_base in []:
        health_results = health_checker.execute(url_base=url_base, url_params=[])
