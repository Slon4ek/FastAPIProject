import os
import shutil
from fastapi import APIRouter, UploadFile, HTTPException

from src.exceptions import ImageUploadError, ImageUploadHTTPException
from src.tasks.tasks import compress_image
from src.utils.upload_validation import validate_image_file

router = APIRouter(prefix="/images", tags=["Работа с изображениями"])


@router.post("")
async def upload_image(file: UploadFile, hotel_id: int | None = None, room_id: int | None = None):
    try:
        validate_image_file(file.filename, file.content_type)  # noqa
    except ImageUploadError as e:
        raise ImageUploadHTTPException(status_code=415, detail=str(e))

    img_path = f"src/static/images/{file.filename}"
    imgs_dir = "src/static/images"

    try:
        with open(img_path, "wb+") as new_file:
            shutil.copyfileobj(file.file, new_file)  # noqa
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при сохранении файла: {str(e)}")

    try:
        if hotel_id:
            imgs_dir = f"src/static/images/hotels/{hotel_id}"
        if room_id:
            imgs_dir = f"src/static/images/hotels/{hotel_id}/rooms/{room_id}"

        compress_image.delay(img_path, imgs_dir, hotel_id, room_id)
        return {"message": "Image uploaded successfully"}
    except Exception as e:
        if os.path.exists(img_path):
            os.remove(img_path)
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке изображения: {str(e)}")
