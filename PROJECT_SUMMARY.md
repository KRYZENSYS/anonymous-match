# 🎉 Anonymous Match — Loyiha To'liq Tayyor!

## 📊 Statistika
- **100+ fayl** yaratildi
- **12 ta asosiy model** (users, profiles, likes, matches, chats, messages, media, notifications, premium, payments, reports, blocks, audit_logs)
- **50+ API endpoint**
- **6 ta bot handler moduli**
- **15+ React komponent**
- **3 tilda i18n** (uz/ru/en)
- **To'liq Docker stack**

## ✅ Bajarilgan ishlar

### Backend (FastAPI + Python)
- [x] Database models (SQLAlchemy 2 async)
- [x] Alembic migrations
- [x] JWT auth + Telegram initData verify
- [x] User service (CRUD, profile, location)
- [x] Discover service (swipe, match, mutual)
- [x] Chat service (messages, read, typing)
- [x] Notification service (Redis pubsub)
- [x] Premium service (Telegram Stars)
- [x] Media service (upload, cloudinary)
- [x] WebSocket routes
- [x] Bot handlers (start, profile, discover, chat, premium, admin)
- [x] Middleware (auth, throttle, admin)
- [x] Admin endpoints
- [x] Report/block endpoints
- [x] Audit logging
- [x] Pytest tests
- [x] Seed script
- [x] Makefile + Dockerfile
- [x] Health check + metrics

### Frontend (Next.js 15)
- [x] App router structure
- [x] Telegram WebApp SDK integration
- [x] Zustand stores (auth, theme)
- [x] TanStack Query setup
- [x] API client (full)
- [x] Providers (Telegram, Auth, Theme)
- [x] Onboarding screen
- [x] Main screen (tabs: discover/matches/profile)
- [x] Profile setup (5 steps)
- [x] Profile screen
- [x] Swipe deck (Tinder-style)
- [x] Profile card (animations, badges)
- [x] Chat list
- [x] Chat screen (WebSocket, typing, read receipts)
- [x] Premium page
- [x] Settings page
- [x] Notifications page
- [x] Admin panel
- [x] i18n (3 languages)
- [x] Custom CSS animations
- [x] Tailwind config
- [x] Dockerfile
- [x] Hooks (location, Telegram, WebSocket)
- [x] Utils (cn, format, age, distance)

### DevOps
- [x] Docker Compose (postgres, redis, api, web, nginx)
- [x] Nginx config (rate limit, WebSocket, SSL)
- [x] .env examples
- [x] .gitignore
- [x] README (full)
- [x] DEPLOYMENT.md
- [x] Makefile
- [x] CI/CD ready (GitHub Actions template)

## 🚀 Ishga tushirish

```bash
git clone https://github.com/KRYZENSYS/anonymous-match.git
cd anonymous-match
cp apps/api/.env.example apps/api/.env
# .env ni to'ldiring (BOT_TOKEN, JWT_SECRET)
docker-compose up -d
docker-compose exec api alembic upgrade head
docker-compose exec api python -m scripts.seed
```

## 🌐 API
`http://localhost:8000/docs` — Swagger

## 📱 Web
`http://localhost:3000`

## 🤖 Bot
`@AnonymousMatchBot`

## 👥 Team
**KRYZENSYS** — Tashkent, Uzbekistan 🇺🇿

Made with ❤️ in Tashkent
