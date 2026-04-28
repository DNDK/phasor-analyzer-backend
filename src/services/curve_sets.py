from fastapi import HTTPException, status

from repositories.curve_set import CurveSetRepository
from repositories.curve import CurveRepository
from schemas.curve_set import CurveSet, CurveSetCreate, CurveSetPatch, CurveSetSummary
from schemas.curve import CurveCreate
from schemas.uploaded_curve_set import UploadedCurveSet
from schemas.generation_config import CurveConfig, CurveSetConfig

from computing.curve import CurveGenerator


class CurveSetsService:
    def __init__(self, curve_set_repo: CurveSetRepository, curve_repo: CurveRepository):
        self.curveset_repo = curve_set_repo
        self.curve_repo = curve_repo

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_all_for_user(self, user_id: int) -> list[CurveSetSummary]:
        """Return all curve sets belonging to *user_id* (no curve arrays)."""
        curve_sets = self.curveset_repo.get_all_for_user(user_id)
        return [CurveSetSummary.model_validate(cs, from_attributes=True) for cs in curve_sets]

    def get_curve_set(self, curve_set_id: int, user_id: int) -> CurveSet:
        """Return a single curve set that belongs to *user_id*."""
        cset = self.curveset_repo.get_by_id_for_user(curve_set_id, user_id)
        if cset is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curve set not found.")
        return CurveSet.model_validate(cset, from_attributes=True)

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def create_curve_set(self, data: CurveSetCreate, user_id: int) -> CurveSet:
        curve_set_db = self.curveset_repo.create_with_curves(data, user_id)
        return CurveSet.model_validate(curve_set_db, from_attributes=True)

    def generate_curve(self, config: CurveConfig):
        curve_generator = CurveGenerator(config)
        return curve_generator.get_data()

    def generate_curve_set(self, generation_config: CurveSetConfig, user_id: int) -> CurveSet:
        curve_confs = [
            CurveConfig(
                a1=a1,
                irf_config=generation_config.irf_config,
                tau1=generation_config.tau1,
                tau2=generation_config.tau2,
                dt=generation_config.dt,
                num_points=generation_config.num_points,
                apply_convolution=generation_config.apply_convolution,
                add_noise=generation_config.add_noise,
                strg=generation_config.strg,
            )
            for a1 in generation_config.a1_coeffs
        ]

        curves = [self.generate_curve(conf) for conf in curve_confs]

        curve_set = CurveSetCreate(
            title=generation_config.title,
            description="Generated curve set",
            curves=curves,
        )

        curve_set_db = self.curveset_repo.create_with_curves(curve_set, user_id)
        return CurveSet.model_validate(curve_set_db, from_attributes=True)

    def create_curve_set_from_uploaded(self, uploaded: UploadedCurveSet, user_id: int) -> CurveSet:
        """Build CurveCreate objects from raw arrays and a shared IRF."""
        if not uploaded.irf:
            raise ValueError("irf must be provided for uploaded curve sets")

        irf = uploaded.irf
        curves: list[CurveCreate] = []
        for curve in uploaded.curves:
            length = min(len(curve.time_axis), len(curve.intensity), len(irf))
            raw = curve.intensity[:length]
            curves.append(
                CurveCreate(
                    time_axis=curve.time_axis[:length],
                    raw=raw,
                    raw_scaled=raw,
                    convolved=None,
                    noisy=None,
                    irf=irf[:length],
                    irf_scaled=None,
                )
            )

        curve_set = CurveSetCreate(
            title=uploaded.title,
            description=uploaded.description,
            curves=curves,
        )
        curve_set_db = self.curveset_repo.create_with_curves(curve_set, user_id)
        return CurveSet.model_validate(curve_set_db, from_attributes=True)

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------

    def update_curve_set(self, curve_set_id: int, data: CurveSetPatch, user_id: int) -> CurveSet:
        # Verify ownership before mutating
        existing = self.curveset_repo.get_by_id_for_user(curve_set_id, user_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curve set not found.")
        set_db = self.curveset_repo.update(curve_set_id, data)
        return CurveSet.model_validate(set_db, from_attributes=True)

    def delete_curve_set(self, curve_set_id: int, user_id: int) -> bool:
        existing = self.curveset_repo.get_by_id_for_user(curve_set_id, user_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Curve set not found.")
        self.curveset_repo.delete(curve_set_id)
        return True
