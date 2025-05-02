from fastapi import APIRouter, Depends
from schemas import CurveSet, CurveSetCreate, Curve, CurveCreate

curves_router = APIRouter(prefix='/curves')

@router.post('/create')
def handle_create_curve_set(curve_set: CurveSetCreate):
	pass