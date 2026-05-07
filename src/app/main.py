import logging

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .api.v1 import adaptation as adaptation_router
from .api.v1 import analytics as analytics_router
from .api.v1 import auth as auth_router
from .api.v1 import catalog as catalog_router
from .api.v1 import forecast as forecast_router
from .api.v1 import inbody as inbody_router
from .api.v1 import profile as profile_router
from .api.v1 import workouts as workouts_router
from .config import get_settings

_log = logging.getLogger("app")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="Фитнес-трекер API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(Exception)
    async def _on_unhandled(_request: Request, exc: Exception) -> JSONResponse:
        # Без обработчика стек упадёт мимо CORSMiddleware, и браузер увидит
        # CORS-ошибку вместо 500. JSONResponse идёт через middleware-стек.
        _log.exception("unhandled exception", exc_info=exc)
        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_error",
                "message": "Внутренняя ошибка сервера",
            },
        )

    v1 = APIRouter(prefix=settings.api_v1_prefix)
    v1.include_router(auth_router.router)
    v1.include_router(profile_router.router)
    v1.include_router(adaptation_router.router)
    v1.include_router(analytics_router.router)
    v1.include_router(catalog_router.router)
    v1.include_router(forecast_router.router)
    v1.include_router(inbody_router.router)
    v1.include_router(workouts_router.router)

    @v1.get("/health", tags=["meta"])
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(v1)
    return app


app = create_app()
