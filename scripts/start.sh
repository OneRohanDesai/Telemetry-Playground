#!/bin/bash

set -euo pipefail

CLUSTER_NAME="telemetry-playground"
ARGOCD_NAMESPACE="argocd"
APPLICATION_NAME="telemetry-playground"

echo "========================================"
echo "Starting Telemetry Playground"
echo "========================================"

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
    --timeout=180s

echo
echo "Installing ArgoCD..."

kubectl create namespace "${ARGOCD_NAMESPACE}" \
    --dry-run=client -o yaml | kubectl apply -f -

kubectl apply \
    --server-side \
    -n "${ARGOCD_NAMESPACE}" \
    -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo
echo "Waiting for ArgoCD server..."

kubectl rollout status \
    deployment/argocd-server \
    -n "${ARGOCD_NAMESPACE}" \
    --timeout=300s

echo
echo "Building Docker images..."

docker build -t telemetry-generator:latest -f docker/generator/Dockerfile .
docker build -t telemetry-receiver:latest -f docker/receiver/Dockerfile .
docker build -t telemetry-dashboard:latest -f docker/dashboard/Dockerfile .
docker build -t telemetry-nginx:latest -f docker/nginx/Dockerfile .

echo
echo "Loading images into Kind..."

kind load docker-image telemetry-generator:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-receiver:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-dashboard:latest --name "${CLUSTER_NAME}"
kind load docker-image telemetry-nginx:latest --name "${CLUSTER_NAME}"

echo
echo "Creating ArgoCD Application..."

kubectl wait \
  --for=condition=Established \
  crd/applications.argoproj.io \
  --timeout=60s

kubectl apply -f argocd/application.yaml
kubectl apply -f argocd/observability-application.yaml

echo
echo "Waiting for ArgoCD to synchronize..."

kubectl wait \
  --for=create \
  application/"${APPLICATION_NAME}" \
  -n "${ARGOCD_NAMESPACE}" \
  --timeout=180s

echo
echo "ArgoCD is running at port 8080"

kubectl port-forward svc/argocd-server \
-n argocd \
8080:443 &&

kubectl \
-n argocd \
get secret argocd-initial-admin-secret \
-o jsonpath="{.data.password}" \
| base64 -d

echo
echo "========================================"
echo "Telemetry Playground is Ready"
echo "========================================"

echo
kubectl get pods -n telemetry

echo
kubectl get ingress -n telemetry

echo
echo "Dashboard:"
echo "http://telemetry.local"
