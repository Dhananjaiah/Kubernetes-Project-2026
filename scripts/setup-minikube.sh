#!/bin/bash

# Setup Minikube for Development Environment
# This script sets up a complete Minikube environment with all necessary components

set -e

echo "🚀 Starting Minikube Setup for E-Commerce Application"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if minikube is installed
if ! command -v minikube &> /dev/null; then
    print_error "Minikube is not installed. Please install it first."
    echo "Visit: https://minikube.sigs.k8s.io/docs/start/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

print_info "Starting Minikube cluster..."
minikube start --cpus=4 --memory=8192 --driver=docker

print_info "Enabling Minikube addons..."
minikube addons enable ingress
minikube addons enable metrics-server
minikube addons enable dashboard

print_info "Setting Docker environment to use Minikube's Docker daemon..."
eval $(minikube docker-env)

print_info "Building Docker images..."
cd "$(dirname "$0")/.."

print_info "Building backend image..."
docker build -t backend:latest ./apps/backend

print_info "Building frontend image..."
docker build -t frontend:latest ./apps/frontend

print_info "Creating namespace..."
kubectl apply -f k8s/dev/namespace.yaml

print_info "Applying ConfigMaps and Secrets..."
kubectl apply -f k8s/dev/configmap.yaml
kubectl apply -f k8s/dev/secret.yaml

print_info "Deploying PostgreSQL..."
kubectl apply -f k8s/dev/postgres-deployment.yaml

print_info "Waiting for PostgreSQL to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n ecommerce-dev --timeout=300s

print_info "Deploying Backend..."
kubectl apply -f k8s/dev/backend-deployment.yaml

print_info "Waiting for Backend to be ready..."
kubectl wait --for=condition=ready pod -l app=backend -n ecommerce-dev --timeout=300s

print_info "Deploying Frontend..."
kubectl apply -f k8s/dev/frontend-deployment.yaml

print_info "Waiting for Frontend to be ready..."
kubectl wait --for=condition=ready pod -l app=frontend -n ecommerce-dev --timeout=300s

print_info "Applying Ingress..."
kubectl apply -f k8s/dev/ingress.yaml

# Get Minikube IP
MINIKUBE_IP=$(minikube ip)

print_info "✅ Deployment Complete!"
echo ""
echo "=================================================="
echo "🎉 E-Commerce Application is now running!"
echo "=================================================="
echo ""
echo "Access Methods:"
echo ""
echo "1. NodePort (Direct):"
echo "   Frontend: http://$MINIKUBE_IP:30080"
echo ""
echo "2. Ingress (Add to /etc/hosts):"
echo "   Add this line to /etc/hosts:"
echo "   $MINIKUBE_IP ecommerce.local"
echo "   Then access: http://ecommerce.local"
echo ""
echo "3. Port Forward:"
echo "   kubectl port-forward -n ecommerce-dev svc/frontend-service 3000:3000"
echo "   Then access: http://localhost:3000"
echo ""
echo "Useful Commands:"
echo "  - View pods: kubectl get pods -n ecommerce-dev"
echo "  - View services: kubectl get svc -n ecommerce-dev"
echo "  - View logs: kubectl logs -f deployment/frontend -n ecommerce-dev"
echo "  - Access dashboard: minikube dashboard"
echo ""
echo "To stop: minikube stop"
echo "To delete: minikube delete"
echo ""
