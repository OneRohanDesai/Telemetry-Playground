import redis
import json

r = redis.Redis(
    host="redis",
    port=6379,
    decode_responses=True
)


def get_config(generator_name):
    data = r.get(generator_name)

    if data is None:
        default = {
            "mode": "stable",
            "rate": 10,
            "malformed": False,
            "latency_ms": 0
        }

        r.set(generator_name, json.dumps(default))
        return default

    return json.loads(data)


def set_config(generator_name, config):
    r.set(generator_name, json.dumps(config))
