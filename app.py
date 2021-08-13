"""Docker controller"""

import docker
import json
import os

class DockerController():
    """Docker controller"""

    def __init__(self):
        self.client = docker.from_env()
        self.config = self.pull_config()

    def pull_config(self):
        """Get json config from server"""
        path = os.path.abspath("config.json")
        with open(path, 'r') as myfile:
            data=myfile.read()
        self.config = json.loads(data)

    def get_running_containers(self):
        """Get all containers"""
        return self.client.containers.list()

    def update_all_containers(self):
        """Update all containers"""
        for container in self.get_all_containers():
            container.reload()
            if container.status == 'running':
                container.update()

if __name__ == '__main__':
    controller = DockerController()
    containers = controller.get_running_containers()
    for container in containers:
        print("=" * 100)
        print({
            "id": container.attrs["Id"],
            "config": container.attrs["Config"]
        })

