from fastapi import APIRouter, Depends, HTTPException, status

from dependencies import get_analysis_results_service, get_curve_set_service, get_current_user
from enums.curve_set_status import CurveSetStatus
from models.user import User
from schemas import AnalysisResult
from schemas.analysis_config import AnalysisConfig, UserDataAnalysisConfig
from schemas.curve_set import CurveSetPatch
from services.analysis_results import AnalysisResultsService
from services.curve_sets import CurveSetsService

analysis_router = APIRouter(tags=["analysis"])


@analysis_router.post(
    "/start",
    response_model=AnalysisResult,
    summary="Run phasor analysis on an existing curve set",
)
def handle_analysis_start(
    config: AnalysisConfig,
    analysis_service: AnalysisResultsService = Depends(get_analysis_results_service),
    curve_set_service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    # Fetch and verify ownership
    curve_set_db = curve_set_service.curveset_repo.get_by_id_for_user(
        config.curve_set_id, current_user.id
    )
    if curve_set_db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curve set not found.")
    if not curve_set_db.curves:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Curve set has no curves to analyse.",
        )

    # Mark as running
    curve_set_service.curveset_repo.update(config.curve_set_id, CurveSetPatch(status=CurveSetStatus.RUNNING))

    try:
        result = analysis_service.run_analysis_for_curve_set(curve_set_db, current_user.id)
        curve_set_service.curveset_repo.update(
            config.curve_set_id,
            CurveSetPatch(status=CurveSetStatus.COMPLETED, processing_time=result.processing_time),
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        curve_set_service.curveset_repo.update(
            config.curve_set_id, CurveSetPatch(status=CurveSetStatus.FAILED)
        )
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@analysis_router.post(
    "/process",
    summary="Create a curve set from raw data and immediately analyse it",
)
def handle_process_user_data(
    config: UserDataAnalysisConfig,
    analysis_service: AnalysisResultsService = Depends(get_analysis_results_service),
    curve_set_service: CurveSetsService = Depends(get_curve_set_service),
    current_user: User = Depends(get_current_user),
):
    try:
        curve_set_db_orm = curve_set_service.curveset_repo.create_with_curves(
            config.to_curve_set_create(), current_user.id
        )
        curve_set_service.curveset_repo.update(
            curve_set_db_orm.id, CurveSetPatch(status=CurveSetStatus.RUNNING)
        )
        result = analysis_service.run_analysis_for_curve_set(curve_set_db_orm, current_user.id)
        curve_set_service.curveset_repo.update(
            curve_set_db_orm.id,
            CurveSetPatch(status=CurveSetStatus.COMPLETED, processing_time=result.processing_time),
        )
        from schemas.curve_set import CurveSet
        return {
            "curve_set": CurveSet.model_validate(curve_set_db_orm, from_attributes=True),
            "analysis_result": result,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@analysis_router.get(
    "/{result_id}",
    response_model=AnalysisResult,
    summary="Retrieve an analysis result (must be linked to a curve set you own)",
)
def handle_get_results(
    result_id: int,
    service: AnalysisResultsService = Depends(get_analysis_results_service),
    current_user: User = Depends(get_current_user),
):
    return service.get_analysis_results(result_id, current_user.id)
