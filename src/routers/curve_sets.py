from fastapi import APIRouter, Depends, status

from dependencies import get_curve_set_service, get_current_user
from models.user import User
from schemas import CurveSet, CurveSetCreate, UploadedCurveSet
from schemas.curve_set import CurveSetPatch, CurveSetSummary, CurveSetUserDataCreate
from schemas.generation_config import CurveSetConfig
from services.curve_sets import CurveSetsService

curve_sets_router = APIRouter(tags=["curve-sets"])


@curve_sets_router.get(
    "",
    response_model=list[CurveSetSummary],
    summary="List all curve sets belonging to the current user",
)
def handle_list_curve_sets(
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_all_for_user(current_user.id)


@curve_sets_router.get(
    "/{curve_set_id}",
    response_model=CurveSet,
    summary="Get a single curve set (with curves) owned by the current user",
)
def handle_get_curve_set(
    curve_set_id: int,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_curve_set(curve_set_id, current_user.id)


@curve_sets_router.post(
    "/create",
    response_model=CurveSet,
    status_code=status.HTTP_201_CREATED,
    summary="Create an empty curve set",
)
def handle_create_curve_set(
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_curve_set(CurveSetCreate(), current_user.id)


@curve_sets_router.post(
    "/generate",
    response_model=CurveSet,
    status_code=status.HTTP_201_CREATED,
    summary="Generate a synthetic curve set from a configuration",
)
def handle_generate_curve_set(
    config: CurveSetConfig,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.generate_curve_set(config, current_user.id)


@curve_sets_router.post(
    "/upload",
    response_model=CurveSet,
    status_code=status.HTTP_201_CREATED,
    summary="Upload raw time/intensity arrays to create a new curve set",
)
def handle_upload_curve_set(
    payload: UploadedCurveSet,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_curve_set_from_uploaded(payload, current_user.id)


@curve_sets_router.post(
    "/from_data",
    response_model=CurveSet,
    status_code=status.HTTP_201_CREATED,
    summary="Create a curve set from structured curve data",
)
def handle_create_from_user_data(
    payload: CurveSetUserDataCreate,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.create_curve_set(payload.to_curve_set_create(), current_user.id)


@curve_sets_router.patch(
    "/{curve_set_id}",
    response_model=CurveSet,
    summary="Partially update a curve set owned by the current user",
)
def handle_patch_curve_set(
    curve_set_id: int,
    data: CurveSetPatch,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    return service.update_curve_set(curve_set_id, data, current_user.id)


@curve_sets_router.delete(
    "/{curve_set_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a curve set owned by the current user",
)
def handle_delete_curve_set(
    curve_set_id: int,
    service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    service.delete_curve_set(curve_set_id, current_user.id)
