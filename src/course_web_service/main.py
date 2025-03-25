import logging

import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from course_web_service.apps import apps_router
from course_web_service.core.core_dependecy.db_dependency import DBDependency
from course_web_service.database.initial_data.initial_data import InitialDataLoader
from course_web_service.utils.logger import AppLogger, LoggerConfig

app_logger = AppLogger(config=LoggerConfig())
app_logger.setup()

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения."""
    db = DBDependency()
    try:
        async with db.db_session() as session:
            await InitialDataLoader().load_all(session)
            logger.info("Initial data loaded")

        yield

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    finally:
        await db.close()
        logger.info("Shutdown complete")


app = FastAPI(lifespan=lifespan)
app.include_router(router=apps_router)


def start():
    """Запускает сервер с настройками из конфигурации."""
    uvicorn.run(
        app="course_web_service.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_config=None,
    )
