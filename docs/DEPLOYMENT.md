# Deployment Guide

This guide covers the deployment of the Savannah E-commerce platform using Docker and Kubernetes.

## Prerequisites

- Docker and Docker Compose
- Kubernetes cluster (e.g., Minikube, GKE, EKS)
- kubectl configured
- Container registry access (e.g., GitHub Container Registry)
- Google Cloud Platform account for OAuth2

## Environment Variables

Create a `.env` file for production:

```env
# Django settings
DEBUG=False
SECRET_KEY=your-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DB_NAME=savannah_db
DB_USER=postgres
DB_PASSWORD=secure-password
DB_HOST=postgres
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# SMS (Africa's Talking)
AT_USERNAME=your-username
AT_API_KEY=your-api-key

# Google OAuth2
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-client-secret
SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE=['email', 'profile']
SOCIAL_AUTH_GOOGLE_OAUTH2_AUTH_EXTRA_ARGUMENTS={'access_type': 'offline'}

# OAuth2 Provider
OAUTH2_CLIENT_ID=your-client-id
OAUTH2_CLIENT_SECRET=your-client-secret
```

## Google OAuth2 Setup

1. Go to the [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select an existing one
3. Enable the Google+ API
4. Go to Credentials
5. Create OAuth 2.0 Client ID
6. Add authorized redirect URIs:
   - `https://your-domain.com/complete/google-oauth2/`
   - `https://www.your-domain.com/complete/google-oauth2/`
7. Copy the Client ID and Client Secret to your `.env` file

## Docker Deployment

### 1. Build the Docker Image

```bash
docker build -t ghcr.io/yourusername/savannah-ecommerce:latest .
```

### 2. Push to Container Registry

```bash
docker push ghcr.io/yourusername/savannah-ecommerce:latest
```

### 3. Run with Docker Compose

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace savannah
```

### 2. Create Secrets

```bash
kubectl create secret generic django-secrets \
    --namespace savannah \
    --from-literal=SECRET_KEY=your-secret-key \
    --from-literal=DB_PASSWORD=your-db-password \
    --from-literal=EMAIL_HOST_PASSWORD=your-email-password \
    --from-literal=AT_API_KEY=your-at-api-key \
    --from-literal=OAUTH2_CLIENT_SECRET=your-oauth2-secret \
    --from-literal=GOOGLE_OAUTH2_SECRET=your-google-secret
```

### 3. Create ConfigMap

```bash
kubectl create configmap django-settings \
    --namespace savannah \
    --from-literal=DEBUG=False \
    --from-literal=ALLOWED_HOSTS=your-domain.com,www.your-domain.com \
    --from-literal=DB_NAME=savannah_db \
    --from-literal=DB_USER=postgres \
    --from-literal=DB_HOST=postgres \
    --from-literal=DB_PORT=5432 \
    --from-literal=REDIS_URL=redis://redis:6379/0
```

### 4. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgres.yaml
```

### 5. Deploy Redis

```bash
kubectl apply -f k8s/redis.yaml
```

### 6. Deploy Application

```bash
kubectl apply -f k8s/deployment.yaml
```

### 7. Deploy Service

```bash
kubectl apply -f k8s/service.yaml
```

### 8. Deploy Ingress (if using)

```bash
kubectl apply -f k8s/ingress.yaml
```

## Health Checks

The application includes health check endpoints:

- `/health/`: Overall application health
- `/health/db/`: Database connection
- `/health/cache/`: Redis cache
- `/health/disk/`: Disk space

## Monitoring

### 1. Set up Prometheus

```bash
kubectl apply -f k8s/monitoring/prometheus.yaml
```

### 2. Set up Grafana

```bash
kubectl apply -f k8s/monitoring/grafana.yaml
```

### 3. Configure Logging

```bash
kubectl apply -f k8s/logging/fluentd.yaml
```

## Backup and Restore

### Database Backup

```bash
kubectl exec -it $(kubectl get pod -l app=postgres -n savannah -o jsonpath="{.items[0].metadata.name}") -n savannah -- \
    pg_dump -U postgres savannah_db > backup.sql
```

### Database Restore

```bash
kubectl exec -i $(kubectl get pod -l app=postgres -n savannah -o jsonpath="{.items[0].metadata.name}") -n savannah -- \
    psql -U postgres savannah_db < backup.sql
```

## Scaling

### Horizontal Pod Autoscaling

```bash
kubectl apply -f k8s/autoscaling.yaml
```

This will automatically scale the application based on CPU usage.

## SSL/TLS Configuration

### 1. Create TLS Secret

```bash
kubectl create secret tls savannah-tls \
    --namespace savannah \
    --cert=path/to/cert.pem \
    --key=path/to/key.pem
```

### 2. Update Ingress

```bash
kubectl apply -f k8s/ingress-tls.yaml
```

## Maintenance

### Database Migrations

```bash
kubectl exec -it $(kubectl get pod -l app=savannah-ecommerce -n savannah -o jsonpath="{.items[0].metadata.name}") -n savannah -- \
    python manage.py migrate
```

### Collect Static Files

```bash
kubectl exec -it $(kubectl get pod -l app=savannah-ecommerce -n savannah -o jsonpath="{.items[0].metadata.name}") -n savannah -- \
    python manage.py collectstatic --noinput
```

## Troubleshooting

### Check Pod Logs

```bash
kubectl logs -f $(kubectl get pod -l app=savannah-ecommerce -n savannah -o jsonpath="{.items[0].metadata.name}") -n savannah
```

### Check Pod Status

```bash
kubectl get pods -n savannah
```

### Check Service Status

```bash
kubectl get services -n savannah
```

### Check Ingress Status

```bash
kubectl get ingress -n savannah
```

## Security Considerations

1. Always use HTTPS in production
2. Keep secrets secure and rotate them regularly
3. Implement proper network policies
4. Use resource limits and requests
5. Enable security contexts
6. Regular security updates
7. Monitor for suspicious activities

## Disaster Recovery

1. Regular database backups
2. Document recovery procedures
3. Test recovery procedures regularly
4. Maintain backup of configuration files
5. Keep deployment manifests in version control
