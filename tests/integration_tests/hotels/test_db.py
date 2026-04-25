from src.schemas.hotels import HotelAdd
from src.utils.db_manager import DBManager


async def test_hotel_add(db: DBManager):
    hotel_data = HotelAdd(
        title="Test Hotel",
        stars=5,
        location="Test Location",
    )
    await db.hotels.add(hotel_data)
    await db.commit()
