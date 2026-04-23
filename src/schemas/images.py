from pydantic import BaseModel


class ImageAdd(BaseModel):
    name: str
    image_dir_path: str
    room_id: int | None = None
    hotel_id: int | None = None


class Image(ImageAdd):
    id: int
