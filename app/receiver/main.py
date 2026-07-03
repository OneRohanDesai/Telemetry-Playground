import asyncio
import os
import random
import time

from fastapi import FastAPI, Response
from opentelemetry.trace import Status, StatusCode
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.common.metrics import PACKETS_RECEIVED, REQUEST_LATENCY
from app.common.models import TelemetryPacket
from app.common.telemetry import setup_telemetry

app = FastAPI()
tracer = setup_telemetry("receiver")


@app.post("/receive")
async def receive(packet: TelemetryPacket):

    with tracer.start_as_current_span("process_packet") as span:
        span.set_attribute(
            "packet.id",
            packet.packet_id,
        )

        span.set_attribute(
            "packet.source",
            packet.source,
        )

        span.set_attribute(
            "packet.destination",
            packet.destination,
        )

        span.set_attribute(
            "packet.sequence",
            packet.sequence,
        )

        span.set_attribute(
            "packet.mode",
            packet.traffic_mode,
        )

        span.set_attribute(
            "packet.size_bytes",
            packet.size_bytes,
        )

        span.add_event("packet_received")

        try:
            with tracer.start_as_current_span("business_logic"):
                await asyncio.sleep(random.uniform(0, 0.05))

            latency_seconds = time.time() - packet.timestamp

            with tracer.start_as_current_span("metrics"):
                PACKETS_RECEIVED.labels(
                    receiver=os.getenv(
                        "HOSTNAME",
                        "receiver",
                    )
                ).inc()

                REQUEST_LATENCY.observe(latency_seconds)

            span.set_attribute(
                "packet.latency_seconds",
                latency_seconds,
            )

            span.add_event("metrics_recorded")

            print(
                f"source={packet.source} "
                f"mode={packet.traffic_mode} "
                f"seq={packet.sequence}"
            )

            span.add_event("response_sent")

            return {"ok": True}

        except Exception as e:
            span.record_exception(e)

            span.set_status(Status(StatusCode.ERROR))

            raise


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():

    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
