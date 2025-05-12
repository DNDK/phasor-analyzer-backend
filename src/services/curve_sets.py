from repositories.curve_set import CurveSetRepository
from repositories.curve import CurveRepository
from schemas.curve_set import CurveSetCreate, CurveSet, CurveSetPatch
from schemas.curve import Curve, CurveCreate
from schemas.generation_config import CurveConfig, IrfConfig, CurveSetConfig

from computing.curve import CurveGenerator


class CurveSetsService:
    def __init__(self, curve_set_repo: CurveSetRepository, curve_repo: CurveRepository):
        self.curveset_repo = curve_set_repo
        self.curve_repo = curve_repo

    def get_curve_set(self, id):
        cset = self.curveset_repo.get_by_id(id)
        return cset

    def create_curve_set(self, data: CurveSetCreate):
        return self.curveset_repo.create(data)

    def generate_curve(self, config: CurveConfig):
        curve_generator = CurveGenerator(config)
        data = curve_generator.get_data()
        return data

    def generate_curve_set(self, generation_config: CurveSetConfig) -> CurveSet: 
        # TODO: create conf schema
        print('generate')
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

        curves = [self.generate_curve(curve_conf) for curve_conf in curve_confs]

        curve_set = CurveSetCreate(
            description='Sample',
            curves=curves
            )

        curve_set_db = self.curveset_repo.create_with_curves(curve_set, generation_config.task_id)
        curve_set_serialized = CurveSet.model_validate(curve_set_db, from_attributes=True)
        return curve_set_serialized

    def add_curve_to_set(self, curve: CurveCreate):
        """ 
        Does literally nothing. Nothing at all. Like, it has only `pass` inside
        """
        pass

    def update_curve_set(self, id: int, data: CurveSetPatch) -> CurveSet:
        set_db = self.curveset_repo.update(id, data)
        curveset = CurveSet.model_validate(set_db, from_attributes=True)
        return curveset

    def delete_curve_set(self, id: int):
        try:
            self.curveset_repo.delete(id)
            return True
        except:
            return False
    # maybe more functions