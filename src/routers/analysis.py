from fastapi import APIRouter, Depends

from dependencies import get_analysis_results_service
from services.analysis_results import AnalysisResultsService

analysis_router = APIRouter()

@analysis_router.post('/start')
def handle_analysis_start(servive: AnalysisResultsService = Depends(get_analysis_results_service)):
	print('dick')
	pass