"""Docker controller"""

import argparse
import logging
import time

from controllers import JsonFileController

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def init_argparse():
    """Gets CLI arguments"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Controls a docker  host with a JSON-based config.",
    )
    parser.add_argument("-d", "--debug", help="Show debug logs", action="store_true")
    parser.add_argument("-f", "--file", help="Retrieve config from file", required=True)
    return parser


if __name__ == "__main__":
    args = init_argparse().parse_args()
    if args.debug:
        logging.getLogger(__name__).setLevel(logging.DEBUG)
    controller = JsonFileController(args.file)
    while True:
        try:
            logger.debug("Updating docker host")
            controller.update()
        except Exception as error:
            logger.error(f"Updating docker host failed, error: {error}")
        time.sleep(5)
