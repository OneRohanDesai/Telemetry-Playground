import random
import time
import uuid

from pydantic import BaseModel


class TelemetryPacket(BaseModel):
    packet_id: str

    source: str
    destination: str

    timestamp: float
    sequence: int

    traffic_mode: str

    size_bytes: int

    environment: str
    region: str

    value: float


class GeneratorConfig(BaseModel):
    mode: str = "stable"
    rate: int = 10
    malformed: bool = False
    latency_ms: int = 0


def create_packet(
        source: str,
        destination: str,
        sequence: int,
        mode: str
):

    return TelemetryPacket(
        packet_id=str(uuid.uuid4()),

        source=source,
        destination=destination,

        timestamp=time.time(),

        sequence=sequence,

        traffic_mode=mode,

        size_bytes=random.randint(
            256,
            8192
        ),

        environment="dev",
        region="local",

        value=random.random() * 100
    )
