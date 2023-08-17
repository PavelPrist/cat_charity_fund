from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def not_empty_donations(session: AsyncSession):
    donations = await session.execute(
        select(Donation).where(Donation.fully_invested.is_(False))
    )
    return donations.scalars().all()


async def not_empty_obj(model, session: AsyncSession):
    obj = await session.execute(
        select(model).where(model.fully_invested.is_(False))
    )
    return obj.scalars().all()


async def first_project_for_investments(session: AsyncSession):
    """
    Поиск первого подходящего проекта для инвестиции согласно FIFO
    """
    charity_projects = await session.execute(
        select(CharityProject).where(
            CharityProject.fully_invested.is_(False)
        )
    )
    return charity_projects.scalars().first()


def close_obj(obj):
    obj.invested_amount = obj.full_amount
    obj.fully_invested = True
    obj.close_date = datetime.now()
    return obj


def update_obj(obj, invested_add):
    obj.invested_amount += invested_add
    if obj.invested_amount >= obj.full_amount:
        obj = close_obj(obj)
    return obj


def commit_refresh_db(session: AsyncSession, obj):
    session.commit()
    session.refresh(obj)
