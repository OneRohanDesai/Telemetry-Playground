import asyncio
import os
import random

import httpx
from fastapi import FastAPI, Response
from opentelemetry.trace import Status, StatusCode
from prometheus_client import (
    CONTENT_TYPE_LATEST,
    generate_latest,
)

from app.common.metrics import (
    ACTIVE_REQUESTS,
    MALFORMED_PACKETS,
    PACKETS_SENT,
)
from app.common.models import create_packet
from app.common.redis_client import get_config
from app.common.telemetry import setup_telemetry

app = FastAPI()
tracer = setup_telemetry("generator")

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

            with tracer.start_as_current_span("generate_packet") as span:
                packet = create_packet(
                    source=GENERATOR_NAME,
                    destination="receiver-service",
                    sequence=sequence,
                    mode=mode,
                )

                span.set_attribute("packet.id", packet.packet_id)
                span.set_attribute("packet.source", packet.source)
                span.set_attribute("packet.destination", packet.destination)
                span.set_attribute("packet.sequence", packet.sequence)
                span.set_attribute("packet.mode", packet.traffic_mode)
                span.set_attribute("packet.size_bytes", packet.size_bytes)
                span.set_attribute("generator.name", GENERATOR_NAME)

                span.add_event("packet_created")

                data = packet.model_dump()

            if config["malformed"]:
                data.pop(
                    "packet_id",
                    None,
                )

                MALFORMED_PACKETS.labels(generator=GENERATOR_NAME).inc()

            try:
                ACTIVE_REQUESTS.inc()

                with tracer.start_as_current_span("http_send") as span:
                    span.set_attribute(
                        "http.method",
                        "POST",
                    )

                    span.set_attribute(
                        "http.url",
                        "http://nginx/receive",
                    )

                    response = await client.post(
                        "http://nginx/receive",
                        json=data,
                    )

                    span.set_attribute(
                        "http.status_code",
                        response.status_code,
                    )

                    span.add_event("response_received")

                PACKETS_SENT.labels(generator=GENERATOR_NAME).inc()

            except Exception as e:
                span.record_exception(e)

                span.set_status(Status(StatusCode.ERROR))

                raise

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
