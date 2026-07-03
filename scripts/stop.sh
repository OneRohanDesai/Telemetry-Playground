#!/bin/bash

set -euo pipefail

CLUSTER_NAME="telemetry-playground"

echo "Stopping Telemetry Playground..."

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    kind delete cluster --name "${CLUSTER_NAME}"
else
    echo "Cluster not found."
fi

echo
echo "Telemetry Playground stopped."
