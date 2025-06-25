# Deployment Guide

## Overview

This guide covers deploying Synapse in various environments, from local development to production. The application can be deployed using Docker, Kubernetes, or traditional server deployment.

## Prerequisites

- Python 3.8+
- Redis 6.0+
- MLflow tracking server (optional)
- API keys for external services

## Local Development Deployment

### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd synapse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Start Redis
redis-server

# Start MLflow (optional)
mlflow server --host 0.0.0.0 --port 5000

# Start Synapse
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Environment Variables

Create a `.env` file with the following variables:

```env
# Required API Keys
SLACK_BOT_TOKEN=xoxb-your-slack-bot-token
OPENAI_API_KEY=sk-your-openai-api-key
GITHUB_TOKEN=ghp-your-github-token

# Redis Configuration
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# MLflow Configuration
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=synapse

# OpenAI Configuration
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_MAX_TOKENS=500
OPENAI_TEMPERATURE=0.3

# Cache Configuration
CACHE_TTL=3600
```

## Docker Deployment

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY .env .

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  synapse:
    build: .
    ports:
      - "8000:8000"
    environment:
      - REDIS_HOST=redis
      - MLFLOW_TRACKING_URI=http://mlflow:5000
    depends_on:
      - redis
      - mlflow
    restart: unless-stopped
    volumes:
      - ./logs:/app/logs

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  mlflow:
    image: python:3.9-slim
    ports:
      - "5000:5000"
    environment:
      - MLFLOW_TRACKING_URI=http://localhost:5000
    volumes:
      - mlflow_data:/mlflow
    command: >
      sh -c "pip install mlflow &&
             mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db"
    restart: unless-stopped

volumes:
  redis_data:
  mlflow_data:
```

### Build and Run

```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f synapse

# Stop services
docker-compose down
```

## Kubernetes Deployment

### Namespace

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: synapse
```

### ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: synapse-config
  namespace: synapse
data:
  OPENAI_MODEL: "gpt-4-turbo-preview"
  OPENAI_MAX_TOKENS: "500"
  OPENAI_TEMPERATURE: "0.3"
  MLFLOW_EXPERIMENT_NAME: "synapse"
  CACHE_TTL: "3600"
```

### Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: synapse-secrets
  namespace: synapse
type: Opaque
data:
  SLACK_BOT_TOKEN: <base64-encoded-token>
  OPENAI_API_KEY: <base64-encoded-key>
  GITHUB_TOKEN: <base64-encoded-token>
```

### Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: synapse
  namespace: synapse
spec:
  replicas: 3
  selector:
    matchLabels:
      app: synapse
  template:
    metadata:
      labels:
        app: synapse
    spec:
      containers:
      - name: synapse
        image: your-registry/synapse:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: synapse-config
        - secretRef:
            name: synapse-secrets
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: synapse-service
  namespace: synapse
spec:
  selector:
    app: synapse
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: synapse-ingress
  namespace: synapse
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: synapse.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: synapse-service
            port:
              number: 80
```

## Production Deployment

### Security Considerations

1. **API Key Management**
   - Use Kubernetes secrets or HashiCorp Vault
   - Rotate keys regularly
   - Use least privilege principle

2. **Network Security**
   - Implement TLS/SSL encryption
   - Use API gateway for rate limiting
   - Configure firewall rules

3. **Authentication**
   - Implement API key authentication
   - Consider OAuth2 integration
   - Add request signing

### Performance Optimization

1. **Caching Strategy**
   - Configure Redis persistence
   - Implement cache warming
   - Monitor cache hit rates

2. **Load Balancing**
   - Use multiple Synapse instances
   - Implement health checks
   - Configure auto-scaling

3. **Monitoring**
   - Set up Prometheus metrics
   - Configure Grafana dashboards
   - Implement alerting

### Environment-Specific Configurations

#### Development

```env
LOG_LEVEL=DEBUG
ENVIRONMENT=development
ENABLE_DEBUG_ENDPOINTS=true
```

#### Staging

```env
LOG_LEVEL=INFO
ENVIRONMENT=staging
ENABLE_DEBUG_ENDPOINTS=false
```

#### Production

```env
LOG_LEVEL=WARNING
ENVIRONMENT=production
ENABLE_DEBUG_ENDPOINTS=false
```

## Monitoring and Logging

### Health Check Endpoint

Add to `backend/main.py`:

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }
```

### Logging Configuration

```python
import logging
from logging.config import dictConfig

logging_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout"
        }
    },
    "root": {
        "handlers": ["default"],
        "level": "INFO"
    }
}

dictConfig(logging_config)
```

### Metrics Collection

```python
from prometheus_client import Counter, Histogram, generate_latest

# Define metrics
REQUEST_COUNT = Counter('synapse_requests_total', 'Total requests', ['endpoint', 'status'])
REQUEST_DURATION = Histogram('synapse_request_duration_seconds', 'Request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.labels(
        endpoint=request.url.path,
        status=response.status_code
    ).inc()
    REQUEST_DURATION.observe(duration)
    
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

## Backup and Recovery

### Redis Backup

```bash
# Create backup
redis-cli BGSAVE

# Copy RDB file
cp /var/lib/redis/dump.rdb /backup/redis-$(date +%Y%m%d).rdb
```

### MLflow Backup

```bash
# Backup MLflow database
sqlite3 mlflow.db ".backup /backup/mlflow-$(date +%Y%m%d).db"
```

### Application Data Backup

```bash
# Backup logs and configuration
tar -czf /backup/synapse-$(date +%Y%m%d).tar.gz logs/ .env
```

## Troubleshooting

### Common Issues

1. **Redis Connection Failed**
   - Check Redis service status
   - Verify connection parameters
   - Check firewall settings

2. **API Key Errors**
   - Verify environment variables
   - Check API key permissions
   - Ensure proper encoding

3. **High Memory Usage**
   - Monitor Redis memory usage
   - Check for memory leaks
   - Optimize cache TTL

### Debug Commands

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs synapse

# Test Redis connection
redis-cli ping

# Test API endpoint
curl -X POST http://localhost:8000/agent \
     -H "Content-Type: application/json" \
     -d '{"message": "test"}'
```

## Scaling Considerations

### Horizontal Scaling

- Use load balancer for multiple instances
- Implement session affinity if needed
- Configure shared Redis instance

### Vertical Scaling

- Monitor resource usage
- Adjust CPU/memory limits
- Optimize application performance

### Auto-scaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: synapse-hpa
  namespace: synapse
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: synapse
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
``` 