# Terraform Infrastructure

This directory contains Terraform configurations for deploying the Telemetry Playground infrastructure to different cloud providers.

```
terraform/
├── aws-eks/
├── hetzner/
└── README.md
```

---

# Deployment Targets

| Provider      | Purpose            | Kubernetes |
| ------------- | ------------------ | ---------- |
| Hetzner Cloud | Single Ubuntu VM   | K3s        |
| AWS           | Managed Kubernetes | Amazon EKS |

Both deployments use the same GitOps workflow.

Terraform provisions infrastructure.

Ansible bootstraps servers (Hetzner only).

ArgoCD deploys the applications.

---

# Prerequisites

Install:

* Terraform
* kubectl
* Helm
* Git
* AWS CLI (AWS deployment)
* hcloud CLI (optional)
* Ansible (Hetzner deployment)

Verify:

```bash
terraform version
kubectl version --client
helm version
ansible --version
```

---

# Hetzner Cloud Deployment

## 1. Create an API Token

Hetzner Cloud Console

Project

Security

API Tokens

Create a Read/Write token.

---

## 2. Upload your SSH Key

Hetzner Cloud

Security

SSH Keys

Upload your public SSH key.

Example:

```
~/.ssh/id_ed25519.pub
```

Remember the SSH key name.

---

## 3. Configure terraform.tfvars

Create:

```
terraform/hetzner/terraform.tfvars
```

Example:

```hcl
hcloud_token = "YOUR_API_TOKEN"

ssh_key_name = "my-laptop"

server_name = "telemetry-playground"

location = "nbg1"

server_type = "cx22"
```

---

## 4. Initialize Terraform

```bash
cd terraform/hetzner

terraform init
```

---

## 5. Review the Plan

```bash
terraform plan
```

---

## 6. Create Infrastructure

```bash
terraform apply
```

Terraform creates:

* Ubuntu Server
* Public IPv4
* Public IPv6
* Firewall
* SSH access

---

## 7. SSH into the Server

```bash
ssh root@SERVER_IP
```

or

```bash
terraform output ssh
```

---

## 8. Bootstrap using Ansible

Return to project root.

Update:

```
ansible/inventory/hosts.ini
```

Example:

```ini
[k3s]
SERVER_IP ansible_user=root
```

Run:

```bash
ansible-playbook ansible/playbooks/bootstrap.yml
```

This installs:

* Docker
* K3s
* Helm
* ArgoCD

---

## 9. Configure Local kubeconfig

Copy the kubeconfig from the server.

```bash
scp root@SERVER_IP:/etc/rancher/k3s/k3s.yaml ~/.kube/telemetry-k3s.yaml
```

Replace the server IP inside the kubeconfig with the public IP.

Example:

```
https://SERVER_IP:6443
```

Export:

```bash
export KUBECONFIG=~/.kube/telemetry-k3s.yaml
```

Verify:

```bash
kubectl get nodes
```

---

## 10. Deploy Applications

```bash
kubectl apply -f argocd/application.yaml

kubectl apply -f argocd/observability-application.yaml
```

Wait for synchronization.

```bash
kubectl get applications -n argocd
```

---

# AWS EKS Deployment

## 1. Configure AWS Credentials

```bash
aws configure
```

Verify:

```bash
aws sts get-caller-identity
```

---

## 2. Configure terraform.tfvars

Create:

```
terraform/aws-eks/terraform.tfvars
```

Example:

```hcl
aws_region = "ap-south-1"

cluster_name = "telemetry-playground"

cluster_version = "1.33"

instance_type = "t3.medium"

desired_size = 2

min_size = 2

max_size = 4
```

---

## 3. Initialize Terraform

```bash
cd terraform/aws-eks

terraform init
```

---

## 4. Review the Plan

```bash
terraform plan
```

---

## 5. Create Infrastructure

```bash
terraform apply
```

Terraform provisions:

* VPC
* Public Subnets
* Private Subnets
* NAT Gateway
* Internet Gateway
* Amazon EKS Cluster
* Managed Node Group

---

## 6. Configure Local kubeconfig

```bash
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name telemetry-playground
```

Verify:

```bash
kubectl get nodes
```

---

## 7. Deploy Applications

```bash
kubectl apply -f argocd/application.yaml

kubectl apply -f argocd/observability-application.yaml
```

Wait for synchronization.

```bash
kubectl get applications -n argocd
```

---

# Verify Deployment

Nodes:

```bash
kubectl get nodes
```

Namespaces:

```bash
kubectl get ns
```

Pods:

```bash
kubectl get pods -A
```

Ingress:

```bash
kubectl get ingress -A
```

Applications:

```bash
kubectl get applications -n argocd
```

---

# Destroy Infrastructure

Hetzner:

```bash
cd terraform/hetzner

terraform destroy
```

AWS:

```bash
cd terraform/aws-eks

terraform destroy
```

---

# Deployment Architecture

```
Terraform
        │
        ▼
Cloud Infrastructure
        │
        ▼
Ansible (Hetzner only)
        │
        ▼
Docker
        │
        ▼
K3s / Amazon EKS
        │
        ▼
Helm
        │
        ▼
ArgoCD
        │
        ▼
Telemetry Playground
        │
        ├── NGINX
        ├── Generator
        ├── Receiver
        ├── Dashboard
        ├── Redis
        ├── Prometheus
        ├── Grafana
        ├── Loki
        ├── Promtail
        ├── Tempo
        └── OpenTelemetry Collector
```

---

# Workflow Summary

## Local Development

```
Kind
↓

ArgoCD

↓

Telemetry Playground
```

## Hetzner

```
Terraform

↓

Ubuntu VM

↓

Ansible

↓

K3s

↓

Helm

↓

ArgoCD

↓

Telemetry Playground
```

## AWS

```
Terraform

↓

Amazon EKS

↓

Helm

↓

ArgoCD

↓

Telemetry Playground
```
