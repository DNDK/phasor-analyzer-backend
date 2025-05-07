from .base_repository import BaseRepository

from models.curve_set import CurveSet as CurveSetModel
from models.curve import Curve as CurveModel
from schemas import CurveSetCreate, CurveSet, Curve
from pydantic import BaseModel

class CurveSetRepository(BaseRepository[CurveSetModel]):
    def create_with_curves(self, data: CurveSetCreate) -> CurveSet:
    # Конвертируем Pydantic-модель в словарь
        data_dict = data.model_dump(exclude_unset=True)

        # Достаём кривые и удаляем их из словаря
        curves_data = data_dict.pop("curves", [])

        # Создаём CurveSet без кривых
        db_curve_set = self.model(**data_dict)
        self._session.add(db_curve_set)

        # Добавляем кривые через relationship
        for curve_data in curves_data:
            if isinstance(curve_data, BaseModel):
                curve_data = curve_data.model_dump()
            curve = CurveModel(**curve_data)  # Создаём CurveModel
            db_curve_set.curves.append(curve)

        self._session.commit()
        self._session.refresh(db_curve_set)
        return db_curve_set