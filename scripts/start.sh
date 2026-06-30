#!/bin/bash
set -e

echo "Creating Telemetry Playground cluster..."

kind create cluster --name telemetry-playground --config kind-config.yaml

echo "Labelling ingress node..."

kubectl label node telemetry-playground-control-plane ingress-ready=true --overwrite

echo "Installing ingress-nginx..."

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.11.2/deploy/static/provider/kind/deploy.yaml

kubectl rollout status deployment/ingress-nginx-controller \
  -n ingress-nginx \
  --timeout=180s

echo "Building images..."

docker build -t telemetry-generator:latest -f docker/generator/Dockerfile .
docker build -t telemetry-receiver:latest -f docker/receiver/Dockerfile .
docker build -t telemetry-dashboard:latest -f docker/dashboard/Dockerfile .
docker build -t telemetry-nginx:latest -f docker/nginx/Dockerfile .

echo "Loading images into Kind..."

kind load docker-image telemetry-generator:latest --name telemetry-playground
kind load docker-image telemetry-receiver:latest --name telemetry-playground
kind load docker-image telemetry-dashboard:latest --name telemetry-playground
kind load docker-image telemetry-nginx:latest --name telemetry-playground

echo "Deploying application..."

kubectl apply -k k8s/overlays/local

kubectl rollout status deployment/redis -n telemetry
kubectl rollout status deployment/nginx -n telemetry
kubectl rollout status deployment/receiver -n telemetry
kubectl rollout status deployment/generator -n telemetry
kubectl rollout status deployment/dashboard -n telemetry

echo
echo "Telemetry Playground is ready!"
echo "Dashboard : http://telemetry.local"
echo
echo "Pods:"
kubectl get pods -n telemetry
