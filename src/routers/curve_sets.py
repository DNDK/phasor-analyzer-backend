from fastapi import APIRouter, Depends
from schemas import CurveSet, CurveSetCreate, Curve, CurveCreate
from dependencies import get_curve_set_servie
from services.curve_sets import CurveSetsService

curve_sets_router = APIRouter()


@curve_sets_router.post('/create')
def handle_create_curve_set():
    pass


@curve_sets_router.get('/ping')
async def handle_ping(serv: CurveSetsService = Depends(get_curve_set_servie)):
    # a = await serv.get_curve_set(1)
    # print(a)
    await serv.get_curve_set(0)
    return {'a': 'dick'}

@curve_sets_router.get('/{set_id}')
def handle_get_curve_set(set_id: int):
    print(set_id)

@curve_sets_router.patch('/add_curve/{id}')
def handle_add_curve(set_id: int):
    pass

