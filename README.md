# Docker controller client

Python client to control Docker by calling an API

## Important notes

* Controller only affects the containers launched by itself (by using container Labels).
* Every time you `update` the controller it calls an API looking for a docker configuration.
* If the container was launched previously but is no longer in the configuration it will delete it.
* If the container has the same id and same version it'll not make any attemp to change it.
* If the container id doesn't exist it will create it.
* If the container id exists but has a different version it will update it.

## API example

```JSON
[
    {
        "id": "1",
        "version": "1",
        "config": {
            "name": "dockercontrollertest",
            "image": "nginx",
            "environment": {
                "HOLA": "crayola"
            }
        }
    }
]
```