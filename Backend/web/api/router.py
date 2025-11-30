from fastapi.routing import APIRouter

from Backend.web.api import docs, dummy, echo, monitoring, redis, users, esp32

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(users.router)
api_router.include_router(docs.router)
api_router.include_router(echo.router, prefix="/echo", tags=["echo"])
api_router.include_router(esp32.router, prefix="/sensor", tags=["sensor"])
api_router.include_router(dummy.router, prefix="/dummy", tags=["dummy"])
api_router.include_router(redis.router, prefix="/redis", tags=["redis"])
