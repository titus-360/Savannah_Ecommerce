# Deployment Guide

## Overview

This guide covers the deployment of the Savannah E-commerce Platform using Docker and Kubernetes. The application is designed to be deployed in a containerized environment with proper scaling and monitoring.

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured
- PostgreSQL 15
- Redis 7
- Python 3.12+

## Local Development Deployment

### 1. Using Docker Compose

1. **Build and Start Services**:
   ```bash
   docker-compose up -d
   ```

2. **Run Migrations**:
   ```bash
   docker-compose exec web python manage.py migrate
   ```

3. **Create Superuser**:
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

4. **Collect Static Files**:
   ```bash
   docker-compose exec web python manage.py collectstatic --noinput
   ```

### 2. Environment Configuration

Create a `.env` file:
```env
DEBUG=False
SECRET_KEY=your-secret-key
DB_NAME=savannah_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432
REDIS_URL=redis://redis:6379/0
```

## Production Deployment

### 1. Docker Image

1. **Build Image**:
   ```bash
   docker build -t ghcr.io/yourusername/savannah-ecommerce:latest .
   ```

2. **Push to Registry**:
   ```bash
   docker push ghcr.io/yourusername/savannah-ecommerce:latest
   ```

### 2. Kubernetes Deployment

1. **Create Namespace**:
   ```bash
   kubectl create namespace savannah
   ```

2. **Create Secrets**:
   ```bash
   kubectl create secret generic db-secrets \
       --namespace savannah \
       --from-literal=password=your-db-password
   ```

3. **Apply Configurations**:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   kubectl apply -f k8s/ingress.yaml
   ```

### 3. Database Setup

1. **PostgreSQL**:
   ```bash
   kubectl apply -f k8s/postgres.yaml
   ```

2. **Redis**:
   ```bash
   kubectl apply -f k8s/redis.yaml
   ```

## Monitoring and Logging

### 1. Health Checks

The application includes health check endpoints:
- `/health/`: Overall application health
- `/health/db/`: Database connection
- `/health/cache/`: Redis connection

### 2. Logging

1. **Application Logs**:
   ```bash
   kubectl logs -f deployment/savannah-ecommerce -n savannah
   ```

2. **Database Logs**:
   ```bash
   kubectl logs -f deployment/postgres -n savannah
   ```

### 3. Monitoring

1. **Metrics**:
   - Prometheus metrics available at `/metrics/`
   - Grafana dashboards for visualization

2. **Alerts**:
   - Configure alerting rules in Prometheus
   - Set up notification channels

## Scaling

### 1. Horizontal Pod Autoscaling

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: savannah-ecommerce
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: savannah-ecommerce
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

### 2. Database Scaling

1. **Read Replicas**:
   ```yaml
   apiVersion: apps/v1
   kind: StatefulSet
   metadata:
     name: postgres-replica
   spec:
     replicas: 3
     # ... configuration
   ```

2. **Connection Pooling**:
   - Use PgBouncer for connection pooling
   - Configure in deployment

## Backup and Recovery

### 1. Database Backup

1. **Automated Backups**:
   ```bash
   kubectl apply -f k8s/backup-cronjob.yaml
   ```

2. **Manual Backup**:
   ```bash
   kubectl exec -it postgres-0 -n savannah -- pg_dump -U postgres savannah_db > backup.sql
   ```

### 2. Recovery

1. **Database Recovery**:
   ```bash
   kubectl exec -i postgres-0 -n savannah -- psql -U postgres savannah_db < backup.sql
   ```

2. **Application Recovery**:
   ```bash
   kubectl rollout restart deployment/savannah-ecommerce -n savannah
   ```

## Security

### 1. Network Security

1. **Ingress Configuration**:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: Ingress
   metadata:
     name: savannah-ingress
     annotations:
       kubernetes.io/ingress.class: nginx
       cert-manager.io/cluster-issuer: letsencrypt-prod
   spec:
     tls:
     - hosts:
       - api.savannah.com
       secretName: savannah-tls
     rules:
     - host: api.savannah.com
       http:
         paths:
         - path: /
           pathType: Prefix
           backend:
             service:
               name: savannah-ecommerce
               port:
                 number: 80
   ```

2. **Network Policies**:
   ```yaml
   apiVersion: networking.k8s.io/v1
   kind: NetworkPolicy
   metadata:
     name: savannah-network-policy
   spec:
     podSelector:
       matchLabels:
         app: savannah-ecommerce
     policyTypes:
     - Ingress
     - Egress
     ingress:
     - from:
       - namespaceSelector:
           matchLabels:
             name: ingress-nginx
     egress:
     - to:
       - namespaceSelector:
           matchLabels:
             name: database
   ```

### 2. Secret Management

1. **Kubernetes Secrets**:
   ```bash
   kubectl create secret generic app-secrets \
       --namespace savannah \
       --from-literal=secret-key=your-secret-key \
       --from-literal=db-password=your-db-password
   ```

2. **Environment Variables**:
   ```yaml
   env:
   - name: SECRET_KEY
     valueFrom:
       secretKeyRef:
         name: app-secrets
         key: secret-key
   ```

## Troubleshooting

### 1. Common Issues

1. **Database Connection**:
   ```bash
   # Check database connection
   kubectl exec -it savannah-ecommerce-0 -n savannah -- python manage.py check
   ```

2. **Redis Connection**:
   ```bash
   # Check Redis connection
   kubectl exec -it savannah-ecommerce-0 -n savannah -- python manage.py shell
   >>> from django.core.cache import cache
   >>> cache.set('test', 'value')
   >>> cache.get('test')
   ```

### 2. Debugging

1. **Application Logs**:
   ```bash
   kubectl logs -f deployment/savannah-ecommerce -n savannah
   ```

2. **Database Logs**:
   ```bash
   kubectl logs -f deployment/postgres -n savannah
   ```

## Maintenance

### 1. Updates

1. **Application Update**:
   ```bash
   # Update image
   kubectl set image deployment/savannah-ecommerce \
       savannah-ecommerce=ghcr.io/yourusername/savannah-ecommerce:new-version \
       -n savannah
   ```

2. **Database Migration**:
   ```bash
   kubectl exec -it savannah-ecommerce-0 -n savannah -- python manage.py migrate
   ```

### 2. Monitoring

1. **Resource Usage**:
   ```bash
   kubectl top pods -n savannah
   ```

2. **Performance Metrics**:
   - Check Grafana dashboards
   - Monitor application metrics

## Disaster Recovery

### 1. Backup Strategy

1. **Database Backups**:
   - Daily automated backups
   - Weekly full backups
   - Monthly archives

2. **Configuration Backups**:
   - Version control for configurations
   - Regular backup of secrets

### 2. Recovery Procedures

1. **Database Recovery**:
   ```bash
   # Restore from backup
   kubectl exec -i postgres-0 -n savannah -- psql -U postgres savannah_db < backup.sql
   ```

2. **Application Recovery**:
   ```bash
   # Rollback deployment
   kubectl rollout undo deployment/savannah-ecommerce -n savannah
   ```

## Performance Optimization

### 1. Application

1. **Caching**:
   - Redis for session storage
   - Cache frequently accessed data
   - Use cache headers

2. **Database**:
   - Optimize queries
   - Use indexes
   - Connection pooling

### 2. Infrastructure

1. **Resource Allocation**:
   ```yaml
   resources:
     requests:
       memory: "256Mi"
       cpu: "200m"
     limits:
       memory: "512Mi"
       cpu: "500m"
   ```

2. **Scaling**:
   - Horizontal pod autoscaling
   - Database read replicas
   - Load balancing 