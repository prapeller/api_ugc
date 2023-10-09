from enum import Enum


class LikeValueEnum(int, Enum):
    like = 1
    dislike = -1

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)


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


class MethodsEnum(str, Enum):
    get = 'get'
    post = 'post'
    put = 'put'
    delete = 'delete'
