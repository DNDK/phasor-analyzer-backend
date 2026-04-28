from sqlalchemy import select
from pydantic import BaseModel

from models.curve_set import CurveSet as CurveSetModel
from models.curve import Curve as CurveModel
from schemas.curve_set import CurveSetCreate
from .base_repository import BaseRepository


class CurveSetRepository(BaseRepository[CurveSetModel]):

    def get_all_for_user(self, user_id: int) -> list[CurveSetModel]:
        """Return all curve sets owned by *user_id*."""
        stmt = select(self.model).where(self.model.user_id == user_id)
        return list(self._session.execute(stmt).scalars().all())

    def get_by_id_for_user(self, curve_set_id: int, user_id: int) -> CurveSetModel | None:
        """Return a curve set only if it belongs to *user_id*."""
        stmt = (
            select(self.model)
            .where(self.model.id == curve_set_id)
            .where(self.model.user_id == user_id)
        )
        return self._session.execute(stmt).scalar_one_or_none()

    def create_with_curves(self, data: CurveSetCreate, user_id: int) -> CurveSetModel:
        """Create a CurveSet with its child Curve rows in a single transaction."""
        data_dict = data.model_dump(exclude_unset=True)
        curves_data = data_dict.pop("curves", [])

        db_curve_set = self.model(**data_dict, user_id=user_id)
        self._session.add(db_curve_set)

        for curve_data in curves_data:
            if isinstance(curve_data, BaseModel):
                curve_data = curve_data.model_dump()
            curve = CurveModel(**curve_data)
            db_curve_set.curves.append(curve)

        self._session.commit()
        self._session.refresh(db_curve_set)
        return db_curve_set