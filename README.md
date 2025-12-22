# Stock-watcher

## Quick Start / Usage Instructions

### Prerequisites
- Kubernetes cluster (v1.24+)
- kubectl configured to access the cluster
- Docker registry credentials for gitlab.control.lth.se:5050

### Deployment
1. Clone the repository
2. Create the namespace: `kubectl apply -f k8s/namespace.yaml`
3. Deploy all services: `kubectl apply -f k8s/`
4. Access the frontend at http://129.192.82.232:30080/
5. Generate load: `python workload-api/workload-api.py` at http://localhost:9000/ui but you need to run the python on 
the venv in workload-api folder.

### Testing Alerts
1. Open the frontend UI
2. Create an alert for stock price < $100
3. Run the workload generator
4. Check if notifications appear# Cloud Stock Watcher

Minimal demo project with components:
- `backend-api` : Flask API
- `stock-generator` : worker that emits stock data
- `alert-engine` : worker that evaluates alerts
- `frontend` : React SPA
- `workload-api` : Simple GUI to generate load
- `k8s` : Kubernetes manifests


### Project Report
You can read the full project report here:  
[Cloud Stock Watcher – Project Report (PDF)](Cloud_Stock_Watcher.pdf)

## Deployment and Teardown (Infrastructure-as-Code)

The application is deployed and removed using Ansible playbooks.

### Deploy the system

ansible-playbook ansible/deploy.yml

### Teardown the system
ansible-playbook ansible/teardown.yml

