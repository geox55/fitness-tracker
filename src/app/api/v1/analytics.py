"""Analytics endpoints — agregaty для главного экрана."""

from fastapi import APIRouter

from ...domains.analytics.schemas import OverviewResponse
from ...domains.analytics.service import build_overview
from ..dependencies import CurrentUserDep, SessionDep

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=OverviewResponse)
async def overview(user: CurrentUserDep, session: SessionDep) -> OverviewResponse:
    return await build_overview(session, user_id=user.id)
