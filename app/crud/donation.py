from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Donation


class DonationCRUD(BaseCRUD):
    pass

donation_crud = DonationCRUD(Donation)
