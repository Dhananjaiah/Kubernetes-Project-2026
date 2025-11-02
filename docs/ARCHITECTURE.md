# Architecture Documentation

## System Architecture

### Overview

This is a cloud-native, microservices-based e-commerce application designed to demonstrate production-grade Kubernetes deployments across multiple environments.

## Component Architecture

### 1. Frontend Service

**Technology**: Python Flask
**Port**: 3000
**Responsibilities**:
- Serves web UI
- Communicates with backend API
- Displays product catalog

**Key Features**:
- Responsive web interface
- Health check endpoint
- Environment-aware configuration

### 2. Backend API Service

**Technology**: Python Flask
**Port**: 5000
**Responsibilities**:
- RESTful API for products
- Database operations
- Business logic

**API Endpoints**:
- `GET /api/products` - List all products
- `GET /api/products/<id>` - Get single product
- `GET /api/stats` - Database statistics
- `GET /health` - Health check

**Key Features**:
- Connection pooling
- Retry logic for database connections
- Structured logging
- Health checks

### 3. Database Service

**Technology**: PostgreSQL 15
**Port**: 5432
**Responsibilities**:
- Persistent data storage
- Product catalog management

**Schema**:
```sql
products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10, 2),
    stock INTEGER,
    created_at TIMESTAMP
)
```

## Deployment Architecture

### Development Environment (Minikube)

```
┌──────────────────────────────────────────┐
│           Minikube Node                  │
│  ┌────────────────────────────────────┐  │
│  │     Ingress Controller (NGINX)     │  │
│  └──────────────┬─────────────────────┘  │
│                 │                         │
│  ┌──────────────▼────────┐                │
│  │   Frontend (2 pods)   │                │
│  └──────────────┬────────┘                │
│                 │                         │
│  ┌──────────────▼────────┐                │
│  │   Backend (2 pods)    │                │
│  └──────────────┬────────┘                │
│                 │                         │
│  ┌──────────────▼────────┐                │
│  │   PostgreSQL (1 pod)  │                │
│  │   PersistentVolume    │                │
│  └───────────────────────┘                │
└──────────────────────────────────────────┘
```

### Staging Environment (Kind/Multi-node)

```
┌─────────────────────────────────────────────┐
│            Control Plane                     │
└─────────────────┬───────────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼──────┐          ┌─────────▼────┐
│  Worker 1│          │   Worker 2   │
│          │          │              │
│ Frontend │          │  Frontend    │
│ Backend  │          │  Backend     │
│          │          │  PostgreSQL  │
└──────────┘          └──────────────┘
```

### Production Environment

```
┌────────────────────────────────────────────────┐
│               Load Balancer                    │
└──────────────────┬─────────────────────────────┘
                   │
     ┌─────────────┴────────────────┐
     │                              │
┌────▼──────────┐          ┌────────▼──────────┐
│  Control Plane│          │  Control Plane    │
│      HA       │          │       HA          │
└───────┬───────┘          └────────┬──────────┘
        │                           │
  ┌─────┴───────────────────────────┴─────┐
  │                                       │
┌─▼─────────┐  ┌──────────┐  ┌──────────▼──┐
│ Worker 1  │  │ Worker 2 │  │  Worker 3   │
│           │  │          │  │             │
│ Frontend  │  │ Frontend │  │  Frontend   │
│ Backend   │  │ Backend  │  │  Backend    │
└───────────┘  └──────────┘  │  PostgreSQL │
                              │  (StatefulSet)│
                              └─────────────┘
```

## Network Architecture

### Service Communication

```
External Traffic
       │
       ▼
   Ingress (NGINX)
       │
       ├──► Frontend Service (ClusterIP)
       │         │
       │         ▼
       │    Frontend Pods
       │         │
       │         │ (HTTP)
       │         ▼
       └──► Backend Service (ClusterIP)
                 │
                 ▼
            Backend Pods
                 │
                 │ (PostgreSQL Protocol)
                 ▼
            PostgreSQL Service (Headless)
                 │
                 ▼
            PostgreSQL Pod
```

### Network Policies (Production)

- **Frontend**: Can receive from Ingress, can send to Backend
- **Backend**: Can receive from Frontend, can send to Database
- **Database**: Can receive only from Backend

## Data Flow

### User Request Flow

1. User accesses `https://ecommerce.example.com`
2. Request hits Ingress Controller
3. Ingress routes to Frontend Service
4. Frontend renders page and calls Backend API
5. Backend queries PostgreSQL
6. Response flows back through the stack

### GitOps Flow

1. Developer pushes code to GitHub
2. GitHub Actions builds Docker images
3. Images pushed to Container Registry
4. ArgoCD detects changes in Git
5. ArgoCD syncs to Kubernetes cluster
6. Rolling update deployed

## Scaling Architecture

### Horizontal Pod Autoscaler (HPA)

**Frontend**:
- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

**Backend**:
- Min replicas: 3
- Max replicas: 10
- Target CPU: 70%
- Target Memory: 80%

### Database Scaling

**Development**: Single instance
**Production**: StatefulSet with replication support (future)

## High Availability Design

### Application Layer

- **Multiple Replicas**: Each service runs with 3+ replicas
- **Pod Anti-Affinity**: Pods distributed across nodes
- **Rolling Updates**: Zero-downtime deployments
- **Health Checks**: Liveness and readiness probes

### Database Layer

- **StatefulSet**: Ordered, stable deployment
- **Persistent Volumes**: Data survives pod restarts
- **Backup Strategy**: Regular snapshots (to be implemented)

### Infrastructure Layer

- **Multiple Control Plane Nodes**: HA Kubernetes cluster
- **Multiple Worker Nodes**: Workload distribution
- **Load Balancer**: Traffic distribution

## Security Architecture

### Network Security

- **Network Policies**: Restrict pod-to-pod communication
- **TLS Termination**: HTTPS at ingress
- **Internal Communication**: HTTP within cluster

### Access Control

- **RBAC**: Role-based access control
- **Service Accounts**: Per-application service accounts
- **Secrets Management**: Kubernetes secrets (to be enhanced with Vault)

### Container Security

- **Non-root User**: Containers run as user 1000
- **Read-only Root Filesystem**: Where applicable
- **Dropped Capabilities**: Minimal container capabilities
- **Security Scanning**: Trivy in CI/CD pipeline

## Observability Architecture

### Metrics

- **Prometheus**: Metrics collection
- **ServiceMonitors**: Auto-discovery of services
- **Node Exporter**: Node-level metrics
- **Kube-state-metrics**: Kubernetes object metrics

### Visualization

- **Grafana**: Dashboards and alerting
- **Pre-built Dashboards**: Cluster and application metrics

### Logging (Future Enhancement)

- **EFK Stack**: Elasticsearch, Fluentd, Kibana
- **Loki**: Alternative lightweight logging

### Tracing (Future Enhancement)

- **Jaeger**: Distributed tracing
- **OpenTelemetry**: Instrumentation

## Disaster Recovery

### Backup Strategy

1. **Database Backups**: Daily automated backups
2. **Configuration Backups**: Git repository (GitOps)
3. **Cluster Backups**: etcd snapshots

### Recovery Strategy

1. **Service Failure**: Auto-restart with health checks
2. **Node Failure**: Pod rescheduling to healthy nodes
3. **Cluster Failure**: Restore from backups to new cluster

## Performance Optimization

### Application Level

- **Connection Pooling**: Database connections
- **Caching**: To be implemented (Redis)
- **CDN**: For static assets (future)

### Kubernetes Level

- **Resource Requests/Limits**: Proper sizing
- **HPA**: Automatic scaling
- **Pod Disruption Budgets**: Maintain availability during updates

## Technology Stack

### Application

- **Language**: Python 3.11
- **Framework**: Flask 3.0
- **Database**: PostgreSQL 15
- **Web Server**: Gunicorn

### Infrastructure

- **Orchestration**: Kubernetes 1.25+
- **Container Runtime**: Docker
- **GitOps**: ArgoCD
- **Monitoring**: Prometheus + Grafana
- **Ingress**: NGINX Ingress Controller

### Development

- **Local Dev**: Docker Compose
- **Dev Cluster**: Minikube
- **Test Cluster**: Kind
- **CI/CD**: GitHub Actions

## Future Enhancements

1. **Service Mesh**: Istio for advanced traffic management
2. **Caching Layer**: Redis for performance
3. **API Gateway**: Kong or Ambassador
4. **Message Queue**: RabbitMQ or Kafka for async processing
5. **Advanced Logging**: EFK or Loki stack
6. **Secret Management**: HashiCorp Vault
7. **Database HA**: PostgreSQL replication
8. **Multi-region**: Geo-distributed deployments
