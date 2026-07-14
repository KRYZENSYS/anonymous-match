"""Seed mega data - achievements, missions, gifts, themes, stickers, packages, etc."""
import asyncio
from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.gamification import Achievement, Mission, Gift, ChatTheme, StickerPack, Sticker
from app.models.community import CoinPackage
from app.models.seasonal import SeasonalEvent, SubscriptionPlan
from app.services.gamification import GamificationService
from app.services.seasons import SeasonService


GIFTS = [
    {"code": "rose", "name": "Rose 🌹", "icon": "🌹", "price_coins": 10, "category": "romantic"},
    {"code": "heart", "name": "Heart ❤️", "icon": "❤️", "price_coins": 20, "category": "romantic"},
    {"code": "kiss", "name": "Kiss 💋", "icon": "💋", "price_coins": 30, "category": "romantic"},
    {"code": "ring", "name": "Ring 💍", "icon": "💍", "price_coins": 500, "category": "romantic"},
    {"code": "teddy", "name": "Teddy 🧸", "icon": "🧸", "price_coins": 100, "category": "fun"},
    {"code": "cake", "name": "Cake 🎂", "icon": "🎂", "price_coins": 50, "category": "fun"},
    {"code": "champagne", "name": "Champagne 🍾", "icon": "🍾", "price_coins": 200, "category": "premium"},
    {"code": "diamond", "name": "Diamond 💎", "icon": "💎", "price_coins": 1000, "category": "premium"},
    {"code": "crown", "name": "Crown 👑", "icon": "👑", "price_coins": 5000, "category": "premium"},
    {"code": "firework", "name": "Firework 🎆", "icon": "🎆", "price_coins": 100, "category": "seasonal"},
]


COIN_PACKAGES = [
    {"name": "Starter", "coins": 100, "bonus_coins": 0, "price_stars": 50, "price_usd": 0.99},
    {"name": "Popular", "coins": 500, "bonus_coins": 50, "price_stars": 200, "price_usd": 3.99, "is_popular": True},
    {"name": "Premium", "coins": 1200, "bonus_coins": 200, "price_stars": 500, "price_usd": 7.99},
    {"name": "VIP", "coins": 3000, "bonus_coins": 700, "price_stars": 1000, "price_usd": 14.99},
    {"name": "Mega", "coins": 7500, "bonus_coins": 2500, "price_stars": 2500, "price_usd": 34.99},
    {"name": "Whale", "coins": 20000, "bonus_coins": 8000, "price_stars": 5000, "price_usd": 69.99},
]


SUBSCRIPTION_PLANS = [
    {"code": "plus", "name": "Plus", "tier": 1, "price_stars": 250, "price_usd": 4.99, "duration_days": 30, "features": ["5 superlikes/day", "1 boost/month", "See who liked you", "No ads"], "boost_count": 1, "superlikes_per_day": 5},
    {"code": "gold", "name": "Gold", "tier": 2, "price_stars": 500, "price_usd": 9.99, "duration_days": 30, "features": ["Unlimited likes", "10 superlikes/day", "5 boosts/month", "Read receipts", "Profile boost"], "boost_count": 5, "superlikes_per_day": 10},
    {"code": "platinum", "name": "Platinum", "tier": 3, "price_stars": 1000, "price_usd": 19.99, "duration_days": 30, "features": ["Everything in Gold", "Unlimited boosts", "Message before match", "Priority support", "Travel mode"], "boost_count": 999, "superlikes_per_day": 999},
    {"code": "vip_diamond", "name": "VIP Diamond 👑", "tier": 4, "price_stars": 2500, "price_usd": 49.99, "duration_days": 30, "features": ["Everything in Platinum", "Personal matchmaker", "Exclusive events", "Gift every week", "Profile verification"], "boost_count": 999, "superlikes_per_day": 999, "is_vip": True},
]


CHAT_THEMES = [
    {"name": "Default", "code": "default", "is_free": True, "bubble_color_user": "#f43f5e", "bubble_color_other": "#f1f5f9", "text_color": "#ffffff"},
    {"name": "Dark", "code": "dark", "is_free": True, "bubble_color_user": "#7c3aed", "bubble_color_other": "#1e293b", "text_color": "#ffffff"},
    {"name": "Ocean", "code": "ocean", "is_free": False, "price_coins": 100, "background_url": "/themes/ocean.jpg", "bubble_color_user": "#0891b2", "bubble_color_other": "#155e75", "text_color": "#ffffff"},
    {"name": "Sunset", "code": "sunset", "is_free": False, "price_coins": 100, "background_url": "/themes/sunset.jpg", "bubble_color_user": "#f97316", "bubble_color_other": "#7c2d12", "text_color": "#ffffff"},
    {"name": "Forest", "code": "forest", "is_free": False, "price_coins": 100, "background_url": "/themes/forest.jpg", "bubble_color_user": "#16a34a", "bubble_color_other": "#14532d", "text_color": "#ffffff"},
    {"name": "Galaxy", "code": "galaxy", "is_free": False, "price_coins": 200, "background_url": "/themes/galaxy.jpg", "is_seasonal": True, "bubble_color_user": "#a855f7", "bubble_color_other": "#1e1b4b", "text_color": "#ffffff"},
    {"name": "Valentine", "code": "valentine", "is_free": False, "price_coins": 150, "background_url": "/themes/valentine.jpg", "is_seasonal": True, "bubble_color_user": "#ec4899", "bubble_color_other": "#831843", "text_color": "#ffffff"},
]


STICKER_PACKS = [
    {"name": "Love ❤️", "description": "Romantic stickers", "category": "romantic", "is_free": True, "stickers": [
        {"emoji": "❤️", "image_url": "/stickers/love_heart.png"},
        {"emoji": "😍", "image_url": "/stickers/love_eyes.png"},
        {"emoji": "💋", "image_url": "/stickers/kiss.png"},
        {"emoji": "💕", "image_url": "/stickers/love_letter.png"},
        {"emoji": "🥰", "image_url": "/stickers/love_face.png"},
    ]},
    {"name": "Funny 😂", "description": "Funny memes", "category": "fun", "is_free": True, "stickers": [
        {"emoji": "😂", "image_url": "/stickers/laugh.png"},
        {"emoji": "🤣", "image_url": "/stickers/rofl.png"},
        {"emoji": "😜", "image_url": "/stickers/tongue.png"},
        {"emoji": "😏", "image_url": "/stickers/smirk.png"},
        {"emoji": "🤪", "image_url": "/stickers/crazy.png"},
    ]},
    {"name": "Cute 🐱", "description": "Cute animals", "category": "cute", "is_free": False, "price_coins": 50, "stickers": [
        {"emoji": "🐱", "image_url": "/stickers/cat.png"},
        {"emoji": "🐶", "image_url": "/stickers/dog.png"},
        {"emoji": "🐼", "image_url": "/stickers/panda.png"},
        {"emoji": "🦊", "image_url": "/stickers/fox.png"},
        {"emoji": "🐰", "image_url": "/stickers/rabbit.png"},
    ]},
    {"name": "Uzbek 🇺🇿", "description": "Uzbek culture", "category": "uzbek", "is_free": True, "stickers": [
        {"emoji": "🕌", "image_url": "/stickers/mosque.png"},
        {"emoji": "🥟", "image_url": "/stickers/somsa.png"},
        {"emoji": "🍚", "image_url": "/stickers/plov.png"},
        {"emoji": "🇺🇿", "image_url": "/stickers/flag.png"},
        {"emoji": "🎭", "image_url": "/stickers/theater.png"},
    ]},
]


PROMPTS = [
    {"question": "Mening quvonchli joyim...", "category": "fun", "placeholder": "Yozing..."},
    {"question": "Birgalikda sinab ko'rishimiz kerak bo'lgan narsa...", "category": "fun", "placeholder": "Yozing..."},
    {"question": "Menga noto'g'ri tushunilgan narsa...", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Eng yaxshi do'stim haqida...", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Bir kunda 24 soat bo'lsa...", "category": "fun", "placeholder": "Yozing..."},
    {"question": "Menga yoqadigan va yoqmaydigan...", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Eng yomon sana qaysi?", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Eng yaxshi kecha qaysi?", "category": "fun", "placeholder": "Yozing..."},
    {"question": "Ishonchli odam...", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Biror narsani yo'qotish...", "category": "deep", "placeholder": "Yozing..."},
    {"question": "Meni kuldiradigan narsa...", "category": "fun", "placeholder": "Yozing..."},
    {"question": "Eng so'nggi xarid...", "category": "fun", "placeholder": "Yozing..."},
]


LIFESTYLE_TAGS = [
    {"code": "smoker_yes", "name": "Chekaman", "icon": "🚬", "category": "lifestyle"},
    {"code": "smoker_no", "name": "Chekmayman", "icon": "🚭", "category": "lifestyle"},
    {"code": "drinker_yes", "name": "Ichaman", "icon": "🍷", "category": "lifestyle"},
    {"code": "drinker_no", "name": "Ichmayman", "icon": "🥤", "category": "lifestyle"},
    {"code": "vegan", "name": "Vegan", "icon": "🥗", "category": "dietary"},
    {"code": "vegetarian", "name": "Vegetarian", "icon": "🥦", "category": "dietary"},
    {"code": "halal", "name": "Halol", "icon": "🥩", "category": "dietary"},
    {"code": "kosher", "name": "Kosher", "icon": "✡️", "category": "dietary"},
    {"code": "pet_dog", "name": "It egalari", "icon": "🐕", "category": "pet"},
    {"code": "pet_cat", "name": "Mushuk egalari", "icon": "🐈", "category": "pet"},
    {"code": "muslim", "name": "Muslim", "icon": "☪️", "category": "religion"},
    {"code": "christian", "name": "Christian", "icon": "✝️", "category": "religion"},
    {"code": "atheist", "name": "Ateist", "icon": "🔬", "category": "religion"},
    {"code": "sport", "name": "Sportchi", "icon": "⚽", "category": "lifestyle"},
    {"code": "traveler", "name": "Sayohatchi", "icon": "✈️", "category": "lifestyle"},
    {"code": "bookworm", "name": "Kitobxon", "icon": "📚", "category": "lifestyle"},
    {"code": "gamer", "name": "Gamer", "icon": "🎮", "category": "lifestyle"},
    {"code": "musician", "name": "Musiqachi", "icon": "🎵", "category": "lifestyle"},
    {"code": "artist", "name": "Rassom", "icon": "🎨", "category": "lifestyle"},
    {"code": "introvert", "name": "Introvert", "icon": "🤐", "category": "personality"},
    {"code": "extrovert", "name": "Ekstrovert", "icon": "🎉", "category": "personality"},
    {"code": "ambivert", "name": "Ambivert", "icon": "⚖️", "category": "personality"},
]


async def main():
    async with async_session_maker() as session:
        # Achievements & missions
        await GamificationService.seed_achievements(session)
        await GamificationService.seed_missions(session)

        # Gifts
        r = await session.execute(select(Gift))
        existing_codes = {g.code for g in r.scalars().all()}
        for g in GIFTS:
            if g["code"] not in existing_codes:
                session.add(Gift(**g))
        await session.commit()

        # Coin packages
        from app.models.community import CoinPackage
        r = await session.execute(select(CoinPackage))
        existing_pkgs = {p.name for p in r.scalars().all()}
        for p in COIN_PACKAGES:
            if p["name"] not in existing_pkgs:
                session.add(CoinPackage(**p))
        await session.commit()

        # Subscriptions
        r = await session.execute(select(SubscriptionPlan))
        existing_subs = {s.code for s in r.scalars().all()}
        for s in SUBSCRIPTION_PLANS:
            if s["code"] not in existing_subs:
                session.add(SubscriptionPlan(**s))
        await session.commit()

        # Chat themes
        r = await session.execute(select(ChatTheme))
        existing_themes = {t.code for t in r.scalars().all()}
        for t in CHAT_THEMES:
            if t["code"] not in existing_themes:
                stickers = t.pop("stickers", [])
                theme = ChatTheme(**t)
                session.add(theme)
        await session.commit()

        # Sticker packs
        r = await session.execute(select(StickerPack))
        existing_packs = {p.name for p in r.scalars().all()}
        for p in STICKER_PACKS:
            if p["name"] not in existing_packs:
                stickers = p.pop("stickers")
                pack = StickerPack(**p, sticker_count=len(stickers))
                session.add(pack)
                await session.flush()
                for s in stickers:
                    session.add(Sticker(pack_id=pack.id, **s))
        await session.commit()

        # Prompts
        from app.models.personality import Prompt
        r = await session.execute(select(Prompt))
        existing_prompts = {p.question for p in r.scalars().all()}
        for i, p in enumerate(PROMPTS):
            if p["question"] not in existing_prompts:
                session.add(Prompt(**p, order=i))
        await session.commit()

        # Lifestyle tags
        from app.models.personality import LifestyleTag
        r = await session.execute(select(LifestyleTag))
        existing_tags = {t.code for t in r.scalars().all()}
        for t in LIFESTYLE_TAGS:
            if t["code"] not in existing_tags:
                session.add(LifestyleTag(**t))
        await session.commit()

        # Seasons
        await SeasonService.seed_seasons(session)

        print("✅ Mega seed data loaded successfully!")
        print(f"   - {len(GamificationService.ACHIEVEMENTS)} achievements")
        print(f"   - {len(GamificationService.MISSIONS)} missions")
        print(f"   - {len(GIFTS)} gifts")
        print(f"   - {len(COIN_PACKAGES)} coin packages")
        print(f"   - {len(SUBSCRIPTION_PLANS)} subscription plans")
        print(f"   - {len(CHAT_THEMES)} chat themes")
        print(f"   - {len(STICKER_PACKS)} sticker packs ({sum(len(p['stickers']) for p in STICKER_PACKS)} stickers)")
        print(f"   - {len(PROMPTS)} prompts")
        print(f"   - {len(LIFESTYLE_TAGS)} lifestyle tags")
        print(f"   - {len(SeasonService.SEASONS)} seasonal events")


if __name__ == "__main__":
    asyncio.run(main())
