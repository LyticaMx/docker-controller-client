"""Autorunner module"""
import logging

from .local import JsonFileController
from .remote import RestApiController

__all__ = ["JsonFileController", "RestApiController"]


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
