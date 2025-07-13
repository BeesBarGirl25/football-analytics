# Football Dashboard Deployment Guide

This guide provides comprehensive instructions for deploying the Football Dashboard application in various environments.

## 🚀 Deployment Options

- **[Local Development](#local-development)** - Quick setup for development
- **[Heroku](#heroku-deployment)** - Cloud platform deployment
- **[Docker](#docker-deployment)** - Containerized deployment
- **[AWS](#aws-deployment)** - Amazon Web Services deployment
- **[Production Server](#production-server)** - Self-hosted deployment

## 🏠 Local Development

### Prerequisites

- Python 3.8+
- Git
- PostgreSQL (optional, SQLite used by default)

### Quick Setup

```bash
# Clone repository
git clone <repository-url>
cd Football_Dashboard

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export FLASK_ENV=development
export FLASK_DEBUG=1
export DATABASE_URL=sqlite:///football_dashboard.db

# Initialize database
python create_tables.py

# Generate plot data (optional, takes time)
python data/etl/create_match_plots.py

# Run application
python app.py
```

### Environment Variables

Create a `.env` file in the root directory:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=sqlite:///football_dashboard.db

# StatsBomb API (if needed)
STATSBOMB_API_KEY=your-api-key

# Cache Configuration
CACHE_TYPE=simple
CACHE_DEFAULT_TIMEOUT=300
```

### Development Database Setup

```bash
# Using SQLite (default)
python create_tables.py

# Using PostgreSQL (optional)
export DATABASE_URL=postgresql://username:password@localhost/football_dashboard
python create_tables.py
```

## ☁️ Heroku Deployment

### Prerequisites

- Heroku CLI installed
- Heroku account
- Git repository

### Step-by-Step Deployment

#### 1. Prepare Application

```bash
# Ensure Procfile exists
echo "web: python app.py" > Procfile

# Ensure runtime.txt exists (optional)
echo "python-3.11.0" > runtime.txt

# Commit changes
git add .
git commit -m "Prepare for Heroku deployment"
```

#### 2. Create Heroku Application

```bash
# Login to Heroku
heroku login

# Create new app
heroku create your-app-name

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
```

#### 3. Deploy Application

```bash
# Deploy to Heroku
git push heroku main

# Initialize database
heroku run python create_tables.py

# Generate plot data (optional, may timeout)
heroku run python data/etl/create_match_plots.py --timeout=1800

# Open application
heroku open
```

#### 4. Heroku Configuration

```bash
# View logs
heroku logs --tail

# Scale dynos
heroku ps:scale web=1

# Set additional config vars
heroku config:set CACHE_TYPE=simple
heroku config:set WEB_CONCURRENCY=2
```

### Heroku Environment Variables

```bash
# Required variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DATABASE_URL=postgres://... # Auto-set by addon

# Optional variables
heroku config:set CACHE_TYPE=simple
heroku config:set CACHE_DEFAULT_TIMEOUT=300
heroku config:set WEB_CONCURRENCY=2
```

## 🐳 Docker Deployment

### Dockerfile

Create `Dockerfile` in root directory:

```dockerfile
FROM python:3.11-slim

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
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Run application
CMD ["python", "app.py"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/football_dashboard
      - SECRET_KEY=your-secret-key
    depends_on:
      - db
    volumes:
      - .:/app

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=football_dashboard
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

### Docker Commands

```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d

# Initialize database
docker-compose exec web python create_tables.py

# Generate plot data
docker-compose exec web python data/etl/create_match_plots.py

# View logs
docker-compose logs -f web

# Stop services
docker-compose down
```

## ☁️ AWS Deployment

### AWS Elastic Beanstalk

#### 1. Prepare Application

```bash
# Install EB CLI
pip install awsebcli

# Initialize EB application
eb init

# Create environment
eb create football-dashboard-prod

# Deploy
eb deploy
```

#### 2. Configuration Files

Create `.ebextensions/01_packages.config`:

```yaml
packages:
  yum:
    postgresql-devel: []
    gcc: []
```

Create `.ebextensions/02_python.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app.py
  aws:elasticbeanstalk:application:environment:
    FLASK_ENV: production
    PYTHONPATH: /opt/python/current/app
```

#### 3. RDS Database Setup

```bash
# Create RDS instance
aws rds create-db-instance \
    --db-instance-identifier football-dashboard-db \
    --db-instance-class db.t3.micro \
    --engine postgres \
    --master-username admin \
    --master-user-password your-password \
    --allocated-storage 20

# Set environment variable
eb setenv DATABASE_URL=postgresql://admin:password@endpoint:5432/postgres
```

### AWS EC2 Manual Deployment

#### 1. Launch EC2 Instance

```bash
# Launch Ubuntu 20.04 LTS instance
# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-ip
```

#### 2. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip python3-venv nginx postgresql postgresql-contrib

# Create application user
sudo useradd -m -s /bin/bash football
sudo su - football

# Clone repository
git clone <repository-url>
cd Football_Dashboard

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 3. Database Setup

```bash
# Configure PostgreSQL
sudo -u postgres createuser --interactive football
sudo -u postgres createdb football_dashboard

# Set database URL
export DATABASE_URL=postgresql://football:password@localhost/football_dashboard
```

#### 4. Nginx Configuration

Create `/etc/nginx/sites-available/football-dashboard`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/football/Football_Dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 5. Systemd Service

Create `/etc/systemd/system/football-dashboard.service`:

```ini
[Unit]
Description=Football Dashboard
After=network.target

[Service]
User=football
Group=football
WorkingDirectory=/home/football/Football_Dashboard
Environment=PATH=/home/football/Football_Dashboard/venv/bin
Environment=FLASK_ENV=production
Environment=DATABASE_URL=postgresql://football:password@localhost/football_dashboard
ExecStart=/home/football/Football_Dashboard/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 6. Start Services

```bash
# Enable and start services
sudo systemctl enable football-dashboard
sudo systemctl start football-dashboard
sudo systemctl enable nginx
sudo systemctl start nginx

# Check status
sudo systemctl status football-dashboard
sudo systemctl status nginx
```

## 🏭 Production Server

### Production Checklist

#### Security

- [ ] Set strong `SECRET_KEY`
- [ ] Use HTTPS (SSL/TLS certificates)
- [ ] Configure firewall rules
- [ ] Set up database backups
- [ ] Enable logging and monitoring
- [ ] Use environment variables for secrets
- [ ] Disable debug mode (`FLASK_ENV=production`)

#### Performance

- [ ] Use production WSGI server (Gunicorn)
- [ ] Configure database connection pooling
- [ ] Set up caching (Redis/Memcached)
- [ ] Enable gzip compression
- [ ] Configure static file serving
- [ ] Set up CDN for static assets

#### Monitoring

- [ ] Set up application monitoring
- [ ] Configure log aggregation
- [ ] Set up health checks
- [ ] Monitor database performance
- [ ] Set up alerting

### Production Configuration

#### Gunicorn Setup

```bash
# Install Gunicorn
pip install gunicorn

# Create Gunicorn config
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### Environment Variables

```bash
# Production environment variables
export FLASK_ENV=production
export SECRET_KEY=your-very-secure-secret-key
export DATABASE_URL=postgresql://user:pass@host:5432/dbname
export CACHE_TYPE=redis
export CACHE_REDIS_URL=redis://localhost:6379/0
export WEB_CONCURRENCY=4
```

#### Nginx Production Config

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;

    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location /static {
        alias /path/to/Football_Dashboard/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}
```

## 🔧 Database Migration

### Backup and Restore

```bash
# Backup database
pg_dump $DATABASE_URL > backup.sql

# Restore database
psql $DATABASE_URL < backup.sql

# Backup with compression
pg_dump $DATABASE_URL | gzip > backup.sql.gz

# Restore from compressed backup
gunzip -c backup.sql.gz | psql $DATABASE_URL
```

### Data Migration

```bash
# Export data from old system
python data/etl/export_data.py

# Import data to new system
python data/etl/import_data.py

# Regenerate plots
python data/etl/create_match_plots.py
```

## 📊 Monitoring and Logging

### Application Monitoring

```python
# Add to app.py for production monitoring
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/football_dashboard.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Football Dashboard startup')
```

### Health Check Endpoint

```python
# Add to routes/health.py
@app.route('/health')
def health_check():
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow()})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500
```

## 🚨 Troubleshooting

### Common Issues

#### Database Connection Issues

```bash
# Check database connectivity
python -c "from app import app, db; app.app_context().push(); print(db.engine.execute('SELECT 1').scalar())"

# Reset database
python create_tables.py --reset
```

#### Memory Issues

```bash
# Monitor memory usage
htop

# Reduce worker processes
export WEB_CONCURRENCY=2

# Enable swap if needed
sudo fallocate -l 1G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

#### Performance Issues

```bash
# Check application logs
tail -f logs/football_dashboard.log

# Monitor database queries
# Add to app.py
import logging
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

# Profile slow endpoints
from flask_profiler import Profiler
profiler = Profiler()
profiler.init_app(app)
```

### Log Analysis

```bash
# View recent errors
grep ERROR logs/football_dashboard.log | tail -20

# Monitor real-time logs
tail -f logs/football_dashboard.log

# Analyze access patterns
awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -nr
```

## 📞 Support

For deployment issues:

1. Check application logs
2. Verify environment variables
3. Test database connectivity
4. Review this deployment guide
5. Create an issue in the repository

---

**Last Updated**: 2025-06-30  
**Maintained by**: Football Dashboard Team
