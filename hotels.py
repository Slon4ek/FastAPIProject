from fastapi import APIRouter, Query
from schemas.hotels import Hotel, HotelPatch

router = APIRouter(prefix="/hotels", tags=["Отели"])


hotels = [
    {'id': 1, 'title': 'Hilton', 'stars': 5},
    {'id': 2, 'title': 'Sheraton', 'stars': 4},
    {'id': 2, 'title': 'December', 'stars': 4},
    {'id': 3, 'title': 'Four Seasons', 'stars': 3},
    {'id': 4, 'title': 'Marriott Hotel', 'stars': 2},
    {'id': 4, 'title': 'Marriott', 'stars': 2},
    {'id': 5, 'title': 'Ritz-Carlton', 'stars': 1},
]

@router.get('', summary='Получить список отелей')
def get_hotels(
        stars: int | None = Query(None, description="Фильтр по количеству звезд"),
        title: str | None = Query(None, description="Фильтр по названию отеля"),
):
    hotels_ = []
    for hotel in hotels:
        if stars and hotel["stars"] != stars:
            continue
        if title and hotel["title"] != title:
            continue
        hotels_.append(hotel)
    return hotels_ if hotels_ else hotels


@router.delete('/{hotel_id}', summary='Удалить отель')
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {'message': 'Отель успешно удален'}


@router.post('', summary='Добавить отель')
def create_hotel(
        hotel_data: Hotel
):
    global hotels
    hotels.append({
        'id': hotels[-1]['id'] + 1,
        'title': hotel_data.title,
        'stars': hotel_data.stars
    })
    return {'message': 'Отель успешно добавлен'}


@router.put('/{hotel_id}', summary='Полное обновление данных об отеле')
def update_hotel(hotel_id: int, hotel_data: Hotel):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            hotel['title'] = hotel_data.title
            hotel['stars'] = hotel_data.stars
            return {'message': 'Отель успешно обновлен'}
    return {'message': 'Отель не найден'}

@router.patch('/{hotel_id}', summary='Частичное обновление данных об отеле')
def partial_update_hotel(
        hotel_id: int, hotel_data: HotelPatch
):
    global hotels
    for hotel in hotels:
        if hotel['id'] == hotel_id:
            if hotel_data.title:
                hotel['title'] = hotel_data.title
            if hotel_data.stars:
                hotel['stars'] = hotel_data.stars
            return {'message': 'Отель успешно обновлен'}
    return {'message': 'Отель не найден'}