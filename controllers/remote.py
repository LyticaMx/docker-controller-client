"""Controllers working with local JSON config"""
import logging

import requests

from .base import BaseController

logger = logging.getLogger(__name__)


class RestApiController(BaseController):
    """Control containers based on a JSON file"""

    url = None
    headers = None
    device_id = None
    report_status = True

    def __init__(
        self,
        url,
        device_id,
        report_status=True,
        headers=None,
    ):
        """Initialize controller"""
        self.url = url
        self.device_id = device_id
        if not report_status:
            self.report_status = False
        if headers:
            self.headers = headers
        super().__init__()

    def get_new_docker_config(self):
        """Get json config from server"""
        response = requests.get(f"{self.url}/services/{self.device_id}")
        response.raise_for_status()
        config = response.json()
        # Stringify variables used for docker labels
        for container_config in config:
            container_config["id"] = str(container_config["id"])
            container_config["version"] = str(container_config["version"])
        logger.debug(f"Received config: {config}")
        self.docker_config = config
        return self.docker_config

    def report_services_status(self):
        """Send containers status to an API"""
        if not self.report_status:
            return
        current_config = self.get_running_docker_config()
        status = list(
            map(
                lambda x: {k: v for k, v in x.items() if k in ("id", "status")},
                current_config,
            )
        )
        logger.debug(f"Service status to be send: {status}")
        requests.post(f"{self.url}/services/update-status", json=status)
