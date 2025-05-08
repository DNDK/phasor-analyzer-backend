from typing import Union

from fastapi import FastAPI

from routers import tasks

from routers.curve_sets import curve_sets_router
from routers.tasks import tasks_router
from routers.analysis import analysis_router

app = FastAPI()


app.include_router(curve_sets_router, prefix='/curves')
app.include_router(tasks_router, prefix='/tasks')
app.include_router(analysis_router, prefix='/analysis')