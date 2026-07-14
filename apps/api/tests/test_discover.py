import pytest
from datetime import date, timedelta


@pytest.mark.asyncio
async def test_swipe_creates_like(client, db_session):
    from app.services.user import UserService
    from app.services.auth import create_access_token
    u1, _ = await UserService.get_or_create(db_session, telegram_id=111111)
    u1.nickname = "TestA"; u1.gender = "male"; u1.birth_date = date(2000, 1, 1)
    u1.region = "Toshkent"; u1.interests = ["Musiqa", "Sport", "Texnologiya"]
    u1.photos = ["https://example.com/1.jpg"]; u1.is_profile_complete = True
    u2, _ = await UserService.get_or_create(db_session, telegram_id=222222)
    u2.nickname = "TestB"; u2.gender = "female"; u2.birth_date = date(2002, 1, 1)
    u2.region = "Toshkent"; u2.interests = ["Musiqa", "Sport", "Texnologiya"]
    u2.photos = ["https://example.com/2.jpg"]; u2.is_profile_complete = True
    await db_session.commit()
    token = create_access_token(u1.id)
    headers = {"Authorization": f"Bearer {token}"}
    r = await client.post("/api/v1/discover/swipe", headers=headers, json={"target_user_id": u2.id, "action": "like"})
    assert r.status_code == 200
    data = r.json()
    assert "is_match" in data


@pytest.mark.asyncio
async def test_mutual_like_creates_match(client, db_session):
    from app.services.user import UserService
    from app.services.discover import DiscoverService
    u1, _ = await UserService.get_or_create(db_session, telegram_id=333333)
    u1.nickname = "MutualA"; u1.gender = "male"; u1.birth_date = date(2000, 1, 1)
    u1.region = "Toshkent"; u1.interests = ["A", "B", "C"]
    u1.photos = ["x"]; u1.is_profile_complete = True
    u2, _ = await UserService.get_or_create(db_session, telegram_id=444444)
    u2.nickname = "MutualB"; u2.gender = "female"; u2.birth_date = date(2000, 1, 1)
    u2.region = "Toshkent"; u2.interests = ["A", "B", "C"]
    u2.photos = ["x"]; u2.is_profile_complete = True
    await db_session.commit()
    await DiscoverService.swipe(db_session, u1.id, u2.id, "like")
    r2 = await DiscoverService.swipe(db_session, u2.id, u1.id, "like")
    assert r2["is_match"] is True
    assert r2["match_id"] is not None
