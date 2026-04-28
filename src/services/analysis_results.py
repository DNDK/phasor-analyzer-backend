import math
import time

import numpy as np
from fastapi import HTTPException, status

from models.curve_set import CurveSet as CurveSetModel
from repositories.analysis_results import AnalysisResultsRepository
from repositories.curve_set import CurveSetRepository
from schemas import AnalysisResult, AnalysisResultCreate
from schemas.analysis_result import AnalysisResultPatch
from schemas.curve_set import CurveSet

from computing.phasor_analyzer import PhasorAnalyzer


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
    return [_sanitize_number(v) for v in seq]


class AnalysisResultsService:
    def __init__(
        self,
        analysis_results_repo: AnalysisResultsRepository,
        curve_set_repo: CurveSetRepository,
    ):
        self.repo = analysis_results_repo
        self.curve_set_repo = curve_set_repo

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_analysis_results(self, result_id: int, user_id: int) -> AnalysisResult:
        """Return an analysis result only if the linked curve set is owned by *user_id*."""
        result_db = self.repo.get_by_id(result_id)
        if result_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found.")

        # Ownership check via the curve set
        curve_set = self.curve_set_repo.get_by_id_for_user(result_db.curve_set_id, user_id)
        if curve_set is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        return AnalysisResult.model_validate(result_db, from_attributes=True)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def run_analysis_for_curve_set(
        self, curve_set_db: CurveSetModel, user_id: int
    ) -> AnalysisResult:
        """Run phasor analysis on a curve set and persist the result."""
        # Verify ownership
        if curve_set_db.user_id != user_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

        curve_set = CurveSet.model_validate(curve_set_db, from_attributes=True)

        t_start = time.perf_counter()
        phasor = PhasorAnalyzer(curve_set)
        
        dws = phasor.calc_D()
        v, u = phasor.approx_fourier()
        tau1, tau2 = phasor.calc_taus()
        a1s, a2s = phasor.calc_a_coeffs()
        elapsed = time.perf_counter() - t_start

        result = AnalysisResultCreate(
            curve_set_id=curve_set.id,
            processing_time=round(elapsed, 6),
            dw_real=_sanitize_sequence([x.real for x in dws]),
            dw_imag=_sanitize_sequence([x.imag for x in dws]),
            coeff_v=_sanitize_number(v),
            coeff_u=_sanitize_number(u),
            tau1=_sanitize_number(tau1),
            tau2=_sanitize_number(tau2),
            a1_coeffs=_sanitize_sequence(a1s),
            a2_coeffs=_sanitize_sequence(a2s),
            omega=_sanitize_number(phasor.omega),
        )

        result_db = self.repo.create(result)
        return AnalysisResult.model_validate(result_db, from_attributes=True)

    # ------------------------------------------------------------------
    # Mutation / Deletion
    # ------------------------------------------------------------------

    def update_result(self, result_id: int, data: AnalysisResultPatch, user_id: int) -> AnalysisResult:
        result_db = self.repo.get_by_id(result_id)
        if result_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found.")
        curve_set = self.curve_set_repo.get_by_id_for_user(result_db.curve_set_id, user_id)
        if curve_set is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        updated = self.repo.update(result_id, data)
        return AnalysisResult.model_validate(updated, from_attributes=True)

    def delete_result(self, result_id: int, user_id: int) -> bool:
        result_db = self.repo.get_by_id(result_id)
        if result_db is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found.")
        curve_set = self.curve_set_repo.get_by_id_for_user(result_db.curve_set_id, user_id)
        if curve_set is None:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")
        self.repo.delete(result_id)
        return True
