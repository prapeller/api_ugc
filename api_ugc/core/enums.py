from enum import Enum


class EnvEnum(str, Enum):
    local = 'local'
    docker_compose_local = 'docker-compose-local'
    prod = 'prod'

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class ResponseDetailEnum(str, Enum):
    ok = 'ok'
    unauthorized = 'Unauthorized for this action.'
