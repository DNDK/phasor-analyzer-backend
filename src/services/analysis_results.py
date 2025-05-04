from repositories.analysis_results import AnalysisResultsRepository
from schemas import AnalysisResult, AnalysisResultCreate

class AnalysisResultsService:
    def __init__(self, analysis_results_repo: AnalysisResultsRepository):
        self.repo = analysis_results_repo

    async def get_analysis_results(self, id):
        curve = await self.repo.get_by_id(id)

        analysis_results_ser = AnalysisResult.model_validate(curve)
        return analysis_results_ser

    async def create_curve(self, data: AnalysisResultCreate) -> AnalysisResult:
        crv = await self.repo.create(data=data.model_dump())
        return AnalysisResult.model_validate(crv)

