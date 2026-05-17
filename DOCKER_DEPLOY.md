# LibraTrack — Docker Deployment Guide

## Files added

```
Dockerfile          # Multi-stage Python 3.11 image
docker-compose.yml  # Orchestrates web + db (Postgres) + nginx
nginx/nginx.conf    # Nginx reverse proxy config
.env.example        # Template for required environment variables
.dockerignore       # Keeps the image lean
```

## Quick start

```bash
# 1. Copy and fill in the environment file
cp .env.example .env
# Edit .env — at minimum set SECRET_KEY and POSTGRES_PASSWORD

# 2. Build and start all services
docker compose up --build -d

# 3. (First run only) Seed sample data
docker compose exec web python manage.py seed_data

# 4. Open the app
open http://localhost        # via Nginx on port 80
# Admin: http://localhost/admin  user: admin  password: adminpassword123
```

## Common commands

| Task | Command |
|---|---|
| View logs | `docker compose logs -f web` |
| Run tests | `docker compose exec web python manage.py test books` |
| Django shell | `docker compose exec web python manage.py shell` |
| Create superuser | `docker compose exec web python manage.py createsuperuser` |
| Stop everything | `docker compose down` |
| Stop + delete volumes | `docker compose down -v` |

## Architecture

```
Browser → Nginx :80 ──┬── /static/ → staticfiles volume
                       └── / → Gunicorn :8000 → Django → PostgreSQL :5432
```

- **Nginx** handles static/media files and terminates HTTP connections.
- **Gunicorn** runs 3 worker processes inside the `web` container.
- **PostgreSQL 16** stores all data in a named Docker volume (`postgres_data`).
- Static files and media are shared between `web` and `nginx` via named volumes.

## Production checklist

- [ ] Set `SECRET_KEY` to a long random string (50+ chars)
- [ ] Set `DEBUG=False`
- [ ] Set `ALLOWED_HOSTS` to your real domain(s)
- [ ] Add an SSL certificate (e.g. via Certbot/Let's Encrypt on the host or a load balancer)
- [ ] Back up the `postgres_data` volume regularly
- [ ] Pin image tags in `docker-compose.yml` before going to production
