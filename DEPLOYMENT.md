# Deployment Guide

## Overview

This guide covers deploying Tesseract SaaS MVP to production environments with security, scalability, and reliability best practices.

## Prerequisites

- Docker and Docker Compose installed
- Domain name with DNS configured
- SSL/TLS certificates (Let's Encrypt recommended)
- Production database server
- Redis instance
- AWS account (for S3 and SQS)
- Monitoring and logging infrastructure

## Deployment Options

### Option 1: Docker Compose (Recommended for MVP)

Best for: Small to medium deployments, single server

### Option 2: Kubernetes

Best for: Large scale deployments, multi-region

### Option 3: Cloud Platforms

Best for: Quick deployment with managed services
- AWS ECS/Fargate
- Google Cloud Run
- Azure Container Instances

## Docker Compose Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt-get update && sudo apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Create application user
sudo useradd -m -s /bin/bash tesseract
sudo usermod -aG docker tesseract
```

### 2. Application Setup

```bash
# Clone repository
su - tesseract
git clone <repository-url>
cd tesseract

# Checkout production branch
git checkout main  # or your production branch
```

### 3. Environment Configuration

```bash
# Copy production environment template
cp .env.production.example .env.production

# Edit with secure values
nano .env.production
```

**Critical: Update these values:**

```bash
# Generate strong secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate API keys
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 4. Database Setup

```bash
# Start database only
docker compose -f docker-compose.prod.yml up -d postgres

# Wait for database to be ready
docker compose -f docker-compose.prod.yml exec postgres pg_isready

# Run migrations
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head
```

### 5. Start Services

```bash
# Start all services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### 6. Verify Deployment

```bash
# Check backend health
curl http://localhost:8000/health

# Expected response:
# {"status":"healthy","app":"Tesseract SaaS MVP","version":"0.1.0","timestamp":"..."}

# Test with API key
curl -H "X-API-Key: your-api-key" http://localhost:8000/invoice/extract
```

## Reverse Proxy Setup (Nginx)

### Install Nginx

```bash
sudo apt-get install nginx certbot python3-certbot-nginx
```

### Configure Nginx

Create `/etc/nginx/sites-available/tesseract`:

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=100r/s;

# Backend upstream
upstream backend {
    least_conn;
    server 127.0.0.1:8000 max_fails=3 fail_timeout=30s;
}

# Frontend upstream
upstream frontend {
    least_conn;
    server 127.0.0.1:3000 max_fails=3 fail_timeout=30s;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    listen [::]:80;
    server_name api.yourdomain.com app.yourdomain.com;
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}

# API Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name api.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/tesseract-api-access.log;
    error_log /var/log/nginx/tesseract-api-error.log;

    # Request size
    client_max_body_size 10M;

    location / {
        limit_req zone=api_limit burst=20 nodelay;
        
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Frontend Server
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name app.yourdomain.com;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/app.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Logging
    access_log /var/log/nginx/tesseract-frontend-access.log;
    error_log /var/log/nginx/tesseract-frontend-error.log;

    location / {
        limit_req zone=general_limit burst=50 nodelay;
        
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

### Enable Site and Obtain SSL

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/tesseract /etc/nginx/sites-enabled/

# Test configuration
sudo nginx -t

# Obtain SSL certificates
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com

# Reload Nginx
sudo systemctl reload nginx

# Enable auto-renewal
sudo systemctl enable certbot.timer
```

## AWS Infrastructure Setup

### S3 Bucket Configuration

```bash
# Create bucket
aws s3 mb s3://tesseract-prod-uploads --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket tesseract-prod-uploads \
    --versioning-configuration Status=Enabled

# Enable encryption
aws s3api put-bucket-encryption \
    --bucket tesseract-prod-uploads \
    --server-side-encryption-configuration '{
        "Rules": [{
            "ApplyServerSideEncryptionByDefault": {
                "SSEAlgorithm": "AES256"
            }
        }]
    }'

# Block public access
aws s3api put-public-access-block \
    --bucket tesseract-prod-uploads \
    --public-access-block-configuration \
    "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true"

# Set lifecycle policy
cat > lifecycle.json << EOF
{
    "Rules": [{
        "Id": "DeleteOldFiles",
        "Status": "Enabled",
        "Prefix": "temp/",
        "Expiration": {
            "Days": 7
        }
    }]
}
EOF

aws s3api put-bucket-lifecycle-configuration \
    --bucket tesseract-prod-uploads \
    --lifecycle-configuration file://lifecycle.json
```

### SQS Queue Configuration

```bash
# Create queue
aws sqs create-queue \
    --queue-name tesseract-prod-tasks \
    --attributes '{
        "MessageRetentionPeriod": "345600",
        "VisibilityTimeout": "300",
        "ReceiveMessageWaitTimeSeconds": "20"
    }'

# Create dead letter queue
aws sqs create-queue \
    --queue-name tesseract-prod-tasks-dlq \
    --attributes MessageRetentionPeriod=1209600
```

### IAM Configuration

```bash
# Create IAM policy
cat > tesseract-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": "arn:aws:s3:::tesseract-prod-uploads/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "sqs:SendMessage",
                "sqs:ReceiveMessage",
                "sqs:DeleteMessage",
                "sqs:GetQueueAttributes"
            ],
            "Resource": "arn:aws:sqs:us-east-1:*:tesseract-prod-tasks"
        }
    ]
}
EOF

aws iam create-policy \
    --policy-name TesseractAppPolicy \
    --policy-document file://tesseract-policy.json

# Create IAM user and attach policy
aws iam create-user --user-name tesseract-app
aws iam attach-user-policy \
    --user-name tesseract-app \
    --policy-arn arn:aws:iam::YOUR_ACCOUNT_ID:policy/TesseractAppPolicy

# Create access keys
aws iam create-access-key --user-name tesseract-app
```

## Database Configuration

### PostgreSQL Tuning

Edit `/etc/postgresql/16/main/postgresql.conf`:

```conf
# Connection settings
max_connections = 100
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB

# Logging
logging_collector = on
log_directory = 'log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_line_prefix = '%m [%p] %q%u@%d '
log_timezone = 'UTC'
```

### Backup Strategy

```bash
# Daily backup script
cat > /usr/local/bin/backup-tesseract.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/tesseract"
DATE=$(date +%Y%m%d_%H%M%S)
POSTGRES_USER="prod_user"
POSTGRES_DB="tesseract_prod"

mkdir -p $BACKUP_DIR

# Backup database
docker exec tesseract-postgres-prod pg_dump \
    -U $POSTGRES_USER \
    -d $POSTGRES_DB \
    -F c \
    -f /tmp/backup_$DATE.dump

# Copy from container
docker cp tesseract-postgres-prod:/tmp/backup_$DATE.dump $BACKUP_DIR/

# Upload to S3
aws s3 cp $BACKUP_DIR/backup_$DATE.dump \
    s3://tesseract-backups/database/backup_$DATE.dump \
    --storage-class STANDARD_IA

# Clean up old backups (keep last 7 days locally)
find $BACKUP_DIR -type f -mtime +7 -delete

# Log
echo "Backup completed: $DATE"
EOF

chmod +x /usr/local/bin/backup-tesseract.sh

# Add to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/backup-tesseract.sh") | crontab -
```

## Monitoring & Logging

### Application Monitoring

#### Health Checks

```bash
# Create health check script
cat > /usr/local/bin/health-check.sh << 'EOF'
#!/bin/bash

# Backend health
BACKEND_HEALTH=$(curl -s http://localhost:8000/health | jq -r .status)
if [ "$BACKEND_HEALTH" != "healthy" ]; then
    echo "Backend unhealthy!"
    # Send alert
fi

# Frontend health
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000)
if [ "$FRONTEND_HEALTH" != "200" ]; then
    echo "Frontend unhealthy!"
    # Send alert
fi

# Database health
DB_HEALTH=$(docker exec tesseract-postgres-prod pg_isready -U prod_user)
if [ $? -ne 0 ]; then
    echo "Database unhealthy!"
    # Send alert
fi
EOF

chmod +x /usr/local/bin/health-check.sh

# Run every 5 minutes
(crontab -l 2>/dev/null; echo "*/5 * * * * /usr/local/bin/health-check.sh") | crontab -
```

### Log Management

```bash
# Configure log rotation
cat > /etc/logrotate.d/tesseract << EOF
/var/log/nginx/tesseract-*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        [ -f /var/run/nginx.pid ] && kill -USR1 \$(cat /var/run/nginx.pid)
    endscript
}
EOF
```

## Security Hardening

### Firewall Configuration

```bash
# UFW firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp  # SSH
sudo ufw allow 80/tcp  # HTTP
sudo ufw allow 443/tcp # HTTPS
sudo ufw enable
```

### Fail2Ban Setup

```bash
# Install fail2ban
sudo apt-get install fail2ban

# Configure for nginx
cat > /etc/fail2ban/jail.local << EOF
[nginx-req-limit]
enabled = true
filter = nginx-req-limit
action = iptables-multiport[name=ReqLimit, port="http,https", protocol=tcp]
logpath = /var/log/nginx/tesseract-*-error.log
findtime = 600
bantime = 7200
maxretry = 10
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

## Maintenance

### Update Procedure

```bash
# 1. Backup database
/usr/local/bin/backup-tesseract.sh

# 2. Pull latest code
cd /home/tesseract/tesseract
git pull origin main

# 3. Rebuild containers
docker compose -f docker-compose.prod.yml build

# 4. Stop services
docker compose -f docker-compose.prod.yml down

# 5. Run migrations
docker compose -f docker-compose.prod.yml run --rm backend alembic upgrade head

# 6. Start services
docker compose -f docker-compose.prod.yml up -d

# 7. Verify health
curl http://localhost:8000/health
```

### Rollback Procedure

```bash
# 1. Stop services
docker compose -f docker-compose.prod.yml down

# 2. Checkout previous version
git checkout <previous-commit-hash>

# 3. Rollback migrations if needed
docker compose -f docker-compose.prod.yml run --rm backend alembic downgrade -1

# 4. Rebuild and start
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d
```

## Troubleshooting

### Common Issues

#### Services Won't Start

```bash
# Check logs
docker compose -f docker-compose.prod.yml logs

# Check disk space
df -h

# Check memory
free -m
```

#### Database Connection Issues

```bash
# Test connection
docker exec tesseract-postgres-prod psql -U prod_user -d tesseract_prod -c "SELECT 1"

# Check connections
docker exec tesseract-postgres-prod psql -U prod_user -d tesseract_prod -c "SELECT count(*) FROM pg_stat_activity"
```

#### High Memory Usage

```bash
# Check container stats
docker stats

# Adjust worker processes in Dockerfile.prod
# CMD ["uvicorn", "app.main:app", "--workers", "2", ...]
```

## Performance Optimization

### Database Indexing

```sql
-- Add indexes for common queries
CREATE INDEX idx_invoices_date ON invoices(invoice_date);
CREATE INDEX idx_invoices_carrier ON invoices(carrier_name);
```

### Caching Strategy

```python
# Use Redis for caching frequent queries
# Configure in app/cache.py
```

### CDN Integration

```bash
# Use CloudFront or similar CDN for static assets
# Configure S3 bucket as origin
```

## Support

For deployment issues:
1. Check logs: `docker compose -f docker-compose.prod.yml logs`
2. Review monitoring dashboards
3. Contact support: ops@yourdomain.com

## Next Steps

- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure centralized logging (ELK stack)
- [ ] Implement CI/CD pipeline
- [ ] Set up staging environment
- [ ] Configure automated backups
- [ ] Implement disaster recovery plan
