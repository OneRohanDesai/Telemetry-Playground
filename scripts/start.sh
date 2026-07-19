#!/bin/bash

set -euo pipefail

CLUSTER_NAME="telemetry-playground"
ARGOCD_NAMESPACE="argocd"
TELEMETRY_NAMESPACE="telemetry"
OBSERVABILITY_NAMESPACE="observability"

echo "========================================"
echo "Starting Telemetry Playground"
echo "========================================"

echo
echo "Checking required tools..."

for cmd in kind kubectl docker; do
    command -v "$cmd" >/dev/null || {
        echo "$cmd is not installed."
        exit 1
    }
done

echo
echo "Checking for existing Kind cluster..."

if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Existing cluster found. Deleting..."
    kind delete cluster --name "${CLUSTER_NAME}"
fi

echo
echo "Creating Kind cluster..."

kind create cluster \
    --name "${CLUSTER_NAME}" \
    --config kind-config.yaml

echo
echo "Labelling ingress node..."

kubectl label node \
    "${CLUSTER_NAME}-control-plane" \
    ingress-ready=true \
    --overwrite

echo
echo "Installing ingress-nginx..."

kubectl apply -f \
https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.2/deploy/static/provider/kind/deploy.yaml

echo
echo "Waiting for ingress controller..."

kubectl rollout status \
    deployment/ingress-nginx-controller \
    -n ingress-nginx \
    --timeout=300s

kubectl wait \
    --namespace ingress-nginx \
    --for=condition=Ready \
    pod \
    -l app.kubernetes.io/component=controller \
    --timeout=300s

echo
echo "Installing ArgoCD..."

kubectl create namespace "${ARGOCD_NAMESPACE}" \
    --dry-run=client \
    -o yaml | kubectl apply -f -

kubectl apply \
    --server-side \
    -n "${ARGOCD_NAMESPACE}" \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo
echo "Waiting for ArgoCD..."

kubectl rollout status \
    deployment/argocd-server \
    -n "${ARGOCD_NAMESPACE}" \
    --timeout=300s

echo
echo "Building Docker images..."

docker build \
    -t telemetry-generator:latest \
    -f docker/generator/Dockerfile .

docker build \
    -t telemetry-receiver:latest \
    -f docker/receiver/Dockerfile .

docker build \
    -t telemetry-dashboard:latest \
    -f docker/dashboard/Dockerfile .

docker build \
    -t telemetry-nginx:latest \
    -f docker/nginx/Dockerfile .

echo
echo "Loading images into Kind..."

kind load docker-image telemetry-generator:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-receiver:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-dashboard:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-nginx:latest --name "${CLUSTER_NAME}"

echo
echo "Waiting for ArgoCD CRDs..."

kubectl wait \
    --for=condition=Established \
    crd/applications.argoproj.io \
    --timeout=120s

echo
echo "Creating ArgoCD Applications..."

kubectl apply -f argocd/application.yaml
kubectl apply -f argocd/observability-application.yaml

echo
echo "Waiting for Telemetry deployments..."

kubectl rollout status \
    deployment/dashboard \
    -n "${TELEMETRY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/generator \
    -n "${TELEMETRY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/receiver \
    -n "${TELEMETRY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/nginx \
    -n "${TELEMETRY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/redis \
    -n "${TELEMETRY_NAMESPACE}" \
    --timeout=300s

echo
echo "Waiting for Observability deployments..."

kubectl rollout status \
    deployment/prometheus \
    -n "${OBSERVABILITY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/grafana \
    -n "${OBSERVABILITY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/loki \
    -n "${OBSERVABILITY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/tempo \
    -n "${OBSERVABILITY_NAMESPACE}" \
    --timeout=300s

kubectl rollout status \
    deployment/otel-collector \
    -n "${OBSERVABILITY_NAMESPACE}" \
    --timeout=300s

echo
echo "Starting ArgoCD port-forward..."

pkill -f "kubectl port-forward.*8080:443" >/dev/null 2>&1 || true

kubectl port-forward \
    -n "${ARGOCD_NAMESPACE}" \
    svc/argocd-server \
    8080:443 \
    >/dev/null 2>&1 &

sleep 3

ARGO_PASSWORD=$(
kubectl \
    -n "${ARGOCD_NAMESPACE}" \
    get secret argocd-initial-admin-secret \
    -o jsonpath="{.data.password}" \
    | base64 -d
)

echo
echo "========================================"
echo "Telemetry Playground Ready"
echo "========================================"

echo
echo "Telemetry Namespace"
kubectl get pods -n "${TELEMETRY_NAMESPACE}"

echo
echo "Observability Namespace"
kubectl get pods -n "${OBSERVABILITY_NAMESPACE}"

echo
echo "Ingress"
kubectl get ingress -A

echo
echo "URLs"
echo
echo "Telemetry Dashboard : http://telemetry.local"
echo "Grafana            : http://grafana.local"
echo "Prometheus         : http://prometheus.local"
echo "ArgoCD             : https://localhost:8080"

echo
echo "ArgoCD Credentials"
echo "Username : admin"
echo "Password : ${ARGO_PASSWORD}"

echo
echo "========================================"
echo "Startup Complete"
echo "========================================"
