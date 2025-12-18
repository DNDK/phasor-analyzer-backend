from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_analysis_results_service, get_task_servie, get_curve_set_servie
from services.analysis_results import AnalysisResultsService
from services.curve_sets import CurveSetsService
from schemas.analysis_config import AnalysisConfig, UserDataAnalysisConfig
from services.task import TaskService
from schemas.task import TaskBase, TaskPatch, TaskStatus

analysis_router = APIRouter()

@analysis_router.post('/start')
def handle_analysis_start(config: AnalysisConfig, service: AnalysisResultsService = Depends(get_analysis_results_service), task_service: TaskService = Depends(get_task_servie)):
    # service.create_result(config)
    # return config.model_dump()
    task = task_service.get_task(config.task_id)
    if task.curve_set is None:
        raise HTTPException(status_code=404, detail="Either Task or CurveSet was not found")

    task_service.update_task(task.id, TaskPatch(status=TaskStatus.RUNNING))

    try:
        analysis_result = service.create_result(task)
        task_service.update_task(
            task.id,
            TaskPatch(status=TaskStatus.COMPLETED, analysis_results_id=analysis_result.id),
        )
        return analysis_result
    except Exception as exc:
        task_service.update_task(task.id, TaskPatch(status=TaskStatus.FAILED))
        raise HTTPException(status_code=500, detail=str(exc))

@analysis_router.post('/process_user_data')
def handle_process_user_data(
    config: UserDataAnalysisConfig,
    analysis_service: AnalysisResultsService = Depends(get_analysis_results_service),
    task_service: TaskService = Depends(get_task_servie),
    curve_set_service: CurveSetsService = Depends(get_curve_set_servie),
):
    # Create task and link provided curves as a curve set, then run analysis
    task = task_service.init_task(
        TaskBase(
            created_at=datetime.utcnow(),
            status=TaskStatus.RUNNING,
            title=config.task_title,
        )
    )
    try:
        curve_set = curve_set_service.create_curve_set_for_task(config.to_curve_set_create(), task.id)
        task_with_curves = task_service.get_task(task.id)
        analysis_result = analysis_service.create_result(task_with_curves)
        task_service.update_task(
            task.id,
            TaskPatch(status=TaskStatus.COMPLETED, analysis_results_id=analysis_result.id),
        )
        return {
            "task": task_service.get_task(task.id),
            "curve_set": curve_set,
            "analysis_result": analysis_result,
        }
    except Exception as exc:
        task_service.update_task(task.id, TaskPatch(status=TaskStatus.FAILED))
        raise HTTPException(status_code=400, detail=str(exc))


@analysis_router.get('/{id}')
def handle_get_results(id: int, service: AnalysisResultsService = Depends(get_analysis_results_service)):
    results = service.get_analysis_results(id)
    return results
