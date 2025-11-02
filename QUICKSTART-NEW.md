# Quick Start Guide - Production Microservices

## 🚀 Quick Start with Docker Compose

The fastest way to run the entire microservices platform locally:

```bash
# Clone the repository
git clone https://github.com/Dhananjaiah/Kubernetes-Project-2026.git
cd Kubernetes-Project-2026

# Start all services
docker-compose up --build

# Wait for all services to be healthy (about 1-2 minutes)
```

### Access the Services

Once all services are running:

- **Frontend:** http://localhost:3000
- **API Gateway:** http://localhost:5004
- **Product Service:** http://localhost:5000
- **Auth Service:** http://localhost:5001
- **Order Service:** http://localhost:5002
- **Inventory Service:** http://localhost:5003
- **PostgreSQL:** localhost:5432

## 🧪 Test the APIs

### 1. Check Product Service
```bash
curl http://localhost:5004/api/products
```

### 2. Register a User
```bash
curl -X POST http://localhost:5004/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'
```

### 3. Login and Get JWT Token
```bash
curl -X POST http://localhost:5004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "password123"
  }'
```

Save the `access_token` from the response.

### 4. Create an Order
```bash
curl -X POST http://localhost:5004/api/orders \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "items": [
      {"product_id": 1, "quantity": 2},
      {"product_id": 3, "quantity": 1}
    ],
    "shipping_address": "123 Main St, City, State 12345"
  }'
```

### 5. Check Inventory
```bash
curl http://localhost:5004/api/inventory
```

### 6. Update Product Stock
```bash
curl -X PUT http://localhost:5004/api/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 100,
    "warehouse_location": "Warehouse A"
  }'
```

## 🎯 Kubernetes Deployment (Minikube)

### Prerequisites
- Minikube installed
- kubectl installed
- Docker installed

### Step-by-Step

```bash
# 1. Start Minikube
minikube start --cpus=4 --memory=8192

# 2. Use Minikube's Docker daemon
eval $(minikube docker-env)

# 3. Build all Docker images
cd apps

# Build Product Service
docker build -t backend:latest ./backend

# Build Auth Service
docker build -t auth-service:latest ./auth-service

# Build Order Service
docker build -t order-service:latest ./order-service

# Build Inventory Service
docker build -t inventory-service:latest ./inventory-service

# Build API Gateway
docker build -t api-gateway:latest ./api-gateway

# Build Frontend
docker build -t frontend:latest ./frontend

cd ..

# 4. Deploy to Kubernetes
kubectl apply -f k8s/dev/

# 5. Wait for all pods to be ready
kubectl get pods -n ecommerce-dev -w

# 6. Access the application
minikube service frontend-service -n ecommerce-dev
```

### Verify Deployment

```bash
# Check all services
kubectl get all -n ecommerce-dev

# Check service endpoints
kubectl get endpoints -n ecommerce-dev

# Check logs
kubectl logs -f deployment/backend -n ecommerce-dev
kubectl logs -f deployment/auth-service -n ecommerce-dev
kubectl logs -f deployment/order-service -n ecommerce-dev
kubectl logs -f deployment/inventory-service -n ecommerce-dev
kubectl logs -f deployment/api-gateway -n ecommerce-dev
kubectl logs -f deployment/frontend -n ecommerce-dev
```

## 🔧 Development Mode

### Run Individual Services Locally

Each service can be run independently for development:

#### Backend/Product Service
```bash
cd apps/backend
pip install -r requirements.txt
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=ecommerce
export DB_USER=postgres
export DB_PASSWORD=postgres
python wsgi.py
```

#### Auth Service
```bash
cd apps/auth-service
pip install -r requirements.txt
export DB_HOST=localhost
export JWT_SECRET_KEY=dev-secret
python wsgi.py
```

#### Order Service
```bash
cd apps/order-service
pip install -r requirements.txt
export DB_HOST=localhost
export PRODUCT_SERVICE_URL=http://localhost:5000
export INVENTORY_SERVICE_URL=http://localhost:5003
python wsgi.py
```

#### Inventory Service
```bash
cd apps/inventory-service
pip install -r requirements.txt
export DB_HOST=localhost
python wsgi.py
```

#### API Gateway
```bash
cd apps/api-gateway
pip install -r requirements.txt
export PRODUCT_SERVICE_URL=http://localhost:5000
export AUTH_SERVICE_URL=http://localhost:5001
export ORDER_SERVICE_URL=http://localhost:5002
export INVENTORY_SERVICE_URL=http://localhost:5003
python wsgi.py
```

#### Frontend
```bash
cd apps/frontend
pip install -r requirements.txt
export API_GATEWAY_URL=http://localhost:5004
python wsgi.py
```

## 📊 Monitoring

### Health Checks

All services expose health endpoints:

```bash
# Product Service
curl http://localhost:5000/health

# Auth Service
curl http://localhost:5001/health

# Order Service
curl http://localhost:5002/health

# Inventory Service
curl http://localhost:5003/health

# API Gateway
curl http://localhost:5004/health

# Frontend
curl http://localhost:3000/health
```

### Database Access

```bash
# Using Docker Compose
docker exec -it ecommerce-db psql -U postgres -d ecommerce

# Using Kubernetes
kubectl exec -it postgres-0 -n ecommerce-dev -- psql -U postgres -d ecommerce
```

Useful queries:
```sql
-- List all products
SELECT * FROM products;

-- List all users
SELECT id, username, email, is_active FROM users;

-- List all orders
SELECT * FROM orders;

-- List all inventory
SELECT * FROM inventory;

-- Check order details
SELECT o.*, oi.* 
FROM orders o 
JOIN order_items oi ON o.id = oi.order_id;
```

## 🐛 Troubleshooting

### Services not starting

```bash
# Check container logs
docker-compose logs backend
docker-compose logs auth-service
docker-compose logs order-service

# Or in Kubernetes
kubectl logs deployment/backend -n ecommerce-dev
```

### Database connection issues

```bash
# Test database connection
docker exec -it ecommerce-db pg_isready -U postgres

# Check database exists
docker exec -it ecommerce-db psql -U postgres -l
```

### Port conflicts

```bash
# Check what's using the ports
lsof -i :3000  # Frontend
lsof -i :5000  # Product Service
lsof -i :5001  # Auth Service
lsof -i :5002  # Order Service
lsof -i :5003  # Inventory Service
lsof -i :5004  # API Gateway
lsof -i :5432  # PostgreSQL

# Kill processes if needed
kill -9 <PID>
```

### Clean restart

```bash
# Docker Compose
docker-compose down -v
docker-compose up --build

# Kubernetes
kubectl delete namespace ecommerce-dev
kubectl apply -f k8s/dev/
```

## 📚 Next Steps

1. **Explore the API**: Use the API examples above to interact with each service
2. **Read the Architecture**: Check out [ARCHITECTURE.md](ARCHITECTURE.md) for detailed documentation
3. **Deploy to Production**: See production deployment guides in [DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)
4. **Set up Monitoring**: Install Prometheus and Grafana using scripts in `scripts/`
5. **Configure GitOps**: Set up ArgoCD for automated deployments

## 🆘 Need Help?

- **Architecture Details**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Full Documentation**: [README.md](README.md)
- **Deployment Guide**: [docs/DEPLOYMENT-GUIDE.md](docs/DEPLOYMENT-GUIDE.md)
- **Commands Reference**: [docs/COMMANDS-REFERENCE.md](docs/COMMANDS-REFERENCE.md)

Happy coding! 🚀
