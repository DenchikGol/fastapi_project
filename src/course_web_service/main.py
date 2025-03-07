import uvicorn
from fastapi import FastAPI

from course_web_service.apps import apps_router

app = FastAPI()

app.include_router(router=apps_router)


def start():
    uvicorn.run(app="course_web_service.main:app", reload=True)
