from fastapi import APIRouter

from birt_backend.features.health.schemas import HealthResponse

router = APIRouter()


@router.get("/api/v1/health")
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
