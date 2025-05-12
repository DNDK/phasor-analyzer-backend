from fastapi import APIRouter, Depends
from schemas import CurveSet, CurveSetCreate, Curve, CurveCreate
from schemas.curve_set import CurveSetPatch
from schemas.generation_config import CurveSetConfig, IrfConfig, CurveConfig
from dependencies import get_curve_set_servie
from services.curve_sets import CurveSetsService


curve_sets_router = APIRouter()


@curve_sets_router.post('/create')
def handle_create_curve_set(service: CurveSetsService = Depends(get_curve_set_servie)):
    curve_conf = CurveSetCreate(curves=[])
    curveset = service.create_curve_set(curve_conf)
    return curveset


@curve_sets_router.get('/ping')
async def handle_ping(serv: CurveSetsService = Depends(get_curve_set_servie)):
    # a = await serv.get_curve_set(1)
    # print(a)
    yee = serv.get_curve_set(1)
    return yee

@curve_sets_router.post('/generate_curve_set')
def handle_generate_curve_set(config: CurveSetConfig, curve_set_service: CurveSetsService = Depends(get_curve_set_servie)):
    # test_config = CurveSetConfig(
    # a1_coeffs=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],  # коэффициенты a1 для 5 кривых
    # num_curves=9,  # количество кривых (можно не указывать, если равно длине a1_coeffs)
    
    # # Переопределяем некоторые параметры из SingleSetShared (опционально)
    # tau1=1,
    # tau2=3,
    # add_noise=False,  # отключаем шум для теста
    
    # # Настраиваем IRF (Instrument Response Function)
    # irf_config=IrfConfig(
    #         m=1.8,          # немного меняем параметры IRF
    #         sigma=0.1,
    #         strg=10000
    #     )
    # )

    cs = curve_set_service.generate_curve_set(config)
    return cs

@curve_sets_router.get('/{set_id}')
def handle_get_curve_set(set_id: int):
    print(set_id)

# @curve_sets_router.patch('/add_curve/{id}')
# def handle_add_curve(set_id: int):
#     pass

@curve_sets_router.patch("/{id}")
def handle_patch_task(id: int, data: CurveSetPatch, service: CurveSetsService = Depends(get_curve_set_servie)):
    task = service.update_curve_set(id, data)
    return task

@curve_sets_router.delete("/{id}")
def handle_delete_task(id: int, service: CurveSetsService = Depends(get_curve_set_servie)):
    success = service.delete_curve_set(id)
    if success:
        return {"message": "OK"}
    else:
        return {"message": "FAIL"}