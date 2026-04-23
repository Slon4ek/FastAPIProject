from src.models.images import ImagesOrm
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import ImagesDataMapper


class ImagesRepository(BaseRepository):
    model = ImagesOrm
    mapper = ImagesDataMapper
