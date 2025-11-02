#!/bin/bash

# Setup Kind Cluster for Development/Staging
# Creates a multi-node Kind cluster for testing

set -e

echo "🚀 Starting Kind Cluster Setup"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    print_error "Kind is not installed. Please install it first."
    echo "Visit: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

CLUSTER_NAME="${1:-ecommerce-cluster}"
ENV="${2:-dev}"

print_info "Creating Kind cluster: $CLUSTER_NAME"

cat <<EOF | kind create cluster --name $CLUSTER_NAME --config=-
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
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
- role: worker
- role: worker
EOF

print_info "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s

print_info "Installing NGINX Ingress Controller..."
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

print_info "Waiting for NGINX Ingress to be ready..."
kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=300s

print_info "Installing Metrics Server..."
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
kubectl patch -n kube-system deployment metrics-server --type=json \
  -p '[{"op":"add","path":"/spec/template/spec/containers/0/args/-","value":"--kubelet-insecure-tls"}]'

print_info "Building and loading Docker images..."
cd "$(dirname "$0")/.."

print_info "Building backend image..."
docker build -t backend:latest ./apps/backend
kind load docker-image backend:latest --name $CLUSTER_NAME

print_info "Building frontend image..."
docker build -t frontend:latest ./apps/frontend
kind load docker-image frontend:latest --name $CLUSTER_NAME

print_info "Deploying application to $ENV environment..."
kubectl apply -f k8s/$ENV/

print_info "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment --all -n ecommerce-$ENV || true

print_info "✅ Kind cluster setup complete!"
echo ""
echo "=================================================="
echo "🎉 Kind Cluster is ready!"
echo "=================================================="
echo ""
echo "Cluster: $CLUSTER_NAME"
echo "Environment: $ENV"
echo ""
echo "Access Methods:"
echo "1. NodePort: http://localhost:30080"
echo "2. Ingress (add to /etc/hosts):"
echo "   127.0.0.1 ecommerce.local"
echo "   http://ecommerce.local"
echo ""
echo "Useful Commands:"
echo "  - Get cluster info: kubectl cluster-info --context kind-$CLUSTER_NAME"
echo "  - View pods: kubectl get pods -n ecommerce-$ENV"
echo "  - View services: kubectl get svc -n ecommerce-$ENV"
echo "  - Delete cluster: kind delete cluster --name $CLUSTER_NAME"
echo ""
