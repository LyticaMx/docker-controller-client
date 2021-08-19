"""Controllers working with local JSON config"""
import logging

import requests

from .base import BaseController

logger = logging.getLogger(__name__)


class RestApiController(BaseController):
    """Control containers based on a JSON file"""

    url = None
    headers = None

    def __init__(
        self,
        url,
        headers=None,
    ):
        """Initialize controller"""
        if url:
            self.url = url
        if headers:
            self.headers = headers
        super().__init__()

    def get_new_docker_config(self):
        """Get json config from server"""
        response = requests.get(self.url)
        config = response.json()
        # Stringify variables used for docker labels
        for container_config in config:
            container_config["id"] = str(container_config["id"])
            container_config["version"] = str(container_config["version"])
        logger.debug(f"Received config: {config}")
        self.docker_config = config
        return self.docker_config
