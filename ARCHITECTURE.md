# Production-Grade Microservices Architecture

## Overview

This project demonstrates a real-world, production-ready microservices architecture built with Python Flask and designed for Kubernetes deployment.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                          Ingress / Load Balancer                    │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                   ┌─────────▼──────────┐
                   │     Frontend       │
                   │  (Flask + HTML)    │
                   │    Port: 3000      │
                   └─────────┬──────────┘
                             │
                   ┌─────────▼──────────┐
                   │   API Gateway      │
                   │  (Flask + Proxy)   │
                   │    Port: 5004      │
                   └──┬──┬──┬──┬────────┘
                      │  │  │  │
        ┌─────────────┘  │  │  └─────────────┐
        │                │  │                │
┌───────▼──────┐  ┌──────▼──────┐  ┌────────▼──────┐  ┌──────────────┐
│   Product    │  │    Auth     │  │    Order      │  │  Inventory   │
│   Service    │  │   Service   │  │   Service     │  │   Service    │
│ Port: 5000   │  │ Port: 5001  │  │ Port: 5002    │  │ Port: 5003   │
└──────┬───────┘  └──────┬──────┘  └───────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       └─────────────────┴─────────────────┴─────────────────┘
                                 │
                        ┌────────▼────────┐
                        │   PostgreSQL    │
                        │   Database      │
                        │   Port: 5432    │
                        └─────────────────┘
```

## Microservices

### 1. Product Service (Backend)
**Port:** 5000  
**Path:** `apps/backend/`

**Responsibilities:**
- Product catalog management
- CRUD operations for products
- Product search and filtering
- Product statistics

**API Endpoints:**
- `GET /api/products` - List all products
- `GET /api/products/{id}` - Get product by ID
- `POST /api/products` - Create new product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `GET /api/stats` - Get product statistics

**Database Tables:**
- `products` - Product information with stock levels

### 2. Auth Service
**Port:** 5001  
**Path:** `apps/auth-service/`

**Responsibilities:**
- User registration and authentication
- JWT token generation and validation
- User session management
- Password hashing with bcrypt

**API Endpoints:**
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Authenticate user (returns JWT)
- `GET /api/auth/me` - Get current user info (requires JWT)
- `POST /api/auth/validate` - Validate JWT token

**Database Tables:**
- `users` - User accounts with hashed passwords

**Security Features:**
- JWT-based authentication
- Bcrypt password hashing
- Token expiration (1 hour access, 30 days refresh)

### 3. Order Service
**Port:** 5002  
**Path:** `apps/order-service/`

**Responsibilities:**
- Order creation and management
- Order status tracking
- Integration with Product and Inventory services
- Order history

**API Endpoints:**
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get order by ID
- `GET /api/orders/user/{user_id}` - Get user orders
- `PUT /api/orders/{id}/status` - Update order status

**Database Tables:**
- `orders` - Order information
- `order_items` - Individual items in orders

**Business Logic:**
- Validates products exist before creating order
- Calculates order totals
- Tracks order lifecycle (pending → confirmed → shipped → delivered)

### 4. Inventory Service
**Port:** 5003  
**Path:** `apps/inventory-service/`

**Responsibilities:**
- Stock level management
- Inventory reservation for orders
- Warehouse location tracking
- Stock adjustments

**API Endpoints:**
- `GET /api/inventory` - List all inventory
- `GET /api/inventory/{product_id}` - Get inventory for product
- `PUT /api/inventory/{product_id}` - Update inventory
- `POST /api/inventory/{product_id}/reserve` - Reserve stock
- `POST /api/inventory/{product_id}/release` - Release reserved stock
- `POST /api/inventory/{product_id}/adjust` - Adjust stock levels

**Database Tables:**
- `inventory` - Stock levels with reserved quantities

**Features:**
- Real-time stock tracking
- Reserved vs. available quantities
- Automatic availability calculation

### 5. API Gateway
**Port:** 5004  
**Path:** `apps/api-gateway/`

**Responsibilities:**
- Single entry point for all microservices
- Request routing and load balancing
- Rate limiting
- Request/response logging
- CORS handling

**Features:**
- Intelligent routing to backend services
- Rate limiting (100 requests/minute by default)
- Timeout handling (10 seconds default)
- Error handling and retry logic
- Service health monitoring

**Routing:**
- `/api/products/*` → Product Service
- `/api/auth/*` → Auth Service
- `/api/orders/*` → Order Service
- `/api/inventory/*` → Inventory Service

### 6. Frontend Service
**Port:** 3000  
**Path:** `apps/frontend/`

**Responsibilities:**
- User interface
- Product display
- Shopping cart (UI only)
- API Gateway integration

**Features:**
- Modern responsive design
- Real-time product listing
- Stock availability display
- Service status monitoring

## Technology Stack

### Backend Services
- **Framework:** Flask 3.0.0
- **Database Driver:** psycopg2-binary 2.9.9
- **WSGI Server:** Gunicorn 21.2.0
- **Auth:** Flask-JWT-Extended 4.5.3
- **Password Hashing:** bcrypt 4.1.1

### API Gateway
- **Rate Limiting:** Flask-Limiter 3.5.0
- **HTTP Client:** requests 2.31.0

### Frontend
- **Template Engine:** Jinja2 (Flask built-in)
- **HTTP Client:** requests 2.31.0

### Database
- **RDBMS:** PostgreSQL 15

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Kubernetes
- **GitOps:** ArgoCD
- **Monitoring:** Prometheus + Grafana

## Project Structure

```
apps/
├── backend/              # Product Service
│   ├── app/
│   │   ├── api/         # API routes
│   │   ├── models/      # Data models
│   │   ├── services/    # Business logic
│   │   ├── middleware/  # Logging, error handling
│   │   └── config/      # Configuration management
│   ├── Dockerfile
│   ├── requirements.txt
│   └── wsgi.py
│
├── auth-service/         # Authentication Service
│   ├── app/
│   │   ├── api/         # Auth endpoints
│   │   ├── models/      # User model
│   │   ├── services/    # Auth logic
│   │   └── config/
│   └── ...
│
├── order-service/        # Order Management Service
│   ├── app/
│   │   ├── api/         # Order endpoints
│   │   ├── models/      # Order, OrderItem models
│   │   ├── services/    # Order logic
│   │   └── config/
│   └── ...
│
├── inventory-service/    # Inventory Management Service
│   ├── app/
│   │   ├── api/         # Inventory endpoints
│   │   ├── models/      # Inventory model
│   │   ├── services/    # Inventory logic
│   │   └── config/
│   └── ...
│
├── api-gateway/          # API Gateway
│   ├── app/
│   │   ├── routes/      # Routing logic
│   │   ├── middleware/  # Rate limiting, CORS
│   │   └── config/
│   └── ...
│
└── frontend/             # Web UI
    ├── app/
    │   ├── api/         # View routes
    │   ├── templates/   # HTML templates
    │   ├── static/      # CSS, JS
    │   └── config/
    └── ...
```

## Design Patterns

### 1. Application Factory Pattern
Each service uses Flask's application factory pattern for configuration flexibility.

```python
def create_app(config_name=None):
    app = Flask(__name__)
    config = get_config(config_name)
    app.config.from_object(config)
    # Setup middleware, routes, etc.
    return app
```

### 2. Service Layer Pattern
Business logic is separated from API routes:
- **API Layer**: Request handling, validation, response formatting
- **Service Layer**: Business logic, data processing
- **Model Layer**: Data structures and database interactions

### 3. Configuration Management
Environment-specific configuration:
- Development
- Staging  
- Production

### 4. Dependency Injection
Services receive their dependencies (like database connections) via constructor injection.

### 5. API Gateway Pattern
Single entry point for all client requests:
- Centralized routing
- Rate limiting
- Authentication check (future)
- Request/response transformation

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    stock INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER,
    status VARCHAR(20) DEFAULT 'pending',
    total_amount DECIMAL(10, 2) NOT NULL,
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
    product_id INTEGER NOT NULL,
    product_name VARCHAR(255),
    quantity INTEGER NOT NULL,
    price DECIMAL(10, 2) NOT NULL
);
```

### Inventory Table
```sql
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INTEGER UNIQUE NOT NULL,
    quantity INTEGER NOT NULL DEFAULT 0,
    reserved INTEGER NOT NULL DEFAULT 0,
    available INTEGER GENERATED ALWAYS AS (quantity - reserved) STORED,
    warehouse_location VARCHAR(100),
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Running Locally

### Using Docker Compose (Recommended for Local Development)

```bash
# Build and start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost:3000
# API Gateway: http://localhost:5004
# Product Service: http://localhost:5000
# Auth Service: http://localhost:5001
# Order Service: http://localhost:5002
# Inventory Service: http://localhost:5003
```

### Using Kubernetes (Minikube)

```bash
# Start Minikube
minikube start --cpus=4 --memory=8192

# Build images in Minikube's Docker environment
eval $(minikube docker-env)
cd apps
for service in backend auth-service order-service inventory-service api-gateway frontend; do
    docker build -t $service:latest ./$service
done

# Deploy to Kubernetes
kubectl apply -f k8s/dev/

# Access frontend
minikube service frontend-service -n ecommerce-dev
```

## API Examples

### Register User
```bash
curl -X POST http://localhost:5004/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST http://localhost:5004/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "secure_password_123"
  }'
```

### Create Order
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

### Update Inventory
```bash
curl -X PUT http://localhost:5004/api/inventory/1 \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 100,
    "warehouse_location": "Warehouse A, Shelf B-12"
  }'
```

## Production Considerations

### Security
1. **Secrets Management**: Use Kubernetes Secrets or Vault for sensitive data
2. **JWT Security**: Rotate keys regularly, use short expiration times
3. **Network Policies**: Restrict inter-service communication
4. **TLS/SSL**: Enable HTTPS for all external endpoints
5. **Rate Limiting**: Prevent abuse via API Gateway

### Scalability
1. **Horizontal Pod Autoscaling**: Scale services based on CPU/memory
2. **Database Connection Pooling**: Optimize database connections
3. **Caching**: Add Redis for frequently accessed data
4. **Read Replicas**: Use PostgreSQL read replicas for queries

### Observability
1. **Logging**: Centralized logging with ELK stack
2. **Metrics**: Prometheus metrics for each service
3. **Tracing**: Distributed tracing with Jaeger
4. **Monitoring**: Grafana dashboards for visualization

### High Availability
1. **Multiple Replicas**: Run at least 3 replicas in production
2. **Pod Anti-Affinity**: Spread pods across nodes
3. **Health Checks**: Proper liveness and readiness probes
4. **Database HA**: PostgreSQL with replication

### CI/CD
1. **Automated Testing**: Unit, integration, and E2E tests
2. **Image Scanning**: Scan Docker images for vulnerabilities
3. **GitOps**: ArgoCD for declarative deployments
4. **Rollback Strategy**: Blue-green or canary deployments

## Future Enhancements

1. **Service Mesh**: Implement Istio or Linkerd
2. **Event-Driven Architecture**: Add message queue (RabbitMQ/Kafka)
3. **Notification Service**: Email and SMS notifications
4. **Payment Service**: Payment gateway integration
5. **Search Service**: Elasticsearch for advanced search
6. **Analytics Service**: Real-time analytics and reporting
7. **GraphQL API**: Alternative to REST API
8. **WebSocket Support**: Real-time updates

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines.

## License

MIT License - See [LICENSE](LICENSE) for details.
