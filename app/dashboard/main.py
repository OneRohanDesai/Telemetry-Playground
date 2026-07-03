import os

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.common.redis_client import set_config

app = FastAPI()


class ConfigRequest(BaseModel):
    mode: str
    rate: int
    malformed: bool
    latency_ms: int


@app.get("/")
def index():

    return FileResponse("app/dashboard/static/index.html")


@app.get("/generators")
def generators():

    count = int(os.getenv("GENERATOR_REPLICAS", "3"))

    return [f"generator-{i}" for i in range(1, count + 1)]


@app.post("/generator/{name}")
def update_generator(name: str, config: ConfigRequest):

    set_config(name, config.model_dump())

    print(f"updated {name}: {config.model_dump()}")

    return {"updated": name}


@app.get("/health")
def health():

    return {"status": "ok"}
