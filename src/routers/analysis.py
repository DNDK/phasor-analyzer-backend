from fastapi import APIRouter, Depends

from dependencies import get_analysis_results_service
from services.analysis_results import AnalysisResultsService
from schemas.analysis_config import AnalysisConfig

analysis_router = APIRouter()

@analysis_router.post('/start')
def handle_analysis_start(config: AnalysisConfig, service: AnalysisResultsService = Depends(get_analysis_results_service)):
    service.create_result(config)
    return config.model_dump()

@analysis_router.get('/{id}')
def handle_get_results(id: int, service: AnalysisResultsService = Depends(get_analysis_results_service)):
    yoo_yoo = service.get_analysis_results(id)
    return yoo_yoo