import asyncio
import os
import random

import httpx
from app.common.metrics import (
    ACTIVE_REQUESTS,
    MALFORMED_PACKETS,
    PACKETS_SENT,
)
from app.common.models import create_packet
from app.common.redis_client import get_config
from fastapi import FastAPI, Response
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

app = FastAPI()

GENERATOR_NAME = os.getenv(
    "GENERATOR_NAME",
    "generator-1",
)

running = True


async def worker():

    sequence = 0

    async with httpx.AsyncClient() as client:
        while True:
            config = get_config(GENERATOR_NAME)

            mode = config["mode"]
            rate = config["rate"]

            if mode == "silent":
                await asyncio.sleep(1)
                continue

            if mode == "random":
                rate = random.randint(
                    1,
                    50,
                )

            if mode == "burst":
                rate = random.randint(
                    50,
                    200,
                )

            interval = 1.0 / max(
                rate,
                1,
            )

            packet = create_packet(
                source=GENERATOR_NAME,
                destination="receiver-service",
                sequence=sequence,
                mode=mode,
            )

            data = packet.model_dump()

            if config["malformed"]:
                data.pop(
                    "packet_id",
                    None,
                )

                MALFORMED_PACKETS.labels(generator=GENERATOR_NAME).inc()

            try:
                ACTIVE_REQUESTS.inc()

                await client.post(
                    "http://nginx/receive",
                    json=data,
                )

                PACKETS_SENT.labels(generator=GENERATOR_NAME).inc()

            except Exception:
                pass

            finally:
                try:
                    ACTIVE_REQUESTS.dec()
                except Exception:
                    pass

            sequence += 1

            latency_ms = config["latency_ms"]

            await asyncio.sleep(interval + latency_ms / 1000)


@app.on_event("startup")
async def startup():

    asyncio.create_task(worker())


@app.get("/health")
def health():

    return {"status": "ok"}


@app.get("/metrics")
def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
