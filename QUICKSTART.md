# 🚀 Quick Start Guide

Get the E-Commerce Kubernetes application running in **5 minutes**!

## Choose Your Path

### 🎯 Path 1: Local Development (Fastest - Docker Compose)

Perfect for: Testing the application locally without Kubernetes

```bash
# 1. Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# 2. Start all services
docker-compose up -d

# 3. Access the application
open http://localhost:3000
```

**That's it!** The application is running with all three services (Frontend, Backend, Database).

---

### 💻 Path 2: Development with Minikube (Recommended for Learning)

Perfect for: Learning Kubernetes on your laptop

**Prerequisites**: Docker, Minikube, kubectl

```bash
# 1. Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# 2. Run the automated setup script
./scripts/setup-minikube.sh

# 3. The script will provide you with the access URL
# Typically: http://<minikube-ip>:30080 or http://ecommerce.local
```

**What the script does:**
- Starts Minikube with optimal settings
- Enables ingress and metrics-server
- Builds Docker images
- Deploys all Kubernetes resources
- Provides access instructions

**Manual steps if you prefer:**

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Enable addons
minikube addons enable ingress
minikube addons enable metrics-server

# Build images in Minikube's Docker
eval $(minikube docker-env)
docker build -t backend:latest ./apps/backend
docker build -t frontend:latest ./apps/frontend

# Deploy
kubectl apply -f k8s/dev/

# Wait for pods to be ready
kubectl wait --for=condition=ready pod --all -n ecommerce-dev --timeout=300s

# Access the application
minikube service frontend-service -n ecommerce-dev
```

---

### 🏢 Path 3: Multi-Node with Kind (Production-like)

Perfect for: Testing with multiple nodes locally

**Prerequisites**: Docker, Kind, kubectl

```bash
# 1. Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# 2. Create and deploy to Kind cluster
./scripts/setup-kind.sh ecommerce-cluster dev

# 3. Access the application
open http://localhost:30080
```

---

### ☁️ Path 4: Production on Real Cluster (Kubeadm/Cloud)

Perfect for: Production deployments

**Prerequisites**: Kubernetes cluster (kubeadm/EKS/GKE/AKS), kubectl

```bash
# 1. Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# 2. Build and push images to your registry
docker build -t your-registry/backend:v1.0.0 ./apps/backend
docker build -t your-registry/frontend:v1.0.0 ./apps/frontend
docker push your-registry/backend:v1.0.0
docker push your-registry/frontend:v1.0.0

# 3. Update image references in k8s/prod/ manifests
# Edit k8s/prod/backend-deployment.yaml and k8s/prod/frontend-deployment.yaml
# Replace 'backend:v1.0.0' with 'your-registry/backend:v1.0.0'

# 4. Deploy to production
kubectl apply -f k8s/prod/

# 5. Wait for all pods
kubectl wait --for=condition=ready pod --all -n ecommerce-prod --timeout=600s

# 6. Get ingress IP
kubectl get ingress -n ecommerce-prod
```

---

## 🔄 Add GitOps with ArgoCD

Want continuous deployment? Add ArgoCD!

```bash
# Install ArgoCD
./scripts/setup-argocd.sh

# Access ArgoCD UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Open browser: https://localhost:8080
# Login with username: admin and the password from above
```

---

## 📊 Add Monitoring

Want to monitor your applications?

```bash
# Install Prometheus and Grafana
./scripts/setup-monitoring.sh

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80

# Open browser: http://localhost:3001
# Login: admin / admin
```

---

## 🎛️ Using Makefile Commands

For convenience, use the Makefile:

```bash
# Docker Compose
make docker-compose-up        # Start with Docker Compose
make docker-compose-down      # Stop Docker Compose

# Minikube
make minikube-start          # Setup and deploy to Minikube
make minikube-stop           # Stop Minikube
make minikube-delete         # Delete Minikube cluster

# Kind
make kind-create             # Create Kind cluster
make kind-deploy             # Deploy to Kind
make kind-delete             # Delete Kind cluster

# Monitoring
make monitoring-install      # Install Prometheus/Grafana
make grafana-port-forward    # Access Grafana

# ArgoCD
make argocd-install          # Install ArgoCD
make argocd-password         # Get ArgoCD password
make argocd-port-forward     # Access ArgoCD UI

# Utilities
make logs-frontend-dev       # View frontend logs
make logs-backend-dev        # View backend logs
make status-dev              # Show dev environment status
make help                    # Show all available commands
```

---

## 🔍 Verify Your Deployment

Once deployed, verify everything is working:

```bash
# Check all pods are running
kubectl get pods -n ecommerce-dev

# Check services
kubectl get svc -n ecommerce-dev

# Check ingress
kubectl get ingress -n ecommerce-dev

# Test the API
curl http://localhost:5000/health  # If port-forwarded
curl http://localhost:5000/api/products
```

---

## 🧹 Clean Up

When you're done:

```bash
# Docker Compose
docker-compose down -v

# Minikube
minikube delete

# Kind
kind delete cluster --name ecommerce-cluster

# Kubernetes namespace
kubectl delete namespace ecommerce-dev
kubectl delete namespace ecommerce-staging
kubectl delete namespace ecommerce-prod

# Or use Makefile
make clean-all
```

---

## 🆘 Troubleshooting

### Pods not starting?

```bash
# Check pod status
kubectl get pods -n ecommerce-dev

# Describe problematic pod
kubectl describe pod <pod-name> -n ecommerce-dev

# View logs
kubectl logs <pod-name> -n ecommerce-dev
```

### Can't access the application?

```bash
# For Minikube - use NodePort
minikube service frontend-service -n ecommerce-dev

# Or port-forward directly
kubectl port-forward -n ecommerce-dev svc/frontend-service 3000:3000
# Then access: http://localhost:3000
```

### Images not found?

```bash
# For Minikube - make sure you're using Minikube's Docker
eval $(minikube docker-env)
docker images  # Should see backend:latest and frontend:latest

# For Kind - load images into cluster
kind load docker-image backend:latest --name ecommerce-cluster
kind load docker-image frontend:latest --name ecommerce-cluster
```

---

## 📚 Next Steps

1. **Explore the Application**
   - Browse products
   - Check backend API at `/api/products`
   - View health endpoints

2. **Learn Kubernetes**
   - Modify deployments
   - Scale replicas
   - Update configurations

3. **Implement GitOps**
   - Install ArgoCD
   - Configure auto-sync
   - Make changes via Git

4. **Add Monitoring**
   - Install Prometheus/Grafana
   - Create custom dashboards
   - Set up alerts

5. **Move to Production**
   - Deploy to cloud (EKS/GKE/AKS)
   - Configure TLS certificates
   - Set up CI/CD pipelines

---

## 📖 Documentation

- **[README.md](README.md)** - Full project documentation
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Architecture details
- **[DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)** - Step-by-step deployment
- **[DIAGRAMS.md](docs/DIAGRAMS.md)** - Visual architecture

---

## 🤝 Need Help?

- Check the [Troubleshooting section](README.md#-troubleshooting) in README
- Review logs with `kubectl logs`
- Describe resources with `kubectl describe`
- Open an issue on GitHub

---

**Happy Deploying! 🚀**
