# 🚀 Deployment Guide

## 1. VPS ga deploy (Ubuntu 22.04+)

### Kerakli dasturlar
```bash
# Docker va Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt install -y docker-compose
```

### Loyihani clone qilish
```bash
git clone https://github.com/KRYZENSYS/anonymous-match.git
cd anonymous-match
cp apps/api/.env.example apps/api/.env
nano apps/api/.env  # Sozlash
```

### Environment variables (.env)
```env
POSTGRES_USER=kryzen
POSTGRES_PASSWORD=KRYZEN_SUPER_SECRET_2026
POSTGRES_DB=anonymous_match
JWT_SECRET=64-TARANDOM-HARF-VA-RAQAM-2026
BOT_TOKEN=1234567890:ABCDefghijk...
WEBAPP_URL=https://yourdomain.com
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com
```

### Ishga tushirish
```bash
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## 2. SSL sertifikat (Let's Encrypt)

```bash
sudo apt install -y certbot
sudo certbot certonly --standalone -d yourdomain.com -d api.yourdomain.com
```

## 3. Telegram Bot sozlash

1. @BotFather ga `/newbot`
2. Bot nomi va username bering
3. Tokenni `.env` ga qo'ying
4. `/setdomain` — domain bering
5. WebApp URL: `https://yourdomain.com`

## 4. Cloudinary (ixtiyoriy)

1. https://cloudinary.com da ro'yxatdan o'ting
2. `.env` ga qo'ying:
   ```
   CLOUDINARY_CLOUD_NAME=xxx
   CLOUDINARY_API_KEY=xxx
   CLOUDINARY_API_SECRET=xxx
   ```

## 5. Monitoring

- **Health**: `https://api.yourdomain.com/health`
- **Metrics**: `https://api.yourdomain.com/metrics`
- **Logs**: `docker-compose logs -f`

## 6. Backup

```bash
# Database backup
docker-compose exec postgres pg_dump -U kryzen anonymous_match > backup.sql

# Restore
cat backup.sql | docker-compose exec -T postgres psql -U kryzen anonymous_match
```

## 7. Yangilash

```bash
git pull
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec api alembic upgrade head
```

## 8. Scaling (production)

```yaml
# docker-compose.override.yml
services:
  api:
    deploy:
      replicas: 4
    ulimits:
      nofile:
        soft: 65536
        hard: 65536
  web:
    deploy:
      replicas: 2
```

## 9. CDN (Cloudflare)

1. Cloudflare'ga domain qo'shing
2. SSL: Full (Strict)
3. DNS: A record → server IP
4. Caching: ON
5. Rocket Loader: ON

## 10. CI/CD (GitHub Actions)

`.github/workflows/deploy.yml`:
```yaml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app/anonymous-match
            git pull
            docker-compose up -d --build
            docker-compose exec -T api alembic upgrade head
```

## 11. Troubleshooting

### Bot ishlamayapti
```bash
docker-compose logs -f api | grep bot
```

### Database ulanmayapti
```bash
docker-compose ps
docker-compose logs postgres
```

### WebSocket ulanmayapti
- Nginx: `proxy_set_header Upgrade $http_upgrade;` kerak
- SSL: `wss://` ishlatilishi kerak

## 12. Performance

- **API**: 4 workers, uvloop
- **Web**: Standalone Next.js build
- **DB**: 100 connection pool
- **Redis**: 1GB maxmemory, allkeys-lru
- **CDN**: Cloudflare
- **Caching**: Redis + Browser cache

## 13. Security checklist

- [x] JWT secret 64+ chars
- [x] HTTPS forced
- [x] CORS configured
- [x] Rate limiting
- [x] SQL injection (ORM)
- [x] XSS protection
- [x] CSRF token
- [x] Audit logging
- [x] Daily backups
- [x] Monitoring (Sentry)
- [x] Health checks
