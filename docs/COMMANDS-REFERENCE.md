# Kubernetes Commands Reference

Quick reference for common operations with this project.

## 📦 Deployment Commands

### Deploy to Development

```bash
# Apply all dev manifests
kubectl apply -f k8s/dev/

# Or use Makefile
make k8s-dev-deploy
```

### Deploy to Staging

```bash
kubectl apply -f k8s/staging/
make k8s-staging-deploy
```

### Deploy to Production

```bash
kubectl apply -f k8s/prod/
make k8s-prod-deploy
```

## 🔍 Inspection Commands

### View Resources

```bash
# All resources in namespace
kubectl get all -n ecommerce-dev

# Just pods
kubectl get pods -n ecommerce-dev

# Services
kubectl get svc -n ecommerce-dev

# Deployments
kubectl get deployments -n ecommerce-dev

# With more details
kubectl get pods -n ecommerce-dev -o wide

# Watch for changes
kubectl get pods -n ecommerce-dev --watch
```

### Describe Resources

```bash
# Describe a pod
kubectl describe pod <pod-name> -n ecommerce-dev

# Describe a service
kubectl describe svc frontend-service -n ecommerce-dev

# Describe a deployment
kubectl describe deployment backend -n ecommerce-dev
```

### Check Events

```bash
# Recent events in namespace
kubectl get events -n ecommerce-dev --sort-by='.lastTimestamp'

# Watch events
kubectl get events -n ecommerce-dev --watch
```

## 📋 Logs Commands

### View Logs

```bash
# Current logs
kubectl logs deployment/frontend -n ecommerce-dev

# Follow logs (streaming)
kubectl logs -f deployment/backend -n ecommerce-dev

# Previous container logs (if crashed)
kubectl logs deployment/backend -n ecommerce-dev --previous

# Logs from specific container in pod
kubectl logs <pod-name> -c <container-name> -n ecommerce-dev

# Last 100 lines
kubectl logs deployment/frontend -n ecommerce-dev --tail=100

# Logs from all pods with label
kubectl logs -l app=backend -n ecommerce-dev --all-containers=true
```

### Using Makefile

```bash
make logs-frontend-dev
make logs-backend-dev
make logs-postgres-dev
```

## 🔧 Debugging Commands

### Execute Commands in Pod

```bash
# Get shell access
kubectl exec -it deployment/backend -n ecommerce-dev -- /bin/sh

# Run a single command
kubectl exec deployment/backend -n ecommerce-dev -- env

# Test database connection
kubectl exec -it deployment/backend -n ecommerce-dev -- nc -zv postgres-service 5432
```

### Port Forwarding

```bash
# Forward local port to service
kubectl port-forward -n ecommerce-dev svc/frontend-service 3000:3000
kubectl port-forward -n ecommerce-dev svc/backend-service 5000:5000
kubectl port-forward -n ecommerce-dev svc/postgres-service 5432:5432

# Forward to specific pod
kubectl port-forward -n ecommerce-dev <pod-name> 3000:3000

# Using Makefile
make port-forward-frontend
make port-forward-backend
```

### Debug with Temporary Pod

```bash
# Run busybox for debugging
kubectl run -it --rm debug --image=busybox --restart=Never -n ecommerce-dev -- sh

# Inside the pod, test connectivity
wget -O- http://backend-service:5000/health
nslookup backend-service

# Run curl pod
kubectl run -it --rm curl --image=curlimages/curl --restart=Never -n ecommerce-dev -- sh
```

## ⚙️ Configuration Commands

### ConfigMaps

```bash
# View configmap
kubectl get configmap -n ecommerce-dev
kubectl describe configmap backend-config -n ecommerce-dev

# Edit configmap
kubectl edit configmap backend-config -n ecommerce-dev

# Create from file
kubectl create configmap my-config --from-file=config.yaml -n ecommerce-dev
```

### Secrets

```bash
# View secrets (values are base64 encoded)
kubectl get secrets -n ecommerce-dev
kubectl describe secret postgres-secret -n ecommerce-dev

# Get secret value
kubectl get secret postgres-secret -n ecommerce-dev -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d

# Create secret
kubectl create secret generic my-secret --from-literal=password=mypassword -n ecommerce-dev
```

## 📊 Scaling Commands

### Manual Scaling

```bash
# Scale deployment
kubectl scale deployment frontend --replicas=3 -n ecommerce-dev
kubectl scale deployment backend --replicas=5 -n ecommerce-dev

# Scale StatefulSet
kubectl scale statefulset postgres --replicas=1 -n ecommerce-prod
```

### Autoscaling

```bash
# View HPA status
kubectl get hpa -n ecommerce-prod

# Describe HPA
kubectl describe hpa backend-hpa -n ecommerce-prod

# Create HPA manually
kubectl autoscale deployment backend --cpu-percent=70 --min=2 --max=10 -n ecommerce-dev
```

## 🔄 Update Commands

### Rolling Updates

```bash
# Update image
kubectl set image deployment/backend backend=backend:v2.0.0 -n ecommerce-dev

# Check rollout status
kubectl rollout status deployment/backend -n ecommerce-dev

# View rollout history
kubectl rollout history deployment/backend -n ecommerce-dev

# Rollback to previous version
kubectl rollout undo deployment/backend -n ecommerce-dev

# Rollback to specific revision
kubectl rollout undo deployment/backend --to-revision=2 -n ecommerce-dev

# Pause rollout
kubectl rollout pause deployment/backend -n ecommerce-dev

# Resume rollout
kubectl rollout resume deployment/backend -n ecommerce-dev
```

### Restart Deployments

```bash
# Restart all pods in deployment
kubectl rollout restart deployment/backend -n ecommerce-dev

# Delete pod (will be recreated)
kubectl delete pod <pod-name> -n ecommerce-dev
```

## 🗑️ Cleanup Commands

### Delete Resources

```bash
# Delete by file
kubectl delete -f k8s/dev/backend-deployment.yaml

# Delete by label
kubectl delete pods -l app=backend -n ecommerce-dev

# Delete deployment
kubectl delete deployment backend -n ecommerce-dev

# Delete service
kubectl delete service backend-service -n ecommerce-dev

# Delete namespace (deletes everything in it)
kubectl delete namespace ecommerce-dev

# Force delete stuck pod
kubectl delete pod <pod-name> -n ecommerce-dev --force --grace-period=0
```

### Using Makefile

```bash
make k8s-dev-delete
make k8s-staging-delete
make k8s-prod-delete
```

## 📈 Resource Monitoring

### Resource Usage

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n ecommerce-dev

# Specific pod
kubectl top pod <pod-name> -n ecommerce-dev

# Sort by CPU
kubectl top pods -n ecommerce-dev --sort-by=cpu

# Sort by memory
kubectl top pods -n ecommerce-dev --sort-by=memory
```

### Cluster Info

```bash
# Cluster information
kubectl cluster-info

# Cluster version
kubectl version

# Node information
kubectl get nodes -o wide

# Node details
kubectl describe node <node-name>
```

## 🔐 Security Commands

### RBAC

```bash
# View service accounts
kubectl get serviceaccounts -n ecommerce-dev

# View roles
kubectl get roles -n ecommerce-dev

# View role bindings
kubectl get rolebindings -n ecommerce-dev

# Check permissions
kubectl auth can-i create pods -n ecommerce-dev
kubectl auth can-i list secrets -n ecommerce-dev --as=system:serviceaccount:ecommerce-dev:ecommerce-app
```

### Network Policies

```bash
# View network policies
kubectl get networkpolicies -n ecommerce-prod

# Describe network policy
kubectl describe networkpolicy frontend-network-policy -n ecommerce-prod
```

## 🌐 Ingress Commands

```bash
# View ingress
kubectl get ingress -n ecommerce-dev

# Describe ingress
kubectl describe ingress ecommerce-ingress -n ecommerce-dev

# Get ingress IP/hostname
kubectl get ingress ecommerce-ingress -n ecommerce-dev -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
```

## 💾 Persistent Storage

```bash
# View PVCs
kubectl get pvc -n ecommerce-dev

# Describe PVC
kubectl describe pvc postgres-pvc -n ecommerce-dev

# View PVs
kubectl get pv

# Storage classes
kubectl get storageclass
```

## 🔄 ArgoCD Commands

```bash
# View applications
kubectl get applications -n argocd

# Describe application
kubectl describe application ecommerce-dev -n argocd

# Get application status
kubectl get application ecommerce-dev -n argocd -o jsonpath='{.status.sync.status}'

# Manual sync
kubectl -n argocd patch application ecommerce-dev -p '{"operation":{"sync":{}}}' --type merge

# Get ArgoCD password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

## 📊 Prometheus/Grafana Commands

```bash
# View monitoring resources
kubectl get all -n monitoring

# Port forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3001:80

# Port forward to Prometheus
kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090:9090

# View ServiceMonitors
kubectl get servicemonitors -n ecommerce-prod
```

## 🛠️ Utility Commands

### Labels and Annotations

```bash
# Add label
kubectl label pods <pod-name> env=production -n ecommerce-dev

# Remove label
kubectl label pods <pod-name> env- -n ecommerce-dev

# Add annotation
kubectl annotate pods <pod-name> description="Backend API" -n ecommerce-dev

# Show labels
kubectl get pods --show-labels -n ecommerce-dev

# Filter by label
kubectl get pods -l app=backend -n ecommerce-dev
```

### Copy Files

```bash
# Copy file to pod
kubectl cp /local/file <pod-name>:/remote/path -n ecommerce-dev

# Copy file from pod
kubectl cp <pod-name>:/remote/file /local/path -n ecommerce-dev
```

### Context and Namespaces

```bash
# View contexts
kubectl config get-contexts

# Switch context
kubectl config use-context minikube

# Set default namespace
kubectl config set-context --current --namespace=ecommerce-dev

# View current context
kubectl config current-context
```

## 🎯 Quick Status Checks

```bash
# Are all pods running?
kubectl get pods -n ecommerce-dev | grep -v Running

# Are all deployments ready?
kubectl get deployments -n ecommerce-dev

# Check service endpoints
kubectl get endpoints -n ecommerce-dev

# Overall health check
kubectl get all -n ecommerce-dev && kubectl get pvc -n ecommerce-dev && kubectl get ingress -n ecommerce-dev
```

## 🚀 Performance Commands

```bash
# Stress test with Apache Bench (from local machine)
ab -n 1000 -c 10 http://localhost:3000/

# Watch pod autoscaling
watch kubectl get hpa -n ecommerce-prod

# Monitor pod creation
watch kubectl get pods -n ecommerce-prod
```

---

## 💡 Pro Tips

1. **Use aliases** for common commands:
   ```bash
   alias k='kubectl'
   alias kgp='kubectl get pods'
   alias kgs='kubectl get svc'
   alias kd='kubectl describe'
   alias kl='kubectl logs -f'
   ```

2. **Use kubectl completion**:
   ```bash
   # Bash
   source <(kubectl completion bash)
   
   # Zsh
   source <(kubectl completion zsh)
   ```

3. **Use kubens/kubectx** for easy namespace/context switching:
   ```bash
   # Install from https://github.com/ahmetb/kubectx
   kubens ecommerce-dev
   kubectx minikube
   ```

4. **Use stern** for multi-pod log tailing:
   ```bash
   # Install from https://github.com/stern/stern
   stern backend -n ecommerce-dev
   ```

5. **Use k9s** for terminal UI:
   ```bash
   # Install from https://k9scli.io/
   k9s -n ecommerce-dev
   ```

---

For more detailed information, refer to the [official Kubernetes documentation](https://kubernetes.io/docs/reference/kubectl/).
