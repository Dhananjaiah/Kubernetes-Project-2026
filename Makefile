.PHONY: help build-images docker-compose-up docker-compose-down minikube-start minikube-deploy minikube-stop kind-create kind-deploy kind-delete argocd-install monitoring-install clean

# Default target
.DEFAULT_GOAL := help

# Variables
BACKEND_IMAGE := backend:latest
FRONTEND_IMAGE := frontend:latest
KIND_CLUSTER_NAME := ecommerce-cluster
NAMESPACE_DEV := ecommerce-dev
NAMESPACE_STAGING := ecommerce-staging
NAMESPACE_PROD := ecommerce-prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Docker Compose targets
docker-compose-up: ## Start application with Docker Compose
	docker-compose up -d
	@echo "Application started. Access at http://localhost:3000"

docker-compose-down: ## Stop application with Docker Compose
	docker-compose down -v

docker-compose-logs: ## View Docker Compose logs
	docker-compose logs -f

# Build targets
build-images: ## Build Docker images
	docker build -t $(BACKEND_IMAGE) ./apps/backend
	docker build -t $(FRONTEND_IMAGE) ./apps/frontend
	@echo "Images built successfully"

# Minikube targets
minikube-start: ## Start Minikube cluster
	./scripts/setup-minikube.sh

minikube-deploy: build-images ## Deploy to Minikube (after starting)
	eval $$(minikube docker-env) && \
	docker build -t $(BACKEND_IMAGE) ./apps/backend && \
	docker build -t $(FRONTEND_IMAGE) ./apps/frontend
	kubectl apply -f k8s/dev/
	@echo "Deployed to Minikube. Access at http://$$(minikube ip):30080"

minikube-stop: ## Stop Minikube
	minikube stop

minikube-delete: ## Delete Minikube cluster
	minikube delete

minikube-ip: ## Get Minikube IP
	@minikube ip

# Kind targets
kind-create: ## Create Kind cluster
	./scripts/setup-kind.sh $(KIND_CLUSTER_NAME) dev

kind-deploy: build-images ## Deploy to Kind cluster
	kind load docker-image $(BACKEND_IMAGE) --name $(KIND_CLUSTER_NAME)
	kind load docker-image $(FRONTEND_IMAGE) --name $(KIND_CLUSTER_NAME)
	kubectl apply -f k8s/dev/
	@echo "Deployed to Kind. Access at http://localhost:30080"

kind-delete: ## Delete Kind cluster
	kind delete cluster --name $(KIND_CLUSTER_NAME)

# Kubernetes management targets
k8s-dev-deploy: ## Deploy to development environment
	kubectl apply -f k8s/dev/
	kubectl wait --for=condition=ready pod --all -n $(NAMESPACE_DEV) --timeout=300s

k8s-staging-deploy: ## Deploy to staging environment
	kubectl apply -f k8s/staging/
	kubectl wait --for=condition=ready pod --all -n $(NAMESPACE_STAGING) --timeout=300s

k8s-prod-deploy: ## Deploy to production environment
	kubectl apply -f k8s/prod/
	kubectl wait --for=condition=ready pod --all -n $(NAMESPACE_PROD) --timeout=600s

k8s-dev-delete: ## Delete development environment
	kubectl delete namespace $(NAMESPACE_DEV)

k8s-staging-delete: ## Delete staging environment
	kubectl delete namespace $(NAMESPACE_STAGING)

k8s-prod-delete: ## Delete production environment
	kubectl delete namespace $(NAMESPACE_PROD)

# ArgoCD targets
argocd-install: ## Install ArgoCD
	./scripts/setup-argocd.sh

argocd-password: ## Get ArgoCD admin password
	@kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo

argocd-port-forward: ## Port forward to ArgoCD UI
	kubectl port-forward svc/argocd-server -n argocd 8080:443

# Monitoring targets
monitoring-install: ## Install monitoring stack (Prometheus + Grafana)
	./scripts/setup-monitoring.sh

grafana-password: ## Get Grafana admin password
	@echo "Default: admin / admin"

grafana-port-forward: ## Port forward to Grafana UI
	kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80

prometheus-port-forward: ## Port forward to Prometheus UI
	kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# Utility targets
logs-frontend-dev: ## View frontend logs (dev)
	kubectl logs -f deployment/frontend -n $(NAMESPACE_DEV)

logs-backend-dev: ## View backend logs (dev)
	kubectl logs -f deployment/backend -n $(NAMESPACE_DEV)

logs-postgres-dev: ## View PostgreSQL logs (dev)
	kubectl logs -f deployment/postgres -n $(NAMESPACE_DEV)

status-dev: ## Show status of development environment
	kubectl get all -n $(NAMESPACE_DEV)

status-staging: ## Show status of staging environment
	kubectl get all -n $(NAMESPACE_STAGING)

status-prod: ## Show status of production environment
	kubectl get all -n $(NAMESPACE_PROD)

port-forward-frontend: ## Port forward to frontend service
	kubectl port-forward -n $(NAMESPACE_DEV) svc/frontend-service 3000:3000

port-forward-backend: ## Port forward to backend service
	kubectl port-forward -n $(NAMESPACE_DEV) svc/backend-service 5000:5000

# Testing targets
test-frontend: ## Test frontend health
	@curl -f http://localhost:3000/health || echo "Frontend not accessible"

test-backend: ## Test backend health
	@curl -f http://localhost:5000/health || echo "Backend not accessible"

test-api: ## Test backend API
	@curl -f http://localhost:5000/api/products || echo "Backend API not accessible"

# Clean targets
clean: ## Clean up all resources
	@echo "Cleaning up Docker images..."
	docker rmi -f $(BACKEND_IMAGE) $(FRONTEND_IMAGE) 2>/dev/null || true
	@echo "Stopping Docker Compose..."
	docker-compose down -v 2>/dev/null || true
	@echo "Clean completed"

clean-all: clean ## Clean everything including clusters
	minikube delete 2>/dev/null || true
	kind delete cluster --name $(KIND_CLUSTER_NAME) 2>/dev/null || true
	@echo "All resources cleaned"
