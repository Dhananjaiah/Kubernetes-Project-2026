# Migration Guide - From Monolith to Microservices

## Overview

This guide explains the transformation from the original single-file microservices to the current production-grade architecture.

## What Changed?

### Before (Original Architecture)

```
apps/
├── backend/
│   └── app.py          # Single file with all logic
├── frontend/
│   └── app.py          # Single file with all logic
└── database/
    └── init.sql
```

**Problems:**
- All code in single files
- No separation of concerns
- Hard to test and maintain
- Not scalable
- Limited functionality

### After (New Architecture)

```
apps/
├── backend/              # Product Service
│   ├── app/
│   │   ├── api/         # Routes
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   ├── middleware/  # Logging, errors
│   │   └── config/      # Configuration
│   └── wsgi.py
├── auth-service/         # NEW: Authentication
├── order-service/        # NEW: Order management
├── inventory-service/    # NEW: Stock management
├── api-gateway/          # NEW: Centralized routing
└── frontend/             # Restructured UI
```

## Key Improvements

### 1. Proper Code Structure

**Each service now has:**
- `api/` - API routes and endpoints
- `models/` - Data models and schemas
- `services/` - Business logic layer
- `middleware/` - Cross-cutting concerns
- `config/` - Environment configuration

### 2. New Microservices

#### Auth Service (Port 5001)
- User registration
- JWT authentication
- Password hashing
- Token validation

#### Order Service (Port 5002)
- Order creation
- Order tracking
- Integration with product/inventory

#### Inventory Service (Port 5003)
- Stock management
- Inventory reservation
- Warehouse tracking

#### API Gateway (Port 5004)
- Centralized routing
- Rate limiting
- Request logging
- Error handling

### 3. Production Patterns

**Application Factory Pattern:**
```python
def create_app(config_name=None):
    app = Flask(__name__)
    config = get_config(config_name)
    # Setup...
    return app
```

**Service Layer Pattern:**
```python
# Separation of concerns
API Layer → Service Layer → Data Layer
```

**Configuration Management:**
```python
# Environment-based config
config_by_name = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}
```

## Breaking Changes

### Backend API

**Old:**
```python
# Single app.py file
from flask import Flask
app = Flask(__name__)

@app.route('/api/products')
def get_products():
    # All logic here
```

**New:**
```python
# apps/backend/app/api/products.py
from flask import Blueprint
products_bp = Blueprint('products', __name__)

@products_bp.route('/products')
def get_products():
    service = get_product_service()
    return service.get_all_products()
```

### Frontend

**Old:**
```python
# Single app.py with inline HTML
HTML_TEMPLATE = '''<!DOCTYPE html>...'''
```

**New:**
```python
# apps/frontend/app/api/views.py
from flask import render_template

@views_bp.route('/')
def index():
    return render_template('index.html', ...)
```

### Database Connection

**Old:**
```python
# Direct connection in routes
conn = psycopg2.connect(...)
```

**New:**
```python
# Managed by DatabaseService
class DatabaseService:
    @contextmanager
    def get_cursor(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except:
            conn.rollback()
            raise
```

## Migration Steps

### For Developers

1. **Update dependencies:**
   ```bash
   # Each service has its own requirements.txt
   pip install -r apps/backend/requirements.txt
   pip install -r apps/auth-service/requirements.txt
   # etc.
   ```

2. **Update environment variables:**
   ```bash
   # Old
   export BACKEND_URL=http://backend:5000
   
   # New
   export API_GATEWAY_URL=http://api-gateway:5004
   export PRODUCT_SERVICE_URL=http://backend:5000
   export AUTH_SERVICE_URL=http://auth-service:5001
   export ORDER_SERVICE_URL=http://order-service:5002
   export INVENTORY_SERVICE_URL=http://inventory-service:5003
   ```

3. **Update Docker builds:**
   ```bash
   # Build all new services
   docker build -t backend:latest ./apps/backend
   docker build -t auth-service:latest ./apps/auth-service
   docker build -t order-service:latest ./apps/order-service
   docker build -t inventory-service:latest ./apps/inventory-service
   docker build -t api-gateway:latest ./apps/api-gateway
   docker build -t frontend:latest ./apps/frontend
   ```

### For Operations

1. **Update Kubernetes manifests:**
   - New service deployments added
   - Updated secrets for JWT
   - Service mesh configuration

2. **Update CI/CD:**
   - Build pipeline now uses matrix strategy
   - Builds all 6 services in parallel
   - Updated image tags

3. **Database migrations:**
   - New tables: `users`, `orders`, `order_items`, `inventory`
   - Existing `products` table unchanged

## API Changes

### New Endpoints

#### Auth Service
```
POST /api/auth/register      # Register user
POST /api/auth/login         # Get JWT token
GET  /api/auth/me            # Get current user
POST /api/auth/validate      # Validate token
```

#### Order Service
```
POST /api/orders             # Create order
GET  /api/orders/{id}        # Get order
GET  /api/orders/user/{id}   # User orders
PUT  /api/orders/{id}/status # Update status
```

#### Inventory Service
```
GET  /api/inventory                     # List all
GET  /api/inventory/{product_id}        # Get one
PUT  /api/inventory/{product_id}        # Update
POST /api/inventory/{product_id}/reserve # Reserve
POST /api/inventory/{product_id}/release # Release
POST /api/inventory/{product_id}/adjust  # Adjust
```

### Modified Endpoints

Product Service (Backend) - **No breaking changes**
```
GET    /api/products         # List products (unchanged)
GET    /api/products/{id}    # Get product (unchanged)
POST   /api/products         # Create product (NEW)
PUT    /api/products/{id}    # Update product (NEW)
DELETE /api/products/{id}    # Delete product (NEW)
GET    /api/stats            # Statistics (unchanged)
```

## Testing the Migration

### 1. Test Docker Compose
```bash
docker-compose up --build
# Should start all 6 services + database
```

### 2. Test Health Checks
```bash
curl http://localhost:5000/health  # Product Service
curl http://localhost:5001/health  # Auth Service
curl http://localhost:5002/health  # Order Service
curl http://localhost:5003/health  # Inventory Service
curl http://localhost:5004/health  # API Gateway
curl http://localhost:3000/health  # Frontend
```

### 3. Test API Flow
```bash
# 1. Get products (through gateway)
curl http://localhost:5004/api/products

# 2. Register user
curl -X POST http://localhost:5004/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"test","email":"test@example.com","password":"password123"}'

# 3. Login
curl -X POST http://localhost:5004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"test","password":"password123"}'

# 4. Create order
curl -X POST http://localhost:5004/api/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id":1,"items":[{"product_id":1,"quantity":2}],"shipping_address":"123 Main St"}'
```

### 4. Test Kubernetes
```bash
# Deploy
kubectl apply -f k8s/dev/

# Check status
kubectl get pods -n ecommerce-dev

# Test connectivity
kubectl port-forward svc/frontend-service 3000:3000 -n ecommerce-dev
```

## Rollback Plan

If needed, you can rollback to the original architecture:

1. **Keep old app.py files:**
   - Backed up as `app.py.old` in each service

2. **Use old Kubernetes manifests:**
   ```bash
   git checkout <previous-commit> k8s/
   kubectl apply -f k8s/dev/
   ```

3. **Use old Docker Compose:**
   ```bash
   git checkout <previous-commit> docker-compose.yml
   docker-compose up
   ```

## Support

- **Architecture Documentation:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Quick Start Guide:** [QUICKSTART-NEW.md](QUICKSTART-NEW.md)
- **Main README:** [README.md](README.md)

## Checklist

- [ ] Read ARCHITECTURE.md
- [ ] Update local environment variables
- [ ] Rebuild Docker images
- [ ] Test with Docker Compose
- [ ] Test with Kubernetes
- [ ] Update CI/CD pipelines
- [ ] Train team on new structure
- [ ] Update monitoring dashboards
- [ ] Document custom changes

## Next Steps

1. Review the new architecture
2. Run through the Quick Start guide
3. Test all API endpoints
4. Deploy to staging environment
5. Monitor for issues
6. Deploy to production

The new architecture is designed to be:
- **Scalable:** Each service scales independently
- **Maintainable:** Clear separation of concerns
- **Testable:** Isolated components
- **Production-ready:** Industry best practices
- **Extensible:** Easy to add new services

Happy migrating! 🚀
