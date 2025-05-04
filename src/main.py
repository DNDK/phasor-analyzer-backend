from typing import Union

from fastapi import FastAPI

from routers import tasks

from routers.curve_sets import curve_sets_router

app = FastAPI()


app.include_router(curve_sets_router, prefix='/curves')

