# Telemetry Playground Ansible

## Inventory

Edit:

```
inventory/dev.ini
```

## Run complete bootstrap

```bash
ansible-playbook playbooks/site.yml
```

## Individual stages

```bash
ansible-playbook playbooks/docker.yml
ansible-playbook playbooks/k3s.yml
ansible-playbook playbooks/helm.yml
ansible-playbook playbooks/argocd.yml
ansible-playbook playbooks/monitoring.yml
```
