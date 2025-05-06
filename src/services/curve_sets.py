from repositories.curve_set import CurveSetRepository
from schemas.curve_set import CurveSetCreate, CurveSet
from schemas.curve import Curve, CurveCreate
from schemas.generation_config import CurveConfig, IrfConfig

from computing.curve import CurveGenerator

class CurveSetsService:
	def __init__(self, curve_set_repo: CurveSetRepository):
		self.repo = curve_set_repo

	def get_curve_set(self, id):
		cset = self.repo.get_by_id(id)
		return cset

	async def create_curve_set(self, data: CurveSetCreate):
		await self.repo.create(data.model_dump())

	async def generate_curve_set(self, generation_config): 
		# TODO: create conf schema
		print('generate')

		

	async def add_curve_to_set(self, curve: CurveCreate):
		pass

	# maybe more functions