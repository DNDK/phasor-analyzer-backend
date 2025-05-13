from fastapi import APIRouter, Depends, HTTPException

from dependencies import get_analysis_results_service, get_task_servie
from services.analysis_results import AnalysisResultsService
from schemas.analysis_config import AnalysisConfig
from services.task import TaskService

analysis_router = APIRouter()

@analysis_router.post('/start')
def handle_analysis_start(config: AnalysisConfig, service: AnalysisResultsService = Depends(get_analysis_results_service), task_service: TaskService = Depends(get_task_servie)):
    # service.create_result(config)
    # return config.model_dump()
    task = task_service.get_task(config.task_id)
    if task is not None and task.curve_set is not None:
        anal = service.create_result(task)
        return anal
    else:
        raise HTTPException(status_code=404, detail="Either Task or CurveSet was not found")


@analysis_router.get('/{id}')
def handle_get_results(id: int, service: AnalysisResultsService = Depends(get_analysis_results_service)):
    results = service.get_analysis_results(id)
    return results