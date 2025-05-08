from pydantic import BaseModel

class AnalysisConfig(BaseModel):
	task_id: int
	curve_set_id: int
	