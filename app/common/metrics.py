from prometheus_client import Counter
from prometheus_client import Histogram
from prometheus_client import Gauge


PACKETS_SENT = Counter(
    "telemetry_packets_sent_total",
    "Total packets sent",
    ["generator"],
)

PACKETS_RECEIVED = Counter(
    "telemetry_packets_received_total",
    "Total packets received",
    ["receiver"],
)

MALFORMED_PACKETS = Counter(
    "telemetry_malformed_packets_total",
    "Malformed packets",
    ["generator"],
)

REQUEST_LATENCY = Histogram(
    "telemetry_request_latency_seconds",
    "Packet latency",
)

ACTIVE_REQUESTS = Gauge(
    "telemetry_active_requests",
    "Requests currently in progress",
)
