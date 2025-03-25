from fastapi import APIRouter

from course_web_service.apps.auth_app.routes import auth_router

apps_router = APIRouter(prefix="/api/v1")

apps_router.include_router(router=auth_router)
