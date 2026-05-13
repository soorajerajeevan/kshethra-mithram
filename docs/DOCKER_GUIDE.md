# Docker Deployment Guide

This guide explains how to build and run the Temple App using Docker.

## Prerequisites

- Docker installed ([Download Docker](https://www.docker.com/products/docker-desktop))
- Docker Compose installed (included with Docker Desktop)

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t temple-app:latest .
```

### 2. Run the Container

**Using docker-compose (recommended):**
```bash
 docker compose up -d
```

**Using docker directly:**
```bash
docker run -d \
  --name temple_app \
  -p 5000:5000 \
  -v $(pwd)/app/static/uploads:/app/app/static/uploads \
  -e SECRET_KEY="your-secret-key" \
  temple-app:latest
```

### 3. Access the Application

Open your browser and navigate to: **http://localhost:5000**

## Common Commands

### View running containers
```bash
docker ps
```

### View logs
```bash
docker logs temple_app
```

### View live logs
```bash
docker logs -f temple_app
```

### Execute commands inside container
```bash
docker exec -it temple_app python run.py init_db
docker exec -it temple_app python run.py seed_data
```

### Stop the container
```bash
docker stop temple_app
```

### Remove the container
```bash
docker rm temple_app
```

## With Docker Compose

### Start
```bash
docker-compose up -d
```

### Stop
```bash
docker-compose down
```

### View logs
```bash
docker-compose logs -f web
```

### Initialize database
```bash
docker-compose exec web python run.py init_db
docker-compose exec web python run.py seed_data
```

## Configuration

### Environment Variables

Create a `.dockerenv` file (or use `docker-compose.yml` environment section):

```
FLASK_CONFIG=production
SECRET_KEY=your-very-secret-key-change-in-production
DATABASE_URL=sqlite:///temple_app.db
```

**For Production:**
- Always set a strong `SECRET_KEY`
- Consider using PostgreSQL instead of SQLite: `postgresql://user:pass@host:port/db`
- Set `FLASK_ENV=production`

### Database Options

**SQLite (default - for development):**
```
DATABASE_URL=sqlite:///temple_app.db
```

**PostgreSQL (recommended for production):**

1. Uncomment the `db` service in `docker-compose.yml`
2. Update environment variables:
```
DATABASE_URL=postgresql://temple_user:temple_pass@db:5432/temple_db
```
3. Start with: `docker-compose up -d`

## Volumes

The docker-compose setup mounts:
- `./app/static/uploads` - for user uploads
- `./temple_app.db` - for database persistence

These ensure data persists after container restarts.

## Production Deployment

For production, consider:

1. **Use a production WSGI server:**
   ```dockerfile
   CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
   ```
   Add `gunicorn` to requirements.txt

2. **Use PostgreSQL instead of SQLite**

3. **Set strong SECRET_KEY in environment**

4. **Enable HTTPS (use nginx reverse proxy)**

5. **Set up proper logging and monitoring**

6. **Use environment files** instead of hardcoding values

## Troubleshooting

### Port 5000 already in use
```bash
# On Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On Linux/Mac
lsof -i :5000
kill -9 <PID>
```

### Container won't start
```bash
docker logs temple_app
```

### Database not initializing
```bash
docker exec -it temple_app python run.py init_db
docker exec -it temple_app python run.py seed_data
```

### Permission denied on uploads folder
```bash
docker exec -it temple_app chmod -R 755 /app/app/static/uploads
```

## Cleanup

Remove unused images and containers:
```bash
docker system prune
```

## See Also

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Flask Deployment](https://flask.palletsprojects.com/deployment/)
