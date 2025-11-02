#!/bin/bash

# Setup ArgoCD for GitOps
# Installs and configures ArgoCD with applications

set -e

echo "🚀 Setting up ArgoCD for GitOps"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

print_info "Creating ArgoCD namespace..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -

print_info "Installing ArgoCD..."
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

print_info "Waiting for ArgoCD to be ready..."
kubectl wait --for=condition=available --timeout=300s \
  deployment --all -n argocd

print_info "Applying ArgoCD ingress (optional)..."
kubectl apply -f argocd/install.yaml || true

print_info "Getting ArgoCD admin password..."
ARGOCD_PASSWORD=$(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)

print_info "Applying ArgoCD Applications..."
kubectl apply -f argocd/dev/application.yaml
kubectl apply -f argocd/staging/application.yaml
kubectl apply -f argocd/prod/application.yaml

print_info "✅ ArgoCD setup complete!"
echo ""
echo "=================================================="
echo "🎉 ArgoCD is ready!"
echo "=================================================="
echo ""
echo "Access ArgoCD UI:"
echo ""
echo "1. Port Forward (Recommended for first access):"
echo "   kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "   Then open: https://localhost:8080"
echo ""
echo "2. Ingress (if configured):"
echo "   Add to /etc/hosts: <CLUSTER_IP> argocd.local"
echo "   Then open: https://argocd.local"
echo ""
echo "Login Credentials:"
echo "  Username: admin"
echo "  Password: $ARGOCD_PASSWORD"
echo ""
echo "Applications Deployed:"
echo "  - ecommerce-dev (Auto-sync enabled)"
echo "  - ecommerce-staging (Auto-sync enabled)"
echo "  - ecommerce-prod (Manual sync - requires approval)"
echo ""
echo "ArgoCD CLI Installation (optional):"
echo "  Visit: https://argo-cd.readthedocs.io/en/stable/cli_installation/"
echo ""
echo "Useful Commands:"
echo "  - List applications: kubectl get applications -n argocd"
echo "  - Sync application: kubectl -n argocd patch application ecommerce-dev -p '{\"operation\":{\"sync\":{}}}' --type merge"
echo "  - View application status: kubectl get application ecommerce-dev -n argocd -o yaml"
echo ""
