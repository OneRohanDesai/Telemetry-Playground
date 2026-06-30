#!/bin/bash
set -e

echo "Deleting Kind cluster..."

kind delete cluster -n telemetry-playground

echo ""
echo "Project stopped."
