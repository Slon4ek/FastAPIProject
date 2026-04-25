from src.models.bookings import BookingsOrm
from src.models.facilities import FacilitiesOrm, RoomsFacilitiesOrm
from src.models.hotels import HotelsOrm
from src.models.images import ImagesOrm
from src.models.rooms import RoomsOrm
from src.models.users import UsersOrm
from src.repositories.mappers.base import DataMapper
from src.schemas.bookings import Booking, BookingAdd
from src.schemas.facility import Facility, RoomFacilities
from src.schemas.hotels import Hotel, HotelWithRelations
from src.schemas.images import Image
from src.schemas.rooms import RoomWithRelations, Room
from src.schemas.users import User


class HotelsDataMapper(DataMapper):
    db_model = HotelsOrm
    schema = Hotel


class HotelsWithRelationsDataMapper(HotelsDataMapper):
    schema = HotelWithRelations


class RoomsDataMapper(DataMapper):
    db_model = RoomsOrm
    schema = Room


class RoomsWithRelationsDataMapper(RoomsDataMapper):
    schema = RoomWithRelations


class BookingsDataMapper(DataMapper):
    db_model = BookingsOrm
    schema = Booking


class BookingsAddDataMapper(BookingsDataMapper):
    schema = BookingAdd


class UsersDataMapper(DataMapper):
    db_model = UsersOrm
    schema = User


class FacilitiesDataMapper(DataMapper):
    db_model = FacilitiesOrm
    schema = Facility


class RoomFacilitiesDataMapper(DataMapper):
    db_model = RoomsFacilitiesOrm
    schema = RoomFacilities


class ImagesDataMapper(DataMapper):
    db_model = ImagesOrm
    schema = Image
