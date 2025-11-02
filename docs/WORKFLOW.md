# Development Workflow Guide

This guide explains the typical development workflow for this project.

## 🔄 Standard Development Cycle

### 1. Local Development

```bash
# Start with Docker Compose for fast iteration
docker-compose up -d

# Make code changes in apps/frontend or apps/backend

# Restart specific service to see changes
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Test locally
curl http://localhost:5000/api/products
open http://localhost:3000
```

### 2. Build and Test Docker Images

```bash
# Build images
docker build -t backend:dev ./apps/backend
docker build -t frontend:dev ./apps/frontend

# Test images locally
docker run -p 5000:5000 -e DB_HOST=host.docker.internal backend:dev
docker run -p 3000:3000 -e BACKEND_URL=http://host.docker.internal:5000 frontend:dev
```

### 3. Deploy to Development (Minikube)

```bash
# Start Minikube
minikube start

# Use Minikube's Docker
eval $(minikube docker-env)

# Build images in Minikube
docker build -t backend:latest ./apps/backend
docker build -t frontend:latest ./apps/frontend

# Deploy
kubectl apply -f k8s/dev/

# Verify
kubectl get pods -n ecommerce-dev
kubectl logs -f deployment/backend -n ecommerce-dev

# Test
minikube service frontend-service -n ecommerce-dev
```

### 4. Update Configuration

```bash
# Edit ConfigMap
kubectl edit configmap backend-config -n ecommerce-dev

# Or apply changes from file
kubectl apply -f k8s/dev/configmap.yaml

# Restart pods to pick up changes
kubectl rollout restart deployment/backend -n ecommerce-dev
```

### 5. Test Changes

```bash
# Port forward for testing
kubectl port-forward -n ecommerce-dev svc/backend-service 5000:5000

# Test API
curl http://localhost:5000/api/products
curl http://localhost:5000/health

# Load test
ab -n 100 -c 10 http://localhost:5000/api/products
```

### 6. Update Application Code

```bash
# Make code changes
vim apps/backend/app.py

# Rebuild image
eval $(minikube docker-env)
docker build -t backend:latest ./apps/backend

# Delete pods to force recreation with new image
kubectl delete pods -l app=backend -n ecommerce-dev

# Watch pods restart
kubectl get pods -n ecommerce-dev -w
```

### 7. Move to Staging

```bash
# Create Kind cluster for staging
./scripts/setup-kind.sh ecommerce-staging staging

# Build and tag images for staging
docker build -t backend:v1.1.0 ./apps/backend
docker build -t frontend:v1.1.0 ./apps/frontend

# Load images to Kind
kind load docker-image backend:v1.1.0 --name ecommerce-staging
kind load docker-image frontend:v1.1.0 --name ecommerce-staging

# Update staging manifests with new version
sed -i 's/backend:latest/backend:v1.1.0/g' k8s/staging/backend-deployment.yaml

# Deploy
kubectl apply -f k8s/staging/

# Verify
kubectl get all -n ecommerce-staging
```

### 8. Production Deployment

```bash
# Tag and push images to registry
docker tag backend:v1.1.0 ghcr.io/username/backend:v1.1.0
docker tag frontend:v1.1.0 ghcr.io/username/frontend:v1.1.0

docker push ghcr.io/username/backend:v1.1.0
docker push ghcr.io/username/frontend:v1.1.0

# Update production manifests
sed -i 's|image: backend:.*|image: ghcr.io/username/backend:v1.1.0|g' k8s/prod/backend-deployment.yaml

# Commit changes
git add k8s/prod/
git commit -m "Update production to v1.1.0"
git push

# If using ArgoCD - manually sync production
kubectl -n argocd patch application ecommerce-prod -p '{"operation":{"sync":{}}}' --type merge

# Monitor rollout
kubectl rollout status deployment/backend -n ecommerce-prod
kubectl get pods -n ecommerce-prod -w
```

## 🔧 Common Workflows

### Adding a New Feature

1. **Create feature branch**
   ```bash
   git checkout -b feature/new-endpoint
   ```

2. **Develop locally with Docker Compose**
   ```bash
   docker-compose up -d
   # Edit code
   docker-compose restart backend
   ```

3. **Test in Minikube**
   ```bash
   eval $(minikube docker-env)
   docker build -t backend:latest ./apps/backend
   kubectl delete pods -l app=backend -n ecommerce-dev
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add new API endpoint"
   git push origin feature/new-endpoint
   ```

5. **Create pull request**
   - GitHub Actions will build and test
   - Review and merge

6. **Deploy to staging/prod**
   - ArgoCD auto-syncs to staging
   - Manual sync to production

### Debugging Production Issues

1. **Check pod status**
   ```bash
   kubectl get pods -n ecommerce-prod
   kubectl describe pod <pod-name> -n ecommerce-prod
   ```

2. **View logs**
   ```bash
   kubectl logs -f deployment/backend -n ecommerce-prod
   kubectl logs deployment/backend -n ecommerce-prod --previous
   ```

3. **Check events**
   ```bash
   kubectl get events -n ecommerce-prod --sort-by='.lastTimestamp'
   ```

4. **Access pod shell**
   ```bash
   kubectl exec -it deployment/backend -n ecommerce-prod -- /bin/sh
   ```

5. **Check configurations**
   ```bash
   kubectl get configmap backend-config -n ecommerce-prod -o yaml
   kubectl get secret postgres-secret -n ecommerce-prod -o yaml
   ```

6. **Port forward for direct testing**
   ```bash
   kubectl port-forward -n ecommerce-prod svc/backend-service 5000:5000
   curl http://localhost:5000/health
   ```

### Scaling for Traffic Spike

1. **Monitor current load**
   ```bash
   kubectl top pods -n ecommerce-prod
   kubectl get hpa -n ecommerce-prod
   ```

2. **Manual scale if needed**
   ```bash
   kubectl scale deployment backend --replicas=10 -n ecommerce-prod
   kubectl scale deployment frontend --replicas=10 -n ecommerce-prod
   ```

3. **Watch HPA auto-scale**
   ```bash
   watch kubectl get hpa -n ecommerce-prod
   ```

4. **Monitor pods**
   ```bash
   watch kubectl get pods -n ecommerce-prod
   ```

### Database Maintenance

1. **Backup database**
   ```bash
   kubectl exec -n ecommerce-prod postgres-0 -- \
     pg_dump -U postgres ecommerce > backup-$(date +%Y%m%d).sql
   ```

2. **Access database**
   ```bash
   kubectl exec -it -n ecommerce-prod postgres-0 -- psql -U postgres ecommerce
   ```

3. **Run SQL scripts**
   ```bash
   kubectl exec -i -n ecommerce-prod postgres-0 -- \
     psql -U postgres ecommerce < migration.sql
   ```

4. **Restore from backup**
   ```bash
   kubectl exec -i -n ecommerce-prod postgres-0 -- \
     psql -U postgres ecommerce < backup-20241102.sql
   ```

### Rollback Deployment

1. **View rollout history**
   ```bash
   kubectl rollout history deployment/backend -n ecommerce-prod
   ```

2. **Rollback to previous version**
   ```bash
   kubectl rollout undo deployment/backend -n ecommerce-prod
   ```

3. **Rollback to specific revision**
   ```bash
   kubectl rollout undo deployment/backend --to-revision=3 -n ecommerce-prod
   ```

4. **Verify rollback**
   ```bash
   kubectl rollout status deployment/backend -n ecommerce-prod
   kubectl get pods -n ecommerce-prod
   ```

### Updating Secrets

1. **Create new secret**
   ```bash
   kubectl create secret generic postgres-secret-new \
     --from-literal=POSTGRES_PASSWORD=newpassword \
     -n ecommerce-prod --dry-run=client -o yaml | kubectl apply -f -
   ```

2. **Update deployment to use new secret**
   ```bash
   kubectl edit deployment postgres -n ecommerce-prod
   # Change secretRef name
   ```

3. **Restart pods**
   ```bash
   kubectl rollout restart deployment/postgres -n ecommerce-prod
   ```

## 🎯 GitOps Workflow

When using ArgoCD:

### 1. Make Changes

```bash
# Edit Kubernetes manifests
vim k8s/dev/backend-deployment.yaml

# Commit and push
git add k8s/dev/
git commit -m "Update backend configuration"
git push
```

### 2. ArgoCD Detects Changes

- ArgoCD polls Git repository (every 3 minutes by default)
- Or use webhook for immediate detection
- Shows "OutOfSync" status in UI

### 3. Auto-Sync (Dev/Staging)

```bash
# ArgoCD automatically applies changes
# Monitor sync status
kubectl get application ecommerce-dev -n argocd

# View sync history
kubectl describe application ecommerce-dev -n argocd
```

### 4. Manual Sync (Production)

```bash
# Review changes in ArgoCD UI
# Click "Sync" when ready

# Or via CLI
kubectl -n argocd patch application ecommerce-prod \
  -p '{"operation":{"sync":{}}}' --type merge
```

### 5. Monitor Deployment

```bash
# Watch application status
watch kubectl get application -n argocd

# Check pod status
kubectl get pods -n ecommerce-prod -w

# View ArgoCD logs
kubectl logs -f -n argocd deployment/argocd-application-controller
```

## 🔄 CI/CD Pipeline Workflow

### GitHub Actions Pipeline

1. **Trigger**: Push to main/develop or PR

2. **Build Stage**:
   - Checkout code
   - Build Docker images
   - Run tests (if present)

3. **Security Stage**:
   - Scan images with Trivy
   - Check for vulnerabilities

4. **Push Stage**:
   - Tag images with branch name and SHA
   - Push to GitHub Container Registry

5. **Deploy Stage** (if ArgoCD):
   - ArgoCD detects new images
   - Auto-deploys to dev/staging
   - Manual approval for production

### Example Workflow

```bash
# Developer makes changes
vim apps/backend/app.py

# Commit and push
git add apps/backend/app.py
git commit -m "Add new feature"
git push origin feature/new-feature

# GitHub Actions:
# 1. Builds backend:feature-new-feature-abc123
# 2. Runs security scan
# 3. Pushes to ghcr.io

# Update manifest (or use image updater)
vim k8s/dev/backend-deployment.yaml
# Update image tag

# Commit manifest change
git add k8s/dev/
git commit -m "Update dev to new version"
git push

# ArgoCD auto-syncs to dev environment
```

## 📊 Monitoring Workflow

### Regular Health Checks

```bash
# Check application health
curl http://localhost:3000/health  # Frontend
curl http://localhost:5000/health  # Backend

# Check Kubernetes health
kubectl get componentstatuses
kubectl get nodes
kubectl top nodes

# Check application metrics
kubectl top pods -n ecommerce-prod
```

### Alert Response

1. **Receive Alert** (from Grafana/AlertManager)

2. **Check Metrics**
   ```bash
   # Open Grafana
   kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80
   # Open http://localhost:3001
   ```

3. **Investigate Logs**
   ```bash
   kubectl logs -f deployment/backend -n ecommerce-prod
   kubectl logs deployment/backend -n ecommerce-prod --tail=1000
   ```

4. **Check Resource Usage**
   ```bash
   kubectl top pods -n ecommerce-prod
   kubectl describe pod <pod-name> -n ecommerce-prod
   ```

5. **Take Action**
   - Scale up if needed
   - Rollback if recent deployment
   - Fix configuration
   - Restart pods

## 🎓 Learning Path

### Beginner: Local Development

1. Start with Docker Compose
2. Make code changes
3. Test locally
4. Learn Docker basics

### Intermediate: Kubernetes Basics

1. Deploy to Minikube
2. Learn kubectl commands
3. Understand pods, services, deployments
4. Practice troubleshooting

### Advanced: Production Operations

1. Multi-node with Kind
2. Implement monitoring
3. Configure HPA
4. Add network policies
5. Set up ArgoCD

### Expert: Production Management

1. Deploy to cloud (EKS/GKE/AKS)
2. Implement backup/restore
3. Configure HA control plane
4. Advanced monitoring and alerting
5. Disaster recovery planning

## 📝 Best Practices

1. **Always test locally first** with Docker Compose
2. **Use feature branches** for development
3. **Test in dev** before staging/production
4. **Monitor deployments** during rollouts
5. **Keep backups** of database and configurations
6. **Document changes** in commit messages
7. **Use proper versioning** for images
8. **Review logs** regularly
9. **Set up alerts** for critical issues
10. **Practice rollbacks** in non-production

---

This workflow guide should help you navigate through the development, deployment, and maintenance of the application efficiently!
