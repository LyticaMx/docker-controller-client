"""Docker controller"""

import docker
import json
import os
import time


class DockerAutoRunner:
    """
    Docker auto runner

    Control a docker  host with a JSON-based config
    """

    id_label = "autorunner.id"
    version_label = "autorunner.version"
    config = []
    running_config = []

    def __init__(self, initial_config=None):
        self.client = docker.from_env()
        if initial_config:
            self.config = initial_config
        self.update_containers()

    def update_config(self):
        """Get json config from server"""
        path = os.path.abspath("config.json")
        with open(path, "r") as myfile:
            data = myfile.read()
        self.config = json.loads(data)

    def set_running_config(self):
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

    def get_running_containers(self):
        """
        Get all containers created by the controller

        It filters containers by the autorunner labels
        """
        filters = {"label": [self.id_label, self.version_label]}
        return self.client.containers.list(all=True, filters=filters)

    def get_container_by_id(self, id):
        filters = {"label": id}
        return self.client.containers.list(filters=filters)[0]

    def delete_container(self, id):
        container = self.get_container_by_id(id)
        if container.status() == "running":
            container.stop()
        container.remove()

    def has_updated_version(self, id):
        running_version = next(filter(lambda x: x["id"] == id, self.running_config))[
            "version"
        ]
        new_version = next(filter(lambda x: x["id"] == id, self.config))["version"]
        return running_version != new_version

    def get_classified_containers(self):
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

    def delete_containers(self, containers_to_delete):
        """Compare new and current config and filters outdated config"""
        for container_config in containers_to_delete:
            self.delete_container(container_config["id"])

    def update_containers(self):
        """Update containers based on the current configuration"""
        self.update_config()
        self.set_running_config()
        containers = self.get_classified_containers()
        print(containers)


if __name__ == "__main__":
    controller = DockerAutoRunner()
    while True:
        time.sleep(3000)
        controller.update_containers()
