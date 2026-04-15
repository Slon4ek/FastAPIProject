import asyncio
import os

from PIL import Image
from pydantic import BaseModel

from src.database import async_session_maker_null_pool
from src.schemas.images import ImageAdd
from src.tasks.celery_app import celery_app
from src.utils.db_manager import DBManager


async def add_img_to_db(data_list: list[BaseModel]):
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        await db.images.add_bulk(data_list)
        await db.commit()

@celery_app.task
def compress_image(
        img_path: str,
        output_dir: str = "src/static/images",
        hotel_id: int = None,
        room_id: int = None
):
    """
    Сжимает изображение до заданных размеров и сохраняет в указанную директорию.

    :param room_id: ID номера, если изображение принадлежит к номеру
    :param hotel_id: ID отеля, если изображение принадлежит к отелю
    :param img_path: Путь к исходному изображению
    :param output_dir: Директория для сохранения сжатых изображений
    """
    images = []
    # Открываем изображение
    sizes: list = [1000, 500, 200]
    with Image.open(img_path) as img:
        # Получаем оригинальные размеры
        original_width, original_height = img.size

        # Создаем директорию для сохранения, если её нет
        os.makedirs(output_dir, exist_ok=True)

        # Обрабатываем каждый размер
        for size in sizes:
            # Вычисляем новые размеры с сохранением пропорций
            aspect_ratio = original_height / original_width
            new_height = int(size * aspect_ratio)

            # Создаем уменьшенную копию
            resized_img = img.resize((size, new_height), Image.Resampling.LANCZOS)

            # Сохраняем изображение с уникальным именем
            filename = os.path.basename(img_path)
            name, ext = os.path.splitext(filename)
            output_path = os.path.join(output_dir, f"{name}_{size}{ext}")

            img_data = ImageAdd(
                name = os.path.basename(output_path),
                image_dir_path=output_dir,
                hotel_id=hotel_id,
                room_id=room_id
            )
            images.append(img_data)

            resized_img.save(output_path, quality=85, optimize=True)

        asyncio.run(add_img_to_db(images))

async def get_booking_with_today_checkin_helper():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        bookings = await db.bookings.get_booking_with_today_checkin()
        print(bookings)

@celery_app.task(name="send_emails_today_checkin")
def send_emails_to_users_with_today_checkin():
    asyncio.run(get_booking_with_today_checkin_helper())