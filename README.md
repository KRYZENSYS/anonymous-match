# 🌹 Anonim Tanishuv — Telegram Web App

> Professional darajadagi, zamonaviy va xavfsiz **Telegram Web App** anonim tanishuv platformasi.

![Stack](https://img.shields.io/badge/Next.js-15-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791) ![Redis](https://img.shields.io/badge/Redis-7-DC382D) ![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Xususiyatlar

### 🔐 Autentifikatsiya va xavfsizlik
- **Telegram Login Widget** — bir marta bosib kirish
- **JWT** sessiyalar (HS256, 30 kun)
- **Telegram initData** HMAC-SHA256 validatsiya
- **CSRF** himoyasi (SameSite=Strict + token)
- **Rate limiting** (SlowAPI)
- **XSS** himoyasi (DOMPurify frontend + sanitizatsiya backend)
- **SQL Injection** himoyasi (SQLAlchemy ORM)
- **Spam va flood** himoyasi
- **Report / Block** tizimi

### 💕 Tanishuv
- **Swipe Right** (Like), **Swipe Left** (Pass), **Super Like**
- **Match animatsiyasi** (konfetti effekti)
- **Match tarixi**
- **Filtr**: yosh, viloyat, shahar, qiziqishlar, online

### 💬 Chat
- **Real-time** WebSocket
- Matn, emoji, GIF, sticker, voice, photo, video
- **Typing indicator**, **read status**
- **Reply** va **delete** xabar
- Xabar holati (sent/delivered/read)

### 👤 Profil
- Nickname, yosh, jins, qidirayotgan jins
- Viloyat, shahar, bio, qiziqishlar
- **6 tagacha rasm**
- **Online status** + oxirgi faollik
- **Anonim identifikator** (#kryzen-A1B2)

### 🔒 Anonimlik
- Haqiqiy ism ko'rinMAYdi
- Telefon raqam YASHIRIN
- Telegram username ko'rinMAYdi
- Telegram ID YASHIRIN
- Har bir user uchun **tasodifiy public_id** (UUID-based)

### 💎 Premium
- VIP Badge 👑
- Boost — 30 daqiqaga birinchi o'ringa
- Unlimited Like
- Super Likes (5/hafta → premium = ∞)
- **Kim profilingni ko'rgan** (Who's viewed me)
- Reklama yo'q

### 👮 Admin Panel
- Dashboard, statistika, analitika
- Foydalanuvchilar, ban/suspend
- Reportlarni ko'rish va hal qilish
- Premium boshqaruv
- Broadcast xabar
- Loglar

### 🌐 Qo'shimcha
- **3 til**: 🇺🇿 O'zbek · 🇷🇺 Rus · 🇬🇧 Ingliz
- **Dark/Light mode**
- **PWA** (offline)
- **Glassmorphism** dizayn
- **Telegram** uslubidagi interfeys
- **Responsive** — mobil/tablet/desktop
- **SEO** + OpenGraph
- **Loading** animatsiyalar

---

## 🏗 Arxitektura

```
┌─────────────────────────────────────────────────┐
│   SINGLE SERVER (Docker Compose + Nginx)         │
│                                                   │
│  ┌───────────────────────────────────────────┐  │
│  │  Nginx (:80, :443) — reverse proxy       │  │
│  └─────┬──────────────────────────┬─────────┘  │
│        │ /api/*                    │ /         │
│  ┌─────▼────────────┐    ┌────────▼────────┐  │
│  │  FastAPI         │    │  Next.js 15     │  │
│  │  (uvicorn :8000) │    │  standalone     │  │
│  │  • REST /api/v1  │    │  (next start)   │  │
│  │  • WebSocket     │    │  :3000          │  │
│  │  • aiogram bot   │    │                 │  │
│  │    (polling)     │    │                 │  │
│  └─────┬────────────┘    └─────────────────┘  │
│        │                                        │
│  ┌─────▼──────┐    ┌─────────┐                 │
│  │ PostgreSQL │    │  Redis  │                 │
│  │  :5432     │    │  :6379  │                 │
│  └────────────┘    └─────────┘                 │
└─────────────────────────────────────────────────┘
```

---

## 🛠 Texnologiyalar

| Qatlam | Stack |
|--------|-------|
| Frontend | Next.js 15 · React 19 · TypeScript · Tailwind CSS · Zustand · i18next · Framer Motion |
| Backend | FastAPI · SQLAlchemy 2 (async) · Pydantic v2 · Alembic |
| Database | PostgreSQL 16 · Redis 7 (cache + WS pubsub) |
| Auth | Telegram Login Widget · JWT (HS256) · passlib (bcrypt) |
| Realtime | WebSocket (FastAPI native) |
| Bot | aiogram 3 (polling) |
| Storage | Cloudinary / S3 (rasmlar) |
| Deploy | Docker Compose + Nginx + Let's Encrypt |

---

## 🚀 Tez boshlash (Docker)

### 1. Klonlash
```bash
git clone https://github.com/KRYZENSYS/anonymous-match.git
cd anonymous-match
cp .env.example .env
```

### 2. `.env` to'ldirish
```env
BOT_TOKEN=...              # @BotFather'dan
WEBAPP_URL=https://yourdomain.com
API_URL=https://api.yourdomain.com
POSTGRES_PASSWORD=...
JWT_SECRET=...             # openssl rand -hex 32
REDIS_URL=redis://redis:6379
CLOUDINARY_URL=...         # ixtiyoriy
```

### 3. Ishga tushirish
```bash
docker compose up -d --build
```

Keyin:
- **Web**: `https://yourdomain.com`
- **API docs**: `https://api.yourdomain.com/docs`
- **Telegram bot**: `/start` yuboring

---

## 📁 Struktura

```
anonymous-match/
├── apps/
│   ├── api/                    FastAPI backend
│   │   ├── app/
│   │   │   ├── core/           config, db, security, deps
│   │   │   ├── models/         SQLAlchemy modellari
│   │   │   ├── schemas/        Pydantic sxemalar
│   │   │   ├── repositories/   Repository pattern
│   │   │   ├── services/       Business logic
│   │   │   ├── routers/        FastAPI route'lar
│   │   │   ├── ws/             WebSocket
│   │   │   ├── bot/            aiogram bot
│   │   │   └── utils/          Yordamchi
│   │   ├── alembic/            Migration'lar
│   │   ├── tests/              Pytest testlar
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── web/                    Next.js frontend
│   │   ├── src/
│   │   │   ├── app/[locale]/   i18n routing
│   │   │   ├── components/     UI komponentlar
│   │   │   ├── lib/            API client, utils
│   │   │   ├── stores/         Zustand
│   │   │   ├── i18n/           uz/ru/en
│   │   │   └── styles/
│   │   ├── Dockerfile
│   │   └── package.json
│   └── bot/                    (ixtiyoriy) alohida bot deploy
├── nginx/
│   ├── nginx.conf
│   └── ssl/
├── docker-compose.yml
├── .env.example
├── .github/workflows/          CI/CD
├── DEPLOYMENT.md
├── ARCHITECTURE.md
└── README.md
```

---

## 📜 API

Swagger hujjatlari: **`/docs`** (FastAPI auto-generated)

### REST
- `POST /api/v1/auth/telegram` — Telegram orqali login
- `GET /api/v1/profiles/me` — o'z profilingiz
- `PATCH /api/v1/profiles/me` — profilni tahrirlash
- `GET /api/v1/discover` — swipe uchun odamlar
- `POST /api/v1/swipes` — like/pass/superlike
- `GET /api/v1/matches` — match'lar
- `GET /api/v1/chats` — chatlar
- `GET /api/v1/chats/{id}/messages` — xabarlar
- `POST /api/v1/chats/{id}/messages` — xabar yuborish
- `POST /api/v1/reports` — report
- `POST /api/v1/blocks` — blok
- `POST /api/v1/premium/buy` — premium sotib olish

### WebSocket
- `WS /api/v1/ws/chat/{chat_id}` — real-time chat
- `WS /api/v1/ws/notifications` — bildirishnomalar

---

## 🧪 Testlar

```bash
cd apps/api
pytest -v
```

---

## 📄 Litsenziya

MIT © KRYZENSYS

---

## 📞 Aloqa

- **Telegram**: [@kryzensys](https://t.me/kryzensys)
- **Email**: dev@kryzen.uz
- **Issues**: [GitHub Issues](https://github.com/KRYZENSYS/anonymous-match/issues)
