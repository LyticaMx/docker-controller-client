"""Controllers working with local JSON config"""

import json
import logging

from .base import BaseController

logger = logging.getLogger(__name__)


class JsonFileController(BaseController):
    """Control containers based on a JSON file"""

    path = None

    def __init__(self, path, **kargs):
        """Initialize controller"""
        self.path = path
        super().__init__(**kargs)

    def get_new_docker_config(self):
        """Get json config from server"""
        with open(self.path, "r") as myfile:
            data = myfile.read()
        config = json.loads(data)
        logger.debug(f"Received config: {config}")
        self.docker_config = config
        return self.docker_config
