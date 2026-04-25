import shutil
from fastapi import APIRouter, UploadFile

from src.tasks.tasks import compress_image

router = APIRouter(prefix="/images", tags=["Работа с изображениями"])


@router.post("")
async def upload_image(file: UploadFile, hotel_id: int | None = None, room_id: int | None = None):
    img_path = f"src/static/images/{file.filename}"
    imgs_dir = "src/static/images"

    with open(img_path, "wb+") as new_file:
        shutil.copyfileobj(file.file, new_file)

    if hotel_id:
        imgs_dir = f"src/static/images/hotels/{hotel_id}"
    if room_id:
        imgs_dir = f"src/static/images/hotels/{hotel_id}/rooms/{room_id}"

    compress_image.delay(img_path, imgs_dir, hotel_id, room_id)
    return {"message": "Image uploaded successfully"}
