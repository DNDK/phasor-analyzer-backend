from typing import Union

from fastapi import FastAPI

from routers import tasks

app = FastAPI()


app.include_router(tasks.router, prefix='/tasks')