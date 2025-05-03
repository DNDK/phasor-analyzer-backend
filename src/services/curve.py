from repositories.curve import CurveRepository
from schemas import Curve, CurveCreate

class CurveService:
    def __init__(self, curve_repo: CurveRepository):
        self.repo = curve_repo

    async def get_curve(self, id):
        curve = await self.repo.get_by_id(id)

        curve_ser = Curve.model_validate(curve)
        return curve_ser

    async def create_curve(self, data: CurveCreate) -> Curve:
        crv = await self.repo.create(data=data.model_dump())
        return Curve.model_validate(crv)

