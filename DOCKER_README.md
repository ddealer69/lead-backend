# Lead Backend - Docker Setup

This guide covers running the Lead Backend API using Docker for easy development and deployment.

## 🚀 Quick Start

1. **Clone and setup environment:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env with your actual credentials
   nano .env  # or use your preferred editor
   ```

2. **Start the service:**
   ```bash
   ./start.sh
   ```

3. **Verify it's running:**
   ```bash
   curl http://localhost:3000/health
   ```

## 📋 Docker Commands

### Start Services
```bash
# Using the startup script (recommended)
./start.sh

# Or manually
docker-compose up -d
```

### View Logs
```bash
# Follow logs in real-time
docker-compose logs -f

# View last 50 lines
docker-compose logs --tail=50
```

### Stop Services
```bash
docker-compose down
```

### Rebuild Container
```bash
# Rebuild after code changes
docker-compose build

# Force rebuild (no cache)
docker-compose build --no-cache
```

### Access Container Shell
```bash
docker-compose exec lead-backend bash
```

## 🔧 Development Workflow

### Making Code Changes
1. Edit your code files
2. The container will automatically reload (development mode)
3. No need to rebuild unless you change `requirements.txt`

### Adding New Dependencies
1. Add to `requirements.txt`
2. Rebuild container: `docker-compose build`
3. Restart: `docker-compose up -d`

## 🌐 Service Endpoints

- **Health Check:** http://localhost:3000/health
- **API Documentation:** Available through your API endpoints
- **Email Services:** Various SMTP and email management endpoints

## 🔒 Environment Variables

Required variables in your `.env` file:

- `DATABASE_URL` - Supabase database connection
- `SUPABASE_URL` - Supabase project URL
- `SUPABASE_KEY` - Supabase API key
- `EMAIL_HOST` - SMTP server (e.g., smtp.gmail.com)
- `EMAIL_PORT` - SMTP port (usually 587)
- `EMAIL_USER` - Your email address
- `EMAIL_PASSWORD` - App password for Gmail

## 📊 Monitoring

### Health Checks
The container includes automatic health monitoring:
- Health check endpoint: `/health`
- Check interval: 30 seconds
- Timeout: 10 seconds
- Retries: 3

### Container Status
```bash
# Check container status
docker-compose ps

# View container resource usage
docker stats
```

## 🐛 Troubleshooting

### Container Won't Start
1. Check logs: `docker-compose logs`
2. Verify `.env` file exists and has correct values
3. Ensure port 3000 isn't in use: `lsof -i :3000`

### Database Connection Issues
1. Verify `DATABASE_URL` in `.env`
2. Check Supabase credentials
3. Ensure network connectivity

### Email Service Issues
1. Verify SMTP credentials in `.env`
2. Check if using Gmail app passwords
3. Review email service logs

### Performance Issues
1. Check container resources: `docker stats`
2. Review application logs for errors
3. Monitor health check responses

## 🚀 Production Deployment

For production deployment:

1. **Update environment variables** with production values
2. **Use a production WSGI server** (consider adding Gunicorn)
3. **Set up proper logging** and monitoring
4. **Configure reverse proxy** (nginx) if needed
5. **Enable SSL/TLS** certificates

Example production docker-compose override:
```yaml
# docker-compose.prod.yml
services:
  lead-backend:
    environment:
      - FLASK_ENV=production
    restart: always
```

Run with: `docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d`