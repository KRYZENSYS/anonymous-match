"""Seed data"""
import asyncio
import random
from datetime import date, timedelta
from app.db.session import async_session_maker
from app.models.user import User
from app.services.user import generate_public_id


SAMPLE = [
    {"first_name": "Aziza", "nickname": "SweetRose", "gender": "female", "region": "Toshkent", "interests": ["Musiqa", "Kino", "Sayohat"], "bio": "Kitobxon"},
    {"first_name": "Bobur", "nickname": "TechBro", "gender": "male", "region": "Samarqand", "interests": ["Texnologiya", "Sport"], "bio": "Dasturchi"},
    {"first_name": "Dilshod", "nickname": "MusicLover", "gender": "male", "region": "Toshkent", "interests": ["Musiqa", "Raqs"], "bio": "Musiqa — hayot"},
    {"first_name": "Erika", "nickname": "TravelGirl", "gender": "female", "region": "Buxoro", "interests": ["Sayohat", "Foto"], "bio": "Dunyo kezuvchi"},
    {"first_name": "Farrux", "nickname": "ChefMaster", "gender": "male", "region": "Farg'ona", "interests": ["Ovqat", "Pishiriq"], "bio": "Oshpaz"},
    {"first_name": "Gulnora", "nickname": "BookWorm", "gender": "female", "region": "Andijon", "interests": ["Kitob", "San'at"], "bio": "Adabiyot"},
    {"first_name": "Hasan", "nickname": "FitBoy", "gender": "male", "region": "Toshkent", "interests": ["Sport", "Fitnes"], "bio": "Sog'lik"},
    {"first_name": "Iroda", "nickname": "ArtistSoul", "gender": "female", "region": "Namangan", "interests": ["San'at", "Musiqa"], "bio": "Rassom"},
    {"first_name": "Jasur", "nickname": "GameOn", "gender": "male", "region": "Toshkent", "interests": ["O'yinlar"], "bio": "Gamer"},
    {"first_name": "Kamila", "nickname": "YogaLife", "gender": "female", "region": "Samarqand", "interests": ["Fitnes", "Tabiat"], "bio": "Yoga"},
    {"first_name": "Laziz", "nickname": "CarLover", "gender": "male", "region": "Toshkent", "interests": ["Avtomobil"], "bio": "Cars"},
    {"first_name": "Madina", "nickname": "DanceQueen", "gender": "female", "region": "Buxoro", "interests": ["Raqs", "Musiqa"], "bio": "Raqosa"},
]


async def seed():
    async with async_session_maker() as session:
        for data in SAMPLE:
            age = random.randint(20, 35)
            user = User(telegram_id=random.randint(100000000, 999999999), public_id=generate_public_id(), nickname=data["nickname"], first_name=data["first_name"], gender=data["gender"], looking_for="everyone", birth_date=date.today() - timedelta(days=age*365), region=data["region"], city=data["region"], bio=data["bio"], interests=data["interests"], photos=[f"https://i.pravatar.cc/600?u={data['nickname']}"], language_code="uz", is_profile_complete=True, is_verified=random.random() < 0.3, is_premium=random.random() < 0.2)
            session.add(user)
        await session.commit()
    print(f"✅ {len(SAMPLE)} users seeded")


if __name__ == "__main__":
    asyncio.run(seed())
