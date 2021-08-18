"""Autorunner module"""
import logging

from .local import JsonFileController

__all__ = ["JsonFileController"]


logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
