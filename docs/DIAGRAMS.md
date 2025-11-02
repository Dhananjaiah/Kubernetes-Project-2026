# Architecture Diagrams

This document contains ASCII diagrams for the E-Commerce Kubernetes Project architecture.

## Application Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Internet / Users                         │
└───────────────────────────┬─────────────────────────────────────┘
                            │
                            │ HTTPS
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Ingress Controller (NGINX)                   │
│                  - SSL/TLS Termination                          │
│                  - Path-based Routing                           │
│                  - Load Balancing                               │
└────────────┬──────────────────────────────┬─────────────────────┘
             │                              │
             │ HTTP                         │ HTTP
             ▼                              ▼
┌──────────────────────┐          ┌──────────────────────┐
│  Frontend Service    │          │  Backend Service     │
│  (ClusterIP)         │          │  (ClusterIP)         │
└──────────┬───────────┘          └──────────┬───────────┘
           │                                 │
           │ Load Balance                    │ Load Balance
           ▼                                 ▼
┌──────────────────────┐          ┌──────────────────────┐
│  Frontend Pods       │◄────────►│  Backend Pods        │
│  - Python/Flask      │   HTTP   │  - Python/Flask      │
│  - Port 3000         │          │  - Port 5000         │
│  - 2-3 Replicas      │          │  - 2-3 Replicas      │
└──────────────────────┘          └──────────┬───────────┘
                                             │
                                             │ PostgreSQL
                                             │ Protocol
                                             ▼
                                  ┌──────────────────────┐
                                  │  PostgreSQL Service  │
                                  │  (Headless/ClusterIP)│
                                  └──────────┬───────────┘
                                             │
                                             ▼
                                  ┌──────────────────────┐
                                  │  PostgreSQL Pod      │
                                  │  - Port 5432         │
                                  │  - StatefulSet       │
                                  │  - Persistent Volume │
                                  └──────────────────────┘
```

## GitOps Workflow

```
┌──────────────┐
│  Developer   │
└──────┬───────┘
       │ 1. Push Code
       ▼
┌──────────────────┐
│  GitHub Repo     │
│  - Source Code   │
│  - K8s Manifests │
└────┬─────────────┘
     │ 2. Trigger Build
     ▼
┌──────────────────┐
│ GitHub Actions   │
│ - Build Images   │
│ - Run Tests      │
│ - Push to GHCR   │
└────┬─────────────┘
     │ 3. New Image
     ▼
┌──────────────────┐      ┌─────────────────┐
│ Container        │      │  ArgoCD         │
│ Registry (GHCR)  │◄────►│  - Monitors Git │
└──────────────────┘      │  - Auto Sync    │
                          │  - Rollback     │
                          └────┬────────────┘
                               │ 4. Deploy
                               ▼
┌──────────────────────────────────────────┐
│         Kubernetes Cluster               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  │
│  │   Dev   │  │ Staging │  │   Prod  │  │
│  └─────────┘  └─────────┘  └─────────┘  │
└──────────────────────────────────────────┘
```

## Multi-Environment Deployment

```
┌────────────────────────────────────────────────────────────┐
│                     Git Repository                         │
│                                                            │
│  ├── k8s/dev/        (Development)                        │
│  ├── k8s/staging/    (Staging)                            │
│  └── k8s/prod/       (Production)                         │
└────────────────────────────────────────────────────────────┘
                            │
                ┌───────────┼───────────┐
                │           │           │
                ▼           ▼           ▼
┌──────────────────┐ ┌──────────────┐ ┌──────────────────┐
│   Development    │ │   Staging    │ │   Production     │
│   (Minikube)     │ │   (Kind)     │ │   (Kubeadm)      │
│                  │ │              │ │                  │
│ - 1 Node         │ │ - 3 Nodes    │ │ - 5+ Nodes       │
│ - Min Resources  │ │ - 2 Replicas │ │ - 3+ Replicas    │
│ - Auto-sync      │ │ - Auto-sync  │ │ - Manual sync    │
│ - NodePort       │ │ - Ingress    │ │ - Ingress + TLS  │
└──────────────────┘ └──────────────┘ └──────────────────┘
```

## Network Policy (Production)

```
┌────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Ingress Namespace                            │    │
│  │  ┌──────────────────┐                         │    │
│  │  │ Ingress Controller│                        │    │
│  │  └────────┬─────────┘                         │    │
│  └───────────┼──────────────────────────────────┘    │
│              │                                        │
│  ┌───────────┼──────────────────────────────────┐    │
│  │  ecommerce-prod Namespace     │              │    │
│  │           │                    │              │    │
│  │  ┌────────▼────────┐           │              │    │
│  │  │   Frontend      │           │              │    │
│  │  │  Network Policy:│           │              │    │
│  │  │  ✓ From Ingress │           │              │    │
│  │  │  ✓ To Backend   │           │              │    │
│  │  └────────┬────────┘           │              │    │
│  │           │                    │              │    │
│  │           │ ALLOWED            │              │    │
│  │  ┌────────▼────────┐           │              │    │
│  │  │   Backend       │           │              │    │
│  │  │  Network Policy:│           │              │    │
│  │  │  ✓ From Frontend│           │              │    │
│  │  │  ✓ To Database  │           │              │    │
│  │  └────────┬────────┘           │              │    │
│  │           │                    │              │    │
│  │           │ ALLOWED            │              │    │
│  │  ┌────────▼────────┐           │              │    │
│  │  │   Database      │           │              │    │
│  │  │  Network Policy:│           │              │    │
│  │  │  ✓ From Backend │           │              │    │
│  │  │  ✗ Others DENIED│           │              │    │
│  │  └─────────────────┘           │              │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

## High Availability Setup

```
┌───────────────────────────────────────────────────────────┐
│                    Load Balancer                          │
│                   (Cloud/External)                        │
└────────────────────────┬──────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
┌────────────────┐ ┌────────────┐ ┌────────────────┐
│ Control Plane 1│ │Control     │ │ Control Plane 3│
│   (etcd)       │ │Plane 2     │ │   (etcd)       │
│   (API Server) │ │(etcd)      │ │   (API Server) │
└────────────────┘ └────────────┘ └────────────────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌─────────┐         ┌─────────┐         ┌─────────┐
│Worker 1 │         │Worker 2 │         │Worker 3 │
│         │         │         │         │         │
│Frontend │         │Frontend │         │Frontend │
│Backend  │         │Backend  │         │Backend  │
└─────────┘         │Database │         └─────────┘
                    └─────────┘
```

## Pod Scheduling with Anti-Affinity

```
┌─────────────────────────────────────────────────────────┐
│                   Kubernetes Cluster                    │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────┐ │
│  │   Worker 1   │    │   Worker 2   │    │ Worker 3 │ │
│  │              │    │              │    │          │ │
│  │ ┌──────────┐ │    │ ┌──────────┐ │    │┌────────┐│ │
│  │ │Frontend-1│ │    │ │Frontend-2│ │    ││Frontend││ │
│  │ │          │ │    │ │          │ │    ││   -3   ││ │
│  │ └──────────┘ │    │ └──────────┘ │    │└────────┘│ │
│  │              │    │              │    │          │ │
│  │ ┌──────────┐ │    │ ┌──────────┐ │    │┌────────┐│ │
│  │ │Backend-1 │ │    │ │Backend-2 │ │    ││Backend ││ │
│  │ │          │ │    │ │          │ │    ││  -3    ││ │
│  │ └──────────┘ │    │ └──────────┘ │    │└────────┘│ │
│  │              │    │              │    │          │ │
│  └──────────────┘    └──────────────┘    └──────────┘ │
│                                                         │
│  Pod Anti-Affinity Rules:                              │
│  - Frontend pods prefer different nodes                │
│  - Backend pods prefer different nodes                 │
│  - Ensures high availability during node failures      │
└─────────────────────────────────────────────────────────┘
```

## Monitoring Architecture

```
┌────────────────────────────────────────────────────────┐
│                  Kubernetes Cluster                    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Application Namespace                        │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐   │    │
│  │  │ Frontend │  │ Backend  │  │ Database │   │    │
│  │  │   /health│  │  /health │  │          │   │    │
│  │  └─────┬────┘  └─────┬────┘  └─────┬────┘   │    │
│  └────────┼─────────────┼─────────────┼────────┘    │
│           │             │             │             │
│           │ Scrape      │ Scrape      │ Scrape      │
│           │ Metrics     │ Metrics     │ Metrics     │
│           │             │             │             │
│  ┌────────▼─────────────▼─────────────▼────────┐    │
│  │  Monitoring Namespace                        │    │
│  │  ┌───────────────────────────────────┐      │    │
│  │  │      Prometheus                   │      │    │
│  │  │  - Time-series DB                 │      │    │
│  │  │  - Alert Manager                  │      │    │
│  │  │  - Service Discovery              │      │    │
│  │  └────────────┬──────────────────────┘      │    │
│  │               │                             │    │
│  │               │ Query Metrics               │    │
│  │  ┌────────────▼──────────────────────┐      │    │
│  │  │      Grafana                      │      │    │
│  │  │  - Dashboards                     │      │    │
│  │  │  - Visualizations                 │      │    │
│  │  │  - Alerts                         │      │    │
│  │  └───────────────────────────────────┘      │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
                       │
                       │ Access via Ingress
                       ▼
                  ┌─────────┐
                  │  Users  │
                  └─────────┘
```

## Autoscaling Flow

```
┌────────────────────────────────────────────────────┐
│              Horizontal Pod Autoscaler             │
│                                                    │
│  1. Monitor Metrics                                │
│     ├─ CPU Usage                                   │
│     └─ Memory Usage                                │
└──────────────┬─────────────────────────────────────┘
               │
               │ 2. Query Metrics Server
               ▼
┌────────────────────────────────────────────────────┐
│              Metrics Server                        │
│  - Collects resource metrics from nodes/pods      │
└──────────────┬─────────────────────────────────────┘
               │
               │ 3. Returns current metrics
               ▼
┌────────────────────────────────────────────────────┐
│         HPA Decision Engine                        │
│                                                    │
│  IF CPU > 70% OR Memory > 80%                     │
│     THEN scale up (add pods)                      │
│  ELSE IF CPU < 30% AND Memory < 40%               │
│     THEN scale down (remove pods)                 │
└──────────────┬─────────────────────────────────────┘
               │
               │ 4. Scale deployment
               ▼
┌────────────────────────────────────────────────────┐
│              Deployment                            │
│                                                    │
│  Current: 3 pods  ──►  Scaled: 5 pods             │
│                                                    │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐    │
│  │ Pod │  │ Pod │  │ Pod │  │ Pod │  │ Pod │    │
│  │  1  │  │  2  │  │  3  │  │  4  │  │  5  │    │
│  └─────┘  └─────┘  └─────┘  └─────┘  └─────┘    │
└────────────────────────────────────────────────────┘
```

## CI/CD Pipeline Flow

```
┌─────────────────────────────────────────────────────────┐
│  1. Developer Push                                      │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  2. GitHub Actions Triggered                            │
│     ├─ Checkout Code                                    │
│     ├─ Setup Docker Buildx                              │
│     └─ Run Security Scans                               │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  3. Build & Test                                        │
│     ├─ Build Docker Images                              │
│     ├─ Run Unit Tests                                   │
│     └─ Run Integration Tests                            │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  4. Push to Registry                                    │
│     └─ Push to GitHub Container Registry (GHCR)        │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  5. ArgoCD Detection                                    │
│     ├─ Monitors Git repository                          │
│     └─ Detects manifest changes                         │
└────────────┬────────────────────────────────────────────┘
             │
             ▼
┌─────────────────────────────────────────────────────────┐
│  6. Deployment Strategy                                 │
│                                                         │
│     DEV ──────► Auto-sync                              │
│                 Deploy immediately                      │
│                                                         │
│     STAGING ──► Auto-sync                              │
│                 Deploy after tests pass                 │
│                                                         │
│     PROD ─────► Manual approval required               │
│                 Deploy after validation                 │
└─────────────────────────────────────────────────────────┘
```

## Data Persistence

```
┌────────────────────────────────────────────────────────┐
│              PostgreSQL StatefulSet                    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  postgres-0 (Pod)                            │    │
│  │  ├─ PostgreSQL Container                     │    │
│  │  └─ Init Container (wait for volume)         │    │
│  └──────────────┬───────────────────────────────┘    │
│                 │                                     │
│                 │ Mount                               │
│                 ▼                                     │
│  ┌──────────────────────────────────────────────┐    │
│  │  PersistentVolumeClaim (postgres-storage)    │    │
│  │  - Size: 10Gi (Production)                   │    │
│  │  - AccessMode: ReadWriteOnce                 │    │
│  └──────────────┬───────────────────────────────┘    │
│                 │                                     │
│                 │ Bound to                            │
│                 ▼                                     │
│  ┌──────────────────────────────────────────────┐    │
│  │  PersistentVolume                            │    │
│  │  - Storage Class: standard/fast              │    │
│  │  - Reclaim Policy: Retain                    │    │
│  └──────────────┬───────────────────────────────┘    │
│                 │                                     │
│                 ▼                                     │
│  ┌──────────────────────────────────────────────┐    │
│  │  Physical Storage                            │    │
│  │  - Cloud: EBS, GCE PD, Azure Disk           │    │
│  │  - Local: HostPath, NFS                      │    │
│  └──────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────┘
```

## Rolling Update Strategy

```
Time: T0 (Initial State - 3 Pods)
┌─────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌──────┐│
│  │ Pod v1  │  │ Pod v1  │  │Pod v1││
│  └─────────┘  └─────────┘  └──────┘│
└─────────────────────────────────────┘

Time: T1 (Create new pod)
┌──────────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌──────┐     │
│  │ Pod v1  │  │ Pod v1  │  │Pod v1│     │
│  └─────────┘  └─────────┘  └──────┘     │
│                                  ┌──────┐│
│                                  │Pod v2││
│                                  └──────┘│
└──────────────────────────────────────────┘

Time: T2 (Terminate old pod)
┌──────────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐      ┌──────┐ │
│  │ Pod v1  │  │ Pod v1  │      │Pod v2│ │
│  └─────────┘  └─────────┘      └──────┘ │
└──────────────────────────────────────────┘

Time: T3 (Create another new pod)
┌──────────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐      ┌──────┐ │
│  │ Pod v1  │  │ Pod v1  │      │Pod v2│ │
│  └─────────┘  └─────────┘      └──────┘ │
│                           ┌──────┐       │
│                           │Pod v2│       │
│                           └──────┘       │
└──────────────────────────────────────────┘

Time: T4 (Continue until complete)
┌──────────────────────────────────────────┐
│  ┌─────────┐              ┌──────┐       │
│  │ Pod v1  │              │Pod v2│       │
│  └─────────┘              └──────┘       │
│               ┌──────┐                   │
│               │Pod v2│                   │
│               └──────┘                   │
└──────────────────────────────────────────┘

Time: T5 (All pods updated)
┌─────────────────────────────────────┐
│  ┌─────────┐  ┌─────────┐  ┌──────┐│
│  │ Pod v2  │  │ Pod v2  │  │Pod v2││
│  └─────────┘  └─────────┘  └──────┘│
└─────────────────────────────────────┘

Configuration:
- maxSurge: 1 (can have 4 pods during update)
- maxUnavailable: 0 (always maintain 3 pods)
- Zero downtime deployment
```

These diagrams provide visual representations of the various architectural components and workflows in the project.
