from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import current_user
from app.crud.donation import donation_crud
from app.models import User
from app.schemas.donation import DonationCreate, DonationDb, DonationsDb
from app.services.money_process import (
    commit_refresh_db,
    donation_distribution
)

router = APIRouter()


@router.post(
    '/',
    dependencies=[Depends(current_user)],
    response_model=DonationDb,
    response_model_exclude_none=True
)
async def create_donation(
    donation: DonationCreate,
    session: AsyncSession = Depends(get_async_session),
    user: User = Depends(current_user),
):
    donation = await donation_crud.create(
        donation,
        session,
        user
    )
    donation_new, charity_project_new, session = await donation_distribution(
        donation, session
    )
    donation_end, _ = await commit_refresh_db(
        session, charity_project=charity_project_new, donation=donation_new
    )
    return donation_new
