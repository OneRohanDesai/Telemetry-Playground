import asyncio
import random

from app.common.models import TelemetryPacket
from fastapi import FastAPI

app = FastAPI()


@app.post("/receive")
async def receive(packet: TelemetryPacket):

    await asyncio.sleep(random.uniform(0, 0.05))

    print(f"source={packet.source} mode={packet.traffic_mode} seq={packet.sequence}")


@app.get("/health")
def health():
    return {"status": "ok"}
