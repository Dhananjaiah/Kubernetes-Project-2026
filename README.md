# End-to-End Kubernetes E-Commerce Microservices Project

<div align="center">

![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-EF7B4D?style=for-the-badge&logo=argo&logoColor=white)
![Prometheus](https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white)
![Grafana](https://img.shields.io/badge/grafana-%23F46800.svg?style=for-the-badge&logo=grafana&logoColor=white)

A production-ready, cloud-native microservices application demonstrating Kubernetes deployment across development, staging, and production environments with GitOps.

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Quick Start](#-quick-start)
- [Deployment Environments](#-deployment-environments)
- [GitOps with ArgoCD](#-gitops-with-argocd)
- [Monitoring & Observability](#-monitoring--observability)
- [CI/CD Pipeline](#-cicd-pipeline)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)

## 🎯 Overview

This project demonstrates a **complete production-grade Kubernetes deployment** for a microservices-based e-commerce application with proper separation of concerns and real-world architecture patterns. It showcases:

- **True Microservices Architecture**: 
  - Product Service (catalog management)
  - Auth Service (JWT authentication)
  - Order Service (order processing)
  - Inventory Service (stock management)
  - API Gateway (centralized routing)
  - Frontend Service (user interface)
- **Production-Grade Code Structure**: Proper separation of routes, models, services, and config
- **Multi-Environment Deployment**: Development (Minikube), Staging, and Production
- **GitOps**: Automated deployment using ArgoCD
- **Observability**: Monitoring with Prometheus and Grafana
- **CI/CD**: Automated builds and deployments with GitHub Actions
- **Security**: JWT authentication, network policies, RBAC, and secrets management
- **High Availability**: HPA, pod anti-affinity, and rolling updates

## 🏗️ Architecture

### Application Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                   Ingress/Load Balancer                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
              ┌──────────▼──────────┐
              │     Frontend        │
              │  (Flask + HTML)     │
              │    Port: 3000       │
              └──────────┬──────────┘
                         │
              ┌──────────▼──────────┐
              │   API Gateway       │
              │  (Rate Limiting)    │
              │    Port: 5004       │
              └─┬───┬───┬───┬───────┘
                │   │   │   │
     ┌──────────┘   │   │   └──────────┐
     │              │   │              │
┌────▼─────┐  ┌────▼────┐  ┌─────▼────┐  ┌────▼─────┐
│ Product  │  │  Auth   │  │  Order   │  │Inventory │
│ Service  │  │ Service │  │ Service  │  │ Service  │
│   5000   │  │  5001   │  │  5002    │  │  5003    │
└────┬─────┘  └────┬────┘  └─────┬────┘  └────┬─────┘
     └─────────────┴─────────────┴────────────┘
                         │
              ┌──────────▼──────────┐
              │   PostgreSQL DB     │
              │    Port: 5432       │
              └─────────────────────┘
```

**See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation.**

### Deployment Progression

```
Development (Minikube)  →  Staging (Kind/Kubeadm)  →  Production (Kubeadm/Cloud)
    ↓                          ↓                          ↓
  Auto-sync                 Auto-sync                Manual approval
  (ArgoCD)                  (ArgoCD)                  (ArgoCD)
```

## 🛠️ Prerequisites

### Required Tools

- **Kubernetes Cluster**: Choose one based on your environment
  - [Minikube](https://minikube.sigs.k8s.io/docs/start/) - Development
  - [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/) - Development/Staging
  - [kubeadm](https://kubernetes.io/docs/setup/production-environment/tools/kubeadm/) - Production
- [kubectl](https://kubernetes.io/docs/tasks/tools/) (v1.25+)
- [Docker](https://docs.docker.com/get-docker/) (v20.10+)
- [Helm](https://helm.sh/docs/intro/install/) (v3.10+) - For monitoring stack
- [Git](https://git-scm.com/downloads)

### System Requirements

**Development (Minikube):**
- 4 CPU cores
- 8GB RAM
- 20GB free disk space

**Staging/Production:**
- 8+ CPU cores
- 16GB+ RAM
- 50GB+ free disk space

## 🚀 Quick Start

### Option 1: Development with Minikube (Recommended for Learning)

```bash
# Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# Run the automated setup script
./scripts/setup-minikube.sh
```

The script will:
- Start Minikube with required resources
- Enable necessary addons (ingress, metrics-server)
- Build Docker images
- Deploy all services
- Configure ingress

**Access the application:**
```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
<MINIKUBE_IP> ecommerce.local

# Open in browser
http://ecommerce.local
```

### Option 2: Multi-Node Setup with Kind

```bash
# Create a Kind cluster with 3 nodes
./scripts/setup-kind.sh ecommerce-cluster dev

# Access via NodePort
http://localhost:30080
```

### Option 3: Manual Docker Compose (Local Development)

```bash
# Start all services locally
docker-compose up -d

# Access the application
http://localhost:3000
```

## 🌍 Deployment Environments

### Development Environment

**Target**: Minikube or Kind
**Features**:
- Minimal resource requirements
- Single replica for each service
- NodePort services for easy access
- Auto-sync with ArgoCD

**Deploy manually:**
```bash
# Apply all development manifests
kubectl apply -f k8s/dev/
```

### Staging Environment

**Target**: Kind multi-node or kubeadm cluster
**Features**:
- 2 replicas per service
- Resource limits enforced
- Production-like configuration
- Auto-sync with ArgoCD

**Deploy manually:**
```bash
# Apply all staging manifests
kubectl apply -f k8s/staging/
```

### Production Environment

**Target**: kubeadm or managed Kubernetes (EKS, GKE, AKS)
**Features**:
- 3+ replicas with pod anti-affinity
- Horizontal Pod Autoscaler (HPA)
- StatefulSet for database
- Network policies and RBAC
- TLS/SSL termination
- Manual sync in ArgoCD (requires approval)

**Deploy manually:**
```bash
# Apply all production manifests
kubectl apply -f k8s/prod/
```

## 🔄 GitOps with ArgoCD

### Installation

```bash
# Install and configure ArgoCD
./scripts/setup-argocd.sh
```

### Access ArgoCD UI

```bash
# Port forward to access UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get admin password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Open browser: https://localhost:8080
# Username: admin
# Password: <from above command>
```

### ArgoCD Applications

Three applications are pre-configured:

1. **ecommerce-dev**: Auto-syncs from `k8s/dev/`
2. **ecommerce-staging**: Auto-syncs from `k8s/staging/`
3. **ecommerce-prod**: Manual sync from `k8s/prod/` (requires approval)

### Manual Sync Production

```bash
# Using kubectl
kubectl -n argocd patch application ecommerce-prod -p '{"operation":{"sync":{}}}' --type merge

# Or use ArgoCD CLI
argocd app sync ecommerce-prod
```

## 📊 Monitoring & Observability

### Install Monitoring Stack

```bash
# Install Prometheus, Grafana, and AlertManager
./scripts/setup-monitoring.sh
```

### Access Monitoring Tools

**Grafana:**
```bash
kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80
# Open: http://localhost:3001
# Username: admin, Password: admin
```

**Prometheus:**
```bash
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090
# Open: http://localhost:9090
```

### Pre-configured Dashboards

Grafana comes with pre-installed dashboards for:
- Kubernetes cluster overview
- Node metrics
- Pod metrics
- Application health

### Application Metrics

Each service exposes a `/health` endpoint for health checks and monitoring.

## 🔧 CI/CD Pipeline

### GitHub Actions Workflows

The project includes automated CI/CD:

**Build and Push** (`.github/workflows/build-and-push.yml`):
- Builds Docker images for frontend and backend
- Pushes to GitHub Container Registry (ghcr.io)
- Runs security scanning with Trivy
- Triggered on push to main/develop branches

**Setup:**
```bash
# Enable GitHub Container Registry in your repository
# Settings → Packages → Connect repository

# Images will be available at:
# ghcr.io/<username>/kubernetes-project-2026/frontend
# ghcr.io/<username>/kubernetes-project-2026/backend
```

## 📁 Project Structure

```
.
├── apps/                           # Microservices source code
│   ├── backend/                    # Product Service (Port 5000)
│   │   ├── app/
│   │   │   ├── api/               # API routes
│   │   │   ├── models/            # Data models
│   │   │   ├── services/          # Business logic
│   │   │   ├── middleware/        # Logging, errors
│   │   │   └── config/            # Configuration
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   └── wsgi.py
│   ├── auth-service/               # Auth Service (Port 5001)
│   │   ├── app/
│   │   │   ├── api/               # Auth endpoints
│   │   │   ├── models/            # User model
│   │   │   ├── services/          # Auth logic + JWT
│   │   │   └── config/
│   │   └── ...
│   ├── order-service/              # Order Service (Port 5002)
│   │   ├── app/
│   │   │   ├── api/               # Order endpoints
│   │   │   ├── models/            # Order models
│   │   │   ├── services/          # Order logic
│   │   │   └── config/
│   │   └── ...
│   ├── inventory-service/          # Inventory Service (Port 5003)
│   │   ├── app/
│   │   │   ├── api/               # Inventory endpoints
│   │   │   ├── models/            # Inventory model
│   │   │   ├── services/          # Stock management
│   │   │   └── config/
│   │   └── ...
│   ├── api-gateway/                # API Gateway (Port 5004)
│   │   ├── app/
│   │   │   ├── routes/            # Routing logic
│   │   │   ├── middleware/        # Rate limiting, CORS
│   │   │   └── config/
│   │   └── ...
│   ├── frontend/                   # Frontend UI (Port 3000)
│   │   ├── app/
│   │   │   ├── api/               # View routes
│   │   │   ├── templates/         # HTML templates
│   │   │   ├── static/            # CSS, JavaScript
│   │   │   └── config/
│   │   └── ...
│   └── database/                   # Database initialization
│       └── init.sql
├── k8s/                           # Kubernetes manifests
│   ├── dev/                       # Development environment
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secret.yaml
│   │   ├── postgres-deployment.yaml
│   │   ├── backend-deployment.yaml
│   │   ├── frontend-deployment.yaml
│   │   └── ingress.yaml
│   ├── staging/                   # Staging environment
│   │   └── ...
│   └── prod/                      # Production environment
│       ├── namespace.yaml
│       ├── configmap.yaml
│       ├── postgres-statefulset.yaml
│       ├── backend-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── ingress.yaml
│       ├── network-policy.yaml
│       └── rbac.yaml
├── argocd/                        # ArgoCD configurations
│   ├── install.yaml
│   ├── dev/
│   │   └── application.yaml
│   ├── staging/
│   │   └── application.yaml
│   └── prod/
│       └── application.yaml
├── monitoring/                    # Monitoring configurations
│   ├── prometheus-values.yaml
│   └── servicemonitor.yaml
├── scripts/                       # Automation scripts
│   ├── setup-minikube.sh
│   ├── setup-kind.sh
│   ├── setup-argocd.sh
│   └── setup-monitoring.sh
├── .github/
│   └── workflows/
│       └── build-and-push.yml     # CI/CD pipeline
├── docker-compose.yml             # Local development
└── README.md                      # This file
```

## 🐛 Troubleshooting

### Common Issues

**1. Minikube won't start**
```bash
# Delete and recreate
minikube delete
minikube start --cpus=4 --memory=8192

# Check system resources
docker system df
```

**2. Images not found in Minikube**
```bash
# Set Docker environment to Minikube
eval $(minikube docker-env)

# Rebuild images
docker build -t backend:latest ./apps/backend
docker build -t frontend:latest ./apps/frontend
```

**3. Pods stuck in Pending state**
```bash
# Check events
kubectl get events -n ecommerce-dev --sort-by='.lastTimestamp'

# Check pod details
kubectl describe pod <pod-name> -n ecommerce-dev

# Check node resources
kubectl top nodes
```

**4. Can't access application**
```bash
# Check service endpoints
kubectl get endpoints -n ecommerce-dev

# Check ingress
kubectl get ingress -n ecommerce-dev

# Port forward directly to service
kubectl port-forward -n ecommerce-dev svc/frontend-service 3000:3000
```

**5. Database connection issues**
```bash
# Check PostgreSQL logs
kubectl logs -f deployment/postgres -n ecommerce-dev

# Test database connectivity from backend
kubectl exec -it deployment/backend -n ecommerce-dev -- nc -zv postgres-service 5432
```

### Logs and Debugging

```bash
# View all pods in namespace
kubectl get pods -n ecommerce-dev

# Get pod logs
kubectl logs -f deployment/frontend -n ecommerce-dev
kubectl logs -f deployment/backend -n ecommerce-dev

# Get previous pod logs (if crashed)
kubectl logs deployment/backend -n ecommerce-dev --previous

# Execute commands in pod
kubectl exec -it deployment/backend -n ecommerce-dev -- /bin/sh

# Describe resources
kubectl describe deployment backend -n ecommerce-dev
```

### Clean Up

**Remove specific environment:**
```bash
# Development
kubectl delete namespace ecommerce-dev

# Staging
kubectl delete namespace ecommerce-staging

# Production
kubectl delete namespace ecommerce-prod
```

**Remove ArgoCD:**
```bash
kubectl delete namespace argocd
```

**Remove monitoring:**
```bash
helm uninstall prometheus -n monitoring
kubectl delete namespace monitoring
```

**Delete Minikube cluster:**
```bash
minikube delete
```

**Delete Kind cluster:**
```bash
kind delete cluster --name ecommerce-cluster
```

## 🎓 Learning Path

### For Beginners (Development Environment)

1. **Start with Docker Compose**
   - Understand the application architecture
   - Run `docker-compose up` and explore

2. **Move to Minikube**
   - Deploy to single-node Kubernetes
   - Learn about Pods, Services, Deployments
   - Use `kubectl` commands

3. **Add GitOps**
   - Install ArgoCD
   - Watch automatic syncing

### For Intermediate (Staging Environment)

1. **Multi-node with Kind**
   - Create 3-node cluster
   - Deploy with replicas
   - Test load balancing

2. **Add Monitoring**
   - Install Prometheus/Grafana
   - Create custom dashboards
   - Set up alerts

3. **Implement CI/CD**
   - Set up GitHub Actions
   - Build and push images
   - Auto-deploy to staging

### For Advanced (Production Environment)

1. **Production Cluster**
   - Set up with kubeadm
   - Configure HA control plane
   - Implement backup/restore

2. **Security Hardening**
   - Network policies
   - Pod security policies
   - Secret management (Vault)

3. **Advanced Features**
   - Service mesh (Istio)
   - Advanced monitoring
   - Chaos engineering

## 📚 Additional Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [ArgoCD Documentation](https://argo-cd.readthedocs.io/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Docker Documentation](https://docs.docker.com/)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👏 Acknowledgments

- Kubernetes community for excellent documentation
- ArgoCD team for GitOps tooling
- Prometheus and Grafana teams for monitoring solutions

---

<div align="center">

**Built with ❤️ for learning Kubernetes and Cloud Native technologies**

[⬆ Back to Top](#end-to-end-kubernetes-e-commerce-microservices-project)

</div>
