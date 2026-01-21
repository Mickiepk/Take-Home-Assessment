# 🐳 Docker Setup Guide

Complete guide for running Computer Use Backend with Docker.

---

## 🚀 Quick Start

### 1. Prerequisites

- Docker Desktop (macOS/Windows) or Docker Engine (Linux)
- Docker Compose v2.0+
- 4GB+ RAM available
- 10GB+ disk space

**Check installation:**
```bash
docker --version
docker-compose --version
```

### 2. Configuration

**Copy environment file:**
```bash
cp .env.example .env
```

**Edit .env and set required values:**
```bash
# REQUIRED
ANTHROPIC_API_KEY=your_actual_api_key_here

# Optional (defaults are fine)
PORT=8000
MAX_CONCURRENT_SESSIONS=100
```

### 3. Start Services

**Easy way:**
```bash
./docker-start.sh
```

**Manual way:**
```bash
docker-compose build
docker-compose up -d
```

### 4. Access

- **Web UI:** http://localhost:8000/
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health/

---

## 📦 What's Included

### Services

1. **Backend** (FastAPI)
   - Computer Use Agent
   - WebSocket streaming
   - VNC server support
   - Worker pool management

2. **PostgreSQL** (Database)
   - Session storage
   - Message history
   - Persistent data

3. **Redis** (Cache)
   - Future use for scaling
   - Session state caching

### Ports

- `8000` - Backend API/Web UI
- `5432` - PostgreSQL (dev only)
- `6379` - Redis (dev only)
- `5900-5910` - VNC servers

---

## 🛠️ Common Commands

### Start/Stop

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Stop and remove volumes (deletes data!)
docker-compose down -v

# Restart a service
docker-compose restart backend
```

### Logs

```bash
# View all logs
docker-compose logs

# Follow backend logs
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Status

```bash
# Check service status
docker-compose ps

# Check health
curl http://localhost:8000/health/

# View resource usage
docker stats
```

### Build

```bash
# Rebuild images
docker-compose build

# Rebuild without cache
docker-compose build --no-cache

# Pull latest base images
docker-compose pull
```

---

## 🏭 Production Deployment

### Using Production Config

```bash
# Use production docker-compose
docker-compose -f docker-compose.prod.yml up -d

# View production logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Checklist

- [ ] Set strong `POSTGRES_PASSWORD` in .env
- [ ] Configure `ALLOWED_ORIGINS` for your domain
- [ ] Set up SSL/TLS (use nginx or reverse proxy)
- [ ] Configure resource limits
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure backups for PostgreSQL
- [ ] Use secrets management (not .env file)
- [ ] Set up log aggregation
- [ ] Configure firewall rules
- [ ] Enable Docker security scanning

### Environment Variables (Production)

```bash
# Required
ANTHROPIC_API_KEY=sk-ant-xxx
POSTGRES_PASSWORD=strong_password_here

# Recommended
MAX_CONCURRENT_SESSIONS=50
ALLOWED_ORIGINS='["https://yourdomain.com"]'
LOG_LEVEL=WARNING

# Optional
DEFAULT_MODEL=claude-sonnet-4-5-20250929
MAX_TOKENS=4096
```

---

## 🔧 Troubleshooting

### Services Won't Start

**Check logs:**
```bash
docker-compose logs backend
docker-compose logs postgres
```

**Common issues:**
- Port already in use: Change `PORT` in .env
- Missing API key: Set `ANTHROPIC_API_KEY` in .env
- Insufficient memory: Increase Docker memory limit

### Database Connection Failed

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Backend Not Responding

```bash
# Check backend status
docker-compose ps backend

# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend

# Rebuild if needed
docker-compose build backend
docker-compose up -d backend
```

### VNC Not Working

VNC requires X11 support which may not work in all Docker environments:

- **Linux:** Should work out of the box
- **macOS:** Limited support, may need XQuartz
- **Windows:** Limited support, may need WSL2

**Test VNC:**
```bash
# Get VNC info for a session
curl http://localhost:8000/vnc/{session_id}/info
```

### Out of Disk Space

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Remove everything (careful!)
docker system prune -a --volumes
```

---

## 📊 Monitoring

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health/

# Detailed health
curl http://localhost:8000/health/detailed

# Worker status
curl http://localhost:8000/sessions/workers/health
```

### Resource Usage

```bash
# Real-time stats
docker stats

# Container info
docker-compose ps

# Disk usage
docker system df
```

### Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d computer_use_backend

# Backup database
docker-compose exec postgres pg_dump -U postgres computer_use_backend > backup.sql

# Restore database
docker-compose exec -T postgres psql -U postgres computer_use_backend < backup.sql
```

---

## 🔐 Security

### Best Practices

1. **Never commit .env file**
   - Use .env.example as template
   - Store secrets in secure vault

2. **Use strong passwords**
   - PostgreSQL password
   - Redis password (if enabled)

3. **Limit exposed ports**
   - Only expose necessary ports
   - Use firewall rules

4. **Keep images updated**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

5. **Scan for vulnerabilities**
   ```bash
   docker scan computer-use-backend
   ```

---

## 🚀 Scaling

### Horizontal Scaling

Run multiple backend instances behind a load balancer:

```yaml
# docker-compose.scale.yml
services:
  backend:
    deploy:
      replicas: 3
```

```bash
docker-compose -f docker-compose.yml -f docker-compose.scale.yml up -d
```

### Vertical Scaling

Increase resources per container:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
```

---

## 📝 Development vs Production

### Development (docker-compose.yml)

- Code mounted as volume (hot reload)
- Ports exposed for debugging
- Debug logging enabled
- SQLite option available

### Production (docker-compose.prod.yml)

- Code baked into image
- Minimal port exposure
- Production logging
- PostgreSQL required
- Resource limits set
- Health checks enabled
- Auto-restart enabled

---

## 🆘 Getting Help

**Check logs first:**
```bash
docker-compose logs -f
```

**Verify configuration:**
```bash
docker-compose config
```

**Test connectivity:**
```bash
curl http://localhost:8000/health/
```

**Clean slate:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up -d
```

---

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)
- [PostgreSQL Docker Guide](https://hub.docker.com/_/postgres)

---

## ✅ Quick Reference

```bash
# Start
./docker-start.sh
# or
docker-compose up -d

# Stop
./docker-stop.sh
# or
docker-compose down

# Logs
docker-compose logs -f backend

# Status
docker-compose ps

# Rebuild
docker-compose build

# Clean
docker-compose down -v
docker system prune -a
```

---

**Need more help?** Check README.md or open an issue.
