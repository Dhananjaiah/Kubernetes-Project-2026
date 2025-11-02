#!/bin/bash

# Setup Monitoring Stack (Prometheus + Grafana)
# Installs kube-prometheus-stack using Helm

set -e

echo "🚀 Setting up Monitoring Stack"

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

# Check if helm is installed
if ! command -v helm &> /dev/null; then
    print_error "Helm is not installed. Please install it first."
    echo "Visit: https://helm.sh/docs/intro/install/"
    exit 1
fi

# Check if kubectl is installed
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed. Please install it first."
    exit 1
fi

print_info "Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

print_info "Adding Prometheus Helm repository..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

print_info "Installing kube-prometheus-stack..."
helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring \
  -f monitoring/prometheus-values.yaml \
  --wait

print_info "Applying ServiceMonitors..."
kubectl apply -f monitoring/servicemonitor.yaml || true

print_info "✅ Monitoring stack setup complete!"
echo ""
echo "=================================================="
echo "🎉 Monitoring Stack is ready!"
echo "=================================================="
echo ""
echo "Access Grafana:"
echo "1. Port Forward:"
echo "   kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80"
echo "   Then open: http://localhost:3001"
echo ""
echo "Login Credentials:"
echo "  Username: admin"
echo "  Password: admin (change after first login)"
echo ""
echo "Access Prometheus:"
echo "   kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090"
echo "   Then open: http://localhost:9090"
echo ""
echo "Access AlertManager:"
echo "   kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-alertmanager 9093:9093"
echo "   Then open: http://localhost:9093"
echo ""
echo "Pre-configured Dashboards in Grafana:"
echo "  - Kubernetes Cluster Monitoring"
echo "  - Node Exporter Full"
echo "  - Kubernetes API Server"
echo "  - And many more..."
echo ""
