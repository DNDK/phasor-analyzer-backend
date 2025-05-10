from repositories.analysis_results import AnalysisResultsRepository
from repositories.curve_set import CurveSetRepository
from schemas import AnalysisResult, AnalysisResultCreate
from schemas.analysis_config import AnalysisConfig
from schemas.curve_set import CurveSet

from computing.phasor_analyzer import PhasorAnalyzer

class AnalysisResultsService:
    def __init__(self, analysis_results_repo: AnalysisResultsRepository, curve_set_repo: CurveSetRepository):
        self.repo = analysis_results_repo
        self.curve_set_repo = curve_set_repo

    def get_analysis_results(self, id):
        curve = self.repo.get_by_id(id)

        analysis_results_ser = AnalysisResult.model_validate(curve)
        return analysis_results_ser

    def create_curve(self, data: AnalysisResultCreate) -> AnalysisResult:
        crv = self.repo.create(data=data)
        return AnalysisResult.model_validate(crv)

    def create_result(self, data: AnalysisConfig):
        curve_set_db = self.curve_set_repo.get_by_id(data.curve_set_id)
        curve_set = CurveSet.model_validate(curve_set_db, from_attributes=True)

        # phasor = PhasorAnalyzer()

        print(curve_set)
