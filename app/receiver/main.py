import asyncio
import os
import random
import time

from app.common.metrics import PACKETS_RECEIVED, REQUEST_LATENCY
from app.common.models import TelemetryPacket
from fastapi import FastAPI, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

app = FastAPI()


@app.post("/receive")
async def receive(packet: TelemetryPacket):

    await asyncio.sleep(random.uniform(0, 0.05))

    PACKETS_RECEIVED.labels(
        receiver=os.getenv(
            "HOSTNAME",
            "receiver",
        )
    ).inc()

    latency_seconds = time.time() - packet.timestamp

    REQUEST_LATENCY.observe(latency_seconds)

    print(f"source={packet.source} mode={packet.traffic_mode} seq={packet.sequence}")

    return {"ok": True}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
