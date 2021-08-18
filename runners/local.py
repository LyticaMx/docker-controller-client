"""Autorunners controlled by local config"""

import json
import logging
import os

from .base import BaseRunner

logger = logging.getLogger(__name__)


class JsonFileRunner(BaseRunner):
    """Run containers based on a JSON file"""

    def get_new_config(self):
        """Get json config from server"""
        path = os.path.abspath("config.json")
        with open(path, "r") as myfile:
            data = myfile.read()
        config = json.loads(data)
        logger.debug(f"Received config: {config}")
        self.config = config
        return self.config
