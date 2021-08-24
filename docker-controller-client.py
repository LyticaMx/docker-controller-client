"""Docker controller"""

import argparse
import logging
import time

from controllers import JsonFileController, RestApiController, logger


def init_argparse():
    """Gets CLI arguments"""
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Controls a docker  host with a JSON-based config.",
    )
    parser.add_argument("-d", "--debug", help="Show debug logs", action="store_true")
    parser.add_argument("-f", "--file", help="Retrieve config from file")
    parser.add_argument("-u", "--url", help="Host URL")
    parser.add_argument("-i", "--id", help="Device identifier for remote services")
    parser.add_argument(
        "-t",
        "--time-delay",
        help="Delay between updates in seconds",
        type=int,
        default=60,
    )
    return parser


if __name__ == "__main__":
    args = init_argparse().parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    if args.url and args.id:
        controller = RestApiController(args.url, args.id)
    if args.file:
        controller = JsonFileController(args.file)

    while True:
        try:
            logger.debug("Updating docker host")
            controller.update()
            controller.report_services_status()
        except Exception as error:
            logger.error(f"Updating docker host failed, error: {error}")
        time.sleep(args.time_delay)
