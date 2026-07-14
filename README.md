# 💖 Anonymous Match

> Telegram orqali **anonim tanishuv** uchun to'liq full-stack platforma. Tinder-style swipe, real-time chat, premium tizim, admin panel.

## ✨ Xususiyatlar

### 🔐 Anonimlik kafolati
- Telegram username yashirin
- Faqat siz tanlagan ma'lumot ko'rinadi
- Yuz, ism, telefon — hech narsa oshkor bo'lmaydi
- Har bir foydalanuvchiga noyob `public_id` beriladi

### 💕 Match & Swipe
- Like / Pass / SuperLike
- Mutual like = **MATCH! 🎉**
- Filtr: yosh, jins, shahar, masofa
- Boost — 30 daqiqaga eng yuqoriga

### 💬 Real-time Chat
- WebSocket orqali tezkor xabarlar
- Typing indicator
- Read receipts (✓✓)
- Reply, edit, delete
- Image / Voice / Sticker

### 💎 Premium tizim
- **Plus** (500⭐) — cheksiz like
- **Gold** (1200⭐) — kim ko'rganini bilish
- **Platinum** (2500⭐) — VIP badge
- Telegram Stars orqali to'lov
- Boost har oyda

### 🛡️ Xavfsizlik
- Block / Report
- AI moderatsiya
- Admin panel
- Audit log
- Rate limiting

### 🌍 i18n
- O'zbek, Rus, English

## 🏗️ Arxitektura

```
anonymous-match/
├── apps/
│   ├── api/              # FastAPI backend
│   │   ├── app/
│   │   │   ├── api/      # Routes
│   │   │   ├── core/     # Config, DB, Redis
│   │   │   ├── models/   # SQLAlchemy models
│   │   │   ├── schemas/  # Pydantic
│   │   │   ├── services/ # Business logic
│   │   │   ├── routers/  # API endpoints
│   │   │   └── bot.py    # Telegram bot
│   │   ├── alembic/      # Migrations
│   │   ├── main.py
│   │   └── requirements.txt
│   └── web/              # Next.js 15 frontend
│       ├── src/
│       │   ├── app/      # App router
│       │   ├── components/
│       │   ├── hooks/
│       │   ├── store/    # Zustand
│       │   └── lib/      # API client
│       └── package.json
├── docker-compose.yml
└── nginx.conf
```

## 🛠️ Tech Stack

### Backend
- **Python 3.12** + **FastAPI**
- **PostgreSQL 16** + **SQLAlchemy 2** (async)
- **Redis 7** (cache, pubsub, rate limit)
- **aiogram 3** (Telegram bot)
- **Alembic** (migrations)
- **uvloop** (high-perf)
- **Cloudinary** (media storage)
- **Sentry** (error tracking)
- **Prometheus** (metrics)

### Frontend
- **Next.js 15** + **React 19** + **TypeScript**
- **Tailwind CSS 3.4** (custom dark/light themes)
- **Framer Motion** (animations)
- **Zustand** (state)
- **TanStack Query** (data fetching)
- **Telegram WebApp SDK**
- **WebSocket** (real-time)

### DevOps
- **Docker** + **Docker Compose**
- **Nginx** (reverse proxy, SSL)
- **GitHub Actions** (CI/CD)

## 🚀 Ishga tushirish

### 1. Repository clone
```bash
git clone https://github.com/KRYZENSYS/anonymous-match.git
cd anonymous-match
```

### 2. Environment sozlash
```bash
cp apps/api/.env.example apps/api/.env
cp apps/web/.env.example apps/web/.env

# .env fayllarni tahrirlash:
# - BOT_TOKEN (BotFather dan)
# - JWT_SECRET (64 ta random belgi)
# - POSTGRES_PASSWORD
# - CLOUDINARY_* (optional)
```

### 3. Docker orqali
```bash
docker-compose up -d
```

### 4. Migration
```bash
docker-compose exec api alembic upgrade head
```

### 5. Telegram bot sozlash
1. @BotFather ga /newbot
2. Bot token ni .env ga qo'ying
3. WebApp URL: `https://yourdomain.com`

## 📚 API

API documentation: `http://localhost:8000/docs`

### Asosiy endpointlar

| Method | Path | Tavsif |
|--------|------|--------|
| POST | `/api/v1/auth/telegram` | Telegram login |
| GET | `/api/v1/users/me` | O'z profilim |
| PATCH | `/api/v1/users/me` | Profilni yangilash |
| GET | `/api/v1/discover` | Swipe uchun profillar |
| POST | `/api/v1/discover/swipe` | Like/Pass/SuperLike |
| GET | `/api/v1/discover/matches` | Matchlarim |
| GET | `/api/v1/chats` | Chatlarim |
| POST | `/api/v1/chats/{id}/messages` | Xabar yuborish |
| GET | `/api/v1/premium/plans` | Premium tariflar |
| POST | `/api/v1/media/upload` | Fayl yuklash |

### WebSocket

- `ws://host/ws/connect?token=JWT` — asosiy ulanish
- `ws://host/ws/chat/{id}?token=JWT` — chat xonasi

## 🗄️ Database Schema

12 ta asosiy jadval:
- `users` — foydalanuvchilar
- `profiles` — profil ma'lumotlari
- `likes` — like/pass/superlike
- `matches` — o'zaro likelar
- `chats` — chatlar
- `messages` — xabarlar
- `media` — fayllar
- `notifications` — bildirishnomalar
- `premium` — premium holati
- `subscriptions` — obunalar
- `reports` — reportlar
- `blocks` — bloklar
- `logs` — tizim loglari

## 🔒 Xavfsizlik

- **JWT** autentifikatsiya
- **Telegram initData** validatsiya
- **Rate limiting** (200/min)
- **CORS** himoya
- **SQL injection** himoya (ORM)
- **XSS** himoya (Pydantic validation)
- **Audit log** barcha muhim amallar uchun

## 📈 Monitoring

- **Prometheus metrics**: `/metrics`
- **Health check**: `/health`
- **Sentry** error tracking

## 💳 To'lov

Telegram Stars orqali:
1. User bot'da /premium
2. Tarif tanlaydi
3. Telegram to'lov
4. API verify qiladi
5. Premium faollashadi

## 📱 Frontend sahifalar

- `/` — Asosiy (discover/chat/profile)
- `/premium` — Premium tariflar
- `/chat/[id]` — Chat
- `/settings` — Sozlamalar

## 🤝 Contributing

Pull requestlar qabul qilinadi. Katta o'zgarishlar uchun avval issue oching.

## 📄 License

MIT © KRYZENSYS

## 👥 Team

- **Backend**: KRYZENSYS
- **Frontend**: KRYZENSYS
- **DevOps**: KRYZENSYS

## 📞 Aloqa

- **Telegram**: @kryzen_support
- **Email**: kryzensys@gmail.com
- **Website**: https://kryzen.uz

---

⚡ **Made with ❤️ by KRYZENSYS in Tashkent**
