from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Donation


class DonationCRUD(BaseCRUD):
    async def first_not_empty_donation(
            self,
            session: AsyncSession
    ):
        donations = await session.execute(
            select(Donation).where(Donation.fully_invested is False)
        )
        return donations.scalars().all()

    async def close_donation(
            self,
            donation: Donation,
    ):
        donation.invested_amount = donation.full_amount
        donation.fully_invested = True
        donation.close_date = datetime.now()
        return donation


donation_crud = DonationCRUD(Donation)
