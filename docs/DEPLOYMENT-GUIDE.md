# Comprehensive Deployment Guide

## Table of Contents

1. [Development Environment (Minikube)](#development-environment-minikube)
2. [Staging Environment (Kind)](#staging-environment-kind)
3. [Production Environment (Kubeadm)](#production-environment-kubeadm)
4. [GitOps Deployment (ArgoCD)](#gitops-deployment-argocd)
5. [Manual Deployment Steps](#manual-deployment-steps)

---

## Development Environment (Minikube)

### Prerequisites

- Minikube installed
- kubectl installed
- Docker installed
- 4 CPU cores, 8GB RAM available

### Automated Setup

```bash
# Clone repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# Run setup script
./scripts/setup-minikube.sh
```

### Manual Setup

#### Step 1: Start Minikube

```bash
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

#### Step 2: Enable Addons

```bash
# Enable ingress controller
minikube addons enable ingress

# Enable metrics server for HPA
minikube addons enable metrics-server

# Optional: Enable dashboard
minikube addons enable dashboard
```

#### Step 3: Build Images

```bash
# Point Docker to Minikube's Docker daemon
eval $(minikube docker-env)

# Build backend image
docker build -t backend:latest ./apps/backend

# Build frontend image
docker build -t frontend:latest ./apps/frontend

# Verify images
docker images | grep -E 'backend|frontend'
```

#### Step 4: Deploy Application

```bash
# Create namespace
kubectl apply -f k8s/dev/namespace.yaml

# Deploy ConfigMaps and Secrets
kubectl apply -f k8s/dev/configmap.yaml
kubectl apply -f k8s/dev/secret.yaml

# Deploy PostgreSQL
kubectl apply -f k8s/dev/postgres-deployment.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce-dev --timeout=300s

# Deploy Backend
kubectl apply -f k8s/dev/backend-deployment.yaml

# Wait for Backend
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce-dev --timeout=300s

# Deploy Frontend
kubectl apply -f k8s/dev/frontend-deployment.yaml

# Deploy Ingress
kubectl apply -f k8s/dev/ingress.yaml
```

#### Step 5: Access Application

```bash
# Get Minikube IP
minikube ip

# Add to /etc/hosts
echo "$(minikube ip) ecommerce.local" | sudo tee -a /etc/hosts

# Access in browser
http://ecommerce.local

# Or use NodePort
http://$(minikube ip):30080
```

### Verification

```bash
# Check all pods are running
kubectl get pods -n ecommerce-dev

# Check services
kubectl get svc -n ecommerce-dev

# Check ingress
kubectl get ingress -n ecommerce-dev

# View logs
kubectl logs -f deployment/frontend -n ecommerce-dev
kubectl logs -f deployment/backend -n ecommerce-dev
```

---

## Staging Environment (Kind)

### Prerequisites

- Kind installed
- kubectl installed
- Docker installed
- 8 CPU cores, 16GB RAM recommended

### Automated Setup

```bash
# Create staging cluster
./scripts/setup-kind.sh ecommerce-staging staging
```

### Manual Setup

#### Step 1: Create Kind Cluster

Create `kind-config.yaml`:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
  - containerPort: 443
    hostPort: 443
  - containerPort: 30080
    hostPort: 30080
- role: worker
- role: worker
```

```bash
# Create cluster
kind create cluster --name ecommerce-staging --config kind-config.yaml

# Verify
kubectl cluster-info --context kind-ecommerce-staging
kubectl get nodes
```

#### Step 2: Install Ingress Controller

```bash
# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

# Wait for ingress to be ready
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s
```

#### Step 3: Install Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Patch for Kind (skip TLS verification)
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'
```

#### Step 4: Build and Load Images

```bash
# Build images
docker build -t backend:v1.0.0 ./apps/backend
docker build -t frontend:v1.0.0 ./apps/frontend

# Load into Kind
kind load docker-image backend:v1.0.0 --name ecommerce-staging
kind load docker-image frontend:v1.0.0 --name ecommerce-staging
```

#### Step 5: Deploy Application

```bash
# Deploy all staging manifests
kubectl apply -f k8s/staging/

# Wait for deployments
kubectl wait --for=condition=available --timeout=300s \
  deployment --all -n ecommerce-staging
```

#### Step 6: Access Application

```bash
# Add to /etc/hosts
echo "127.0.0.1 ecommerce.local" | sudo tee -a /etc/hosts

# Access
http://ecommerce.local
# or
http://localhost:30080
```

---

## Production Environment (Kubeadm)

### Prerequisites

- 3+ Linux servers (Ubuntu 20.04/22.04)
- 2+ CPU cores, 4GB RAM per node (minimum)
- Network connectivity between nodes
- Root/sudo access

### Infrastructure Setup

#### Step 1: Prepare All Nodes

On **all nodes**, run:

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install kubeadm, kubelet, kubectl
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl

curl -fsSL https://pkgs.k8s.io/core:/stable:/v1.28/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

echo 'deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v1.28/deb/ /' | sudo tee /etc/apt/sources.list.d/kubernetes.list

sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl

# Disable swap
sudo swapoff -a
sudo sed -i '/ swap / s/^\(.*\)$/#\1/g' /etc/fstab

# Load kernel modules
cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sudo modprobe overlay
sudo modprobe br_netfilter

# Set sysctl params
cat <<EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-iptables  = 1
net.bridge.bridge-nf-call-ip6tables = 1
net.ipv4.ip_forward                 = 1
EOF

sudo sysctl --system
```

#### Step 2: Initialize Control Plane

On **master node**:

```bash
# Initialize cluster
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

# Setup kubectl for current user
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config

# Install Calico network plugin
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/tigera-operator.yaml
kubectl create -f https://raw.githubusercontent.com/projectcalico/calico/v3.26.1/manifests/custom-resources.yaml

# Wait for all system pods to be ready
kubectl wait --for=condition=Ready pods --all -n kube-system --timeout=300s
```

Save the join command output, you'll need it for worker nodes!

#### Step 3: Join Worker Nodes

On **each worker node**:

```bash
# Use the join command from kubeadm init output
sudo kubeadm join <master-ip>:6443 --token <token> \
    --discovery-token-ca-cert-hash sha256:<hash>
```

Verify on master:

```bash
kubectl get nodes
```

#### Step 4: Install Ingress Controller

```bash
# Install NGINX Ingress
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Wait for external IP (cloud) or get NodePort (bare metal)
kubectl get svc -n ingress-nginx
```

#### Step 5: Install Metrics Server

```bash
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

#### Step 6: Deploy Application

```bash
# Clone repository on master node
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# Deploy production manifests
kubectl apply -f k8s/prod/

# Verify deployment
kubectl get all -n ecommerce-prod

# Wait for all pods
kubectl wait --for=condition=ready pod --all -n ecommerce-prod --timeout=600s
```

#### Step 7: Configure DNS

Point your domain to the LoadBalancer IP or Ingress IP:

```bash
# Get Ingress IP
kubectl get ingress -n ecommerce-prod

# Configure DNS A record
# ecommerce.example.com -> <INGRESS_IP>
```

---

## GitOps Deployment (ArgoCD)

### Installation

```bash
# Install ArgoCD
./scripts/setup-argocd.sh

# Or manually:
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Access ArgoCD

```bash
# Port forward
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Login at https://localhost:8080
# Username: admin
# Password: <from above>
```

### Deploy Applications

```bash
# Apply all ArgoCD applications
kubectl apply -f argocd/dev/application.yaml
kubectl apply -f argocd/staging/application.yaml
kubectl apply -f argocd/prod/application.yaml
```

### Sync Applications

**Development** (auto-sync enabled):
- ArgoCD automatically syncs changes from Git

**Staging** (auto-sync enabled):
- ArgoCD automatically syncs changes from Git

**Production** (manual sync):
```bash
# Via kubectl
kubectl -n argocd patch application ecommerce-prod \
  -p '{"operation":{"sync":{}}}' --type merge

# Via ArgoCD UI
# Click "Sync" button on ecommerce-prod application
```

---

## Manual Deployment Steps

### Without Scripts

#### For Any Environment

1. **Prepare Kubernetes cluster** (Minikube/Kind/Kubeadm)

2. **Build Docker images:**
   ```bash
   docker build -t backend:latest ./apps/backend
   docker build -t frontend:latest ./apps/frontend
   ```

3. **Load images** (for Minikube/Kind):
   ```bash
   # Minikube
   eval $(minikube docker-env)
   
   # Kind
   kind load docker-image backend:latest
   kind load docker-image frontend:latest
   ```

4. **Apply Kubernetes manifests:**
   ```bash
   kubectl apply -f k8s/<env>/
   ```

5. **Verify deployment:**
   ```bash
   kubectl get all -n ecommerce-<env>
   ```

6. **Access application:**
   - Minikube: `minikube service frontend-service -n ecommerce-<env>`
   - Kind/Kubeadm: Via Ingress or NodePort

---

## Post-Deployment

### Enable Monitoring

```bash
./scripts/setup-monitoring.sh
```

### Configure TLS (Production)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Create ClusterIssuer for Let's Encrypt
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### Backup Strategy

```bash
# Backup etcd (control plane)
sudo ETCDCTL_API=3 etcdctl snapshot save /backup/etcd-snapshot.db \
  --endpoints=https://127.0.0.1:2379 \
  --cacert=/etc/kubernetes/pki/etcd/ca.crt \
  --cert=/etc/kubernetes/pki/etcd/server.crt \
  --key=/etc/kubernetes/pki/etcd/server.key

# Backup application data (PostgreSQL)
kubectl exec -n ecommerce-prod postgres-0 -- \
  pg_dump -U postgres ecommerce > backup-$(date +%Y%m%d).sql
```

---

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>
```

**Network issues:**
```bash
# Test pod connectivity
kubectl run -it --rm debug --image=busybox --restart=Never -- sh
# Inside pod: wget -O- http://backend-service.ecommerce-dev:5000/health
```

**Resource constraints:**
```bash
kubectl top nodes
kubectl top pods -n <namespace>
```

---

## Cleanup

```bash
# Delete namespace
kubectl delete namespace ecommerce-<env>

# Delete cluster (Minikube)
minikube delete

# Delete cluster (Kind)
kind delete cluster --name <cluster-name>
```
