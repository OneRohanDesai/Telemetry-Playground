# Telemetry Playground

A synthetic distributed system designed for learning and demonstrating **DevOps, SRE, Observability and DevSecOps** practices.

The application itself is intentionally simple. Its purpose is not business logic, but generating realistic traffic, logs, metrics, traces and failure scenarios that can be used to experiment with Kubernetes, GitOps, chaos engineering and platform tooling.

---

## Overview

Telemetry Playground consists of multiple lightweight services continuously exchanging telemetry packets.

Services can generate:

* Stable traffic
* Bursty traffic
* Fluctuating traffic
* Malformed payloads
* Artificial latency
* Partial failures

All packets are validated and discarded. No business data is stored.

This creates a continuously active environment for:

* Monitoring
* Alerting
* Scaling
* Chaos engineering
* Security testing
* GitOps workflows
* Infrastructure experiments

---

## Architecture

```
Dashboard
    ↓
Redis

Generator Pods
    ↓
Nginx
    ↓
Receiver Pods

Metrics ───► Prometheus
Logs ──────► Loki
Traces ────► Tempo
                ↓
             Grafana

GitHub Actions
        ↓
     ArgoCD
        ↓
   Kubernetes
```

---

## Current Stack

### Application

* Python
* Redis
* Nginx

### Containers and Orchestration

* Docker
* Kubernetes
* kubectl
* Helm
* Kustomize

### CI/CD

* GitHub Actions
* ArgoCD

### Infrastructure

* Terraform
* Ansible

### Observability

* Prometheus
* Grafana
* Loki
* OpenTelemetry
* Tempo

---

## Future SRE Stack

* k6
* LitmusChaos
* KEDA
* Velero
* OpenCost
* Istio
* Keycloak
* Kafka
* MinIO

---

## Future DevSecOps Stack

* Vault
* Trivy
* Falco
* Kyverno
* OPA Gatekeeper
* Cosign
* Sigstore
* Semgrep
* Gitleaks
* OWASP ZAP

---

## Goals

This repository serves as a personal platform engineering playground for experimenting with:

* Kubernetes
* GitOps
* Infrastructure as Code
* Observability
* SRE practices
* Chaos engineering
* DevSecOps
* Platform automation

The application layer is intentionally kept small and mostly unchanged. The surrounding platform continuously evolves.

---

## Planned Capabilities

### Traffic Profiles

* Stable traffic
* Random traffic
* Burst traffic
* Error injection
* Latency injection
* Silent nodes

### Observability

* Metrics
* Logs
* Distributed traces
* Dashboards
* Alerts
* SLOs

### Reliability Engineering

* Horizontal scaling
* Load testing
* Chaos experiments
* Backup and recovery
* Cost monitoring

### Security

* Image scanning
* Runtime security
* Policy enforcement
* Secret management
* Supply-chain security

---

## Deployment Targets

### Local

* Docker
* Kind
* k3s

### Cloud (Ephemeral)

* AWS EKS
* Hetzner Cloud

Infrastructure is fully reproducible and can be created and destroyed on demand.

---

## Philosophy

> Keep the application simple. Make the platform interesting.

The objective of this project is not building software products, but building and operating reliable systems around them.

---

## Status

🚧 Under active development.
