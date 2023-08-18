from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Donation, User


class DonationCRUD(BaseCRUD):
    async def get_by_user_donations(
        self,
        user: User,
        session: AsyncSession
    ) -> list[Donation]:
        donation = await session.execute(
            select(Donation).where(
                Donation.user_id == user.id
            )
        )
        return donation.scalars().all()


donation_crud = DonationCRUD(Donation)
