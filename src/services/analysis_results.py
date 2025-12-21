from models.task import Task
from repositories.analysis_results import AnalysisResultsRepository
from repositories.curve_set import CurveSetRepository
from schemas import AnalysisResult, AnalysisResultCreate
from schemas.analysis_config import AnalysisConfig
from schemas.analysis_result import AnalysisResultPatch
from schemas.curve_set import CurveSet

from computing.phasor_analyzer import PhasorAnalyzer
import math
import numpy as np


def _sanitize_number(val):
    """Return None for non-finite numbers to keep JSON/DB safe."""
    if val is None:
        return None
    if isinstance(val, (float, int)):
        return val if math.isfinite(val) else None
    if isinstance(val, np.generic):
        return float(val) if math.isfinite(val) else None
    return None


def _sanitize_sequence(seq):
    return [ _sanitize_number(v) for v in seq ]

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

    def create_result(self, data: Task) -> AnalysisResult:
        # curve_set_db = self.curve_set_repo.get_by_id(data.curve_set_id)
        # curve_set = CurveSet.model_validate(curve_set_db, from_attributes=True)
        # # print(curve_set.curves)

        curve_set = data.curve_set

        phasor = PhasorAnalyzer(curve_set)
        
        dws = phasor.calc_D()
        v, u = phasor.approx_fourier()
        tau1, tau2 = phasor.calc_taus()
        a1s, a2s = phasor.calc_a_coeffs()
        # sanitize non-finite values before persisting/serializing
        dw_real = _sanitize_sequence([x.real for x in dws])
        dw_imag = _sanitize_sequence([x.imag for x in dws])
        v_s, u_s = _sanitize_number(v), _sanitize_number(u)
        tau1_s, tau2_s = _sanitize_number(tau1), _sanitize_number(tau2)
        a1s_s = _sanitize_sequence(a1s)
        a2s_s = _sanitize_sequence(a2s)
        omega_s = _sanitize_number(phasor.omega)
        result = AnalysisResultCreate(
            curve_set_id=curve_set.id,
            dw_real=dw_real,
            dw_imag=dw_imag,
            coeff_v=v_s,
            coeff_u=u_s,
            tau1=tau1_s,
            tau2=tau2_s,
            a1_coeffs=a1s_s,
            a2_coeffs=a2s_s,
            omega=omega_s
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
