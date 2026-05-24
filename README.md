# api-gateway

A containerised microservices demo running on **Kubernetes**, using **Kong** as an API gateway to route traffic between independently deployed Python (Flask) services.

---

## Architecture

```
                        ┌─────────────────────────────┐
  HTTP Request  ──────► │   Kong Ingress Controller   │
                        └────────────┬────────────────┘
                                     │
                   ┌─────────────────┼─────────────────┐
                   │                                   │
             /users/*                             /orders/*
                   │                                   │
          ┌────────▼────────┐               ┌──────────▼───────┐
          │   User Service  │               │  Order Service   │
          │   (Flask :5000) │◄──────────────│  (Flask :5001)   │
          └─────────────────┘  validates    └──────────────────┘
                                user_id
```

**Request flow:**
- All external traffic enters through the Kong Ingress
- `/users/*` routes to **User Service** (port 5000)
- `/orders/*` routes to **Order Service** (port 5001)
- Order Service calls User Service internally to validate `user_id` before creating an order

---

## Services

### User Service (`/users`)
Manages a simple in-memory user store.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/users` | List all users |
| `GET` | `/users/<id>` | Get a user by ID |
| `POST` | `/users` | Create a new user |
| `GET` | `/health` | Health check |

### Order Service (`/orders`)
Creates orders linked to existing users. Validates user existence via an internal HTTP call to User Service.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/orders` | Create a new order |
| `GET` | `/orders/<id>` | Get an order by ID |
| `GET` | `/health` | Health check |

---

## Tech Stack

- **Python 3 / Flask** — REST microservices
- **Kong** — API gateway & ingress controller
- **Kubernetes** — container orchestration
- **Docker** — containerisation

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)
- A local Kubernetes cluster ([Minikube](https://minikube.sigs.k8s.io/) or [Kind](https://kind.sigs.k8s.io/))
- [Kong Ingress Controller](https://docs.konghq.com/kubernetes-ingress-controller/latest/deployment/minikube/) installed in your cluster

### 1. Build the Docker images

```bash
docker build -t user-service:latest ./user-service
docker build -t order-service:latest ./order-service
```

If using Minikube, load the images into its registry first:

```bash
minikube image load user-service:latest
minikube image load order-service:latest
```

### 2. Deploy to Kubernetes

```bash
kubectl create namespace demo
kubectl apply -f k8s/user-deployment.yaml -n demo
kubectl apply -f k8s/order-deployment.yaml -n demo
kubectl apply -f k8s/ingress.yaml -n demo
```

### 3. Verify pods are running

```bash
kubectl get pods -n demo
```

All pods should show `Running` with `1/1` ready.

### 4. Get the gateway address

```bash
# Minikube
minikube service -n kong kong-proxy --url

# Or use kubectl port-forward
kubectl port-forward -n kong svc/kong-proxy 8080:80
```

---

## Usage

Replace `<GATEWAY_URL>` with the address from step 4 (e.g. `http://localhost:8080`).

### Create a user

```bash
curl -X POST <GATEWAY_URL>/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
```

```json
{"id": 3, "name": "Alice"}
```

### List all users

```bash
curl <GATEWAY_URL>/users
```

### Create an order

```bash
curl -X POST <GATEWAY_URL>/orders \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "items": ["item-A", "item-B"]}'
```

```json
{"id": 1, "user_id": 1, "items": ["item-A", "item-B"]}
```

### Get an order

```bash
curl <GATEWAY_URL>/orders/1
```

---

## Key Concepts Demonstrated

- **API Gateway pattern** — single entry point for all client traffic, with path-based routing
- **Service-to-service communication** — Order Service calls User Service over the cluster network using Kubernetes DNS (`user-service:5000`)
- **Health probes** — readiness probes on `/health` ensure Kubernetes only routes traffic to healthy pods
- **Environment-based config** — service hostnames and ports injected via environment variables, not hardcoded
- **Namespace isolation** — services deployed into a dedicated `demo` namespace

---

## Project Structure

```
api-gateway/
├── user-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
├── order-service/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
└── k8s/
    ├── user-deployment.yaml
    ├── order-deployment.yaml
    └── ingress.yaml
```

---

## Future Improvements

- [ ] Persistent storage (replace in-memory dicts with PostgreSQL)
- [ ] JWT authentication via Kong plugin
- [ ] Rate limiting via Kong plugin
- [ ] Horizontal pod autoscaling
- [ ] Helm chart for deployment
