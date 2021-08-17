"""Docker controller"""

import docker
import json
import os
import time
import logging

import argparse

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - [%(levelname)s] - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def init_argparse():
    parser = argparse.ArgumentParser(
        usage="%(prog)s [OPTION]",
        description="Controls a docker  host with a JSON-based config.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        help="Show debug logs",
        action='store_true'
    )
    return parser


class DockerAutoRunner:
    """
    Docker auto runner

    Controls a docker  host with a JSON-based config
    """

    id_label = "autorunner.id"
    version_label = "autorunner.version"
    config = []
    running_config = []

    def __init__(self, initial_config=None):
        """Initialize autorunner and update current docker host"""
        self.client = docker.from_env()
        if initial_config:
            self.config = initial_config

    def _catch_docker_error(method):
        def catch_error(self, *args, **kwargs):
            try:
                method(self, *args, **kwargs)
            except docker.errors.APIClient as error:
                logger.error(f"Docker host error: {error}")

        return catch_error

    def get_new_config(self):
        """Get json config from server"""
        path = os.path.abspath("config.json")
        with open(path, "r") as myfile:
            data = myfile.read()
        config = json.loads(data)
        logger.debug(f"Received config: {config}")
        self.config = config
        return self.config

    def get_running_config(self):
        """Get config from runnning containers"""
        current_config = []
        containers = self.get_running_containers()
        for container in containers:
            current_config.append(
                {
                    "id": container.labels[self.id_label],
                    "version": container.labels[self.version_label],
                }
            )
        self.running_config = current_config
        return current_config

    def get_running_containers(self):
        """
        Get all containers created by the controller

        It filters containers by the autorunner labels
        """
        filters = {"label": [self.id_label, self.version_label]}
        return self.client.containers.list(all=True, filters=filters)

    def get_container_by_id(self, id):
        """Gets a docker container labelled with a given id"""
        filters = {"label": f"{self.id_label}={id}"}
        return self.client.containers.list(all=True, filters=filters)[0]

    def has_updated_version(self, id):
        """ "Checks if a container has new configuration version"""
        running_version = next(filter(lambda x: x["id"] == id, self.running_config))[
            "version"
        ]
        new_version = next(filter(lambda x: x["id"] == id, self.config))["version"]
        return running_version != new_version

    def get_classified_containers(self):
        """Classify container configuration comparing current vs new configs"""
        containers = {}
        new_config_ids = set([ct["id"] for ct in self.config])
        running_config_ids = set([ct["id"] for ct in self.running_config])
        containers["to_delete"] = list(running_config_ids - new_config_ids)
        containers["to_create"] = list(new_config_ids - running_config_ids)
        already_running = new_config_ids.intersection(running_config_ids)
        containers["to_update"] = []
        for id in already_running:
            if self.has_updated_version(id):
                containers["to_update"].append(id)
        return containers

    @_catch_docker_error
    def delete_containers(self, container_ids):
        """Stop and removes running containers"""
        for id in container_ids:
            container = self.get_container_by_id(id)
            if container.status == "running":
                container.stop()
            container.remove()
            logger.debug(f"Removed container with id `{id}`")

    @_catch_docker_error
    def create_containers(self, container_ids):
        """Create containers based on its new config"""
        for id in container_ids:
            config = next(filter(lambda x: x["id"] == id, self.config))
            labels = {self.id_label: id, self.version_label: config["version"]}
            self.client.containers.run(
                detach=True, **{**config["config"], **{"labels": labels}}
            )
            logger.debug(f"Created container with id `{id}`")

    def update_containers(self, container_ids):
        """Delete old container and creates it with its new config"""
        self.delete_containers(container_ids)
        self.create_containers(container_ids)

    def update(self):
        """Update containers based on the current configuration"""
        self.get_new_config()
        self.get_running_config()
        containers = self.get_classified_containers()
        self.delete_containers(containers["to_delete"])
        self.create_containers(containers["to_create"])
        self.update_containers(containers["to_update"])


if __name__ == "__main__":
    args = init_argparse().parse_args()
    if args.debug:
        logging.getLogger(__name__).setLevel(logging.DEBUG)

    controller = DockerAutoRunner()
    while True:
        try:
            logger.debug("Updating docker host")
            controller.update()
        except Exception as error:
            logger.error(f"Updateing docker host failed, error: {error}")
        time.sleep(5)
