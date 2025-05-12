from repositories.analysis_results import AnalysisResultsRepository
from repositories.curve_set import CurveSetRepository
from schemas import AnalysisResult, AnalysisResultCreate
from schemas.analysis_config import AnalysisConfig
from schemas.analysis_result import AnalysisResultPatch
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

    def create_result(self, data: AnalysisConfig) -> AnalysisResult:
        curve_set_db = self.curve_set_repo.get_by_id(data.curve_set_id)
        curve_set = CurveSet.model_validate(curve_set_db, from_attributes=True)
        # print(curve_set.curves)

        phasor = PhasorAnalyzer(curve_set)
        
        dws = phasor.calc_D()
        v, u = phasor.approx_fourier()
        tau1, tau2 = phasor.calc_taus()
        a1s, a2s = phasor.calc_a_coeffs()
        result = AnalysisResultCreate(
            curve_set_id=curve_set.id,
            dw_real=[x.real for x in dws],
            dw_imag=[x.imag for x in dws],
            coeff_v=v,
            coeff_u=u,
            tau1=tau1,
            tau2=tau2,
            a1_coeffs=a1s,
            a2_coeffs=a2s,
            omega=phasor.omega
            )

        result_db = self.repo.create(result)
        result_ser = AnalysisResult.model_validate(result_db, from_attributes=True)
        return result_ser

    def update_result(self, id: int, data: AnalysisResultPatch) -> AnalysisResult:
        result_db = self.repo.update(id, data)
        result = AnalysisResult.model_validate(result_db, from_attributes=True)
        return result

    def delete_result(self, id: int) -> bool:
        try:
            self.repo.delete(id)
            return True
        except:
            return False