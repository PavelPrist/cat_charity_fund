from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def not_empty_donations(session: AsyncSession):
    donations = await session.execute(
        select(Donation).where(Donation.fully_invested.is_(False))
    )
    return donations.scalars().all()


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


def close_project(charity_project: CharityProject):
    charity_project.invested_amount = charity_project.full_amount
    charity_project.fully_invested = True
    charity_project.close_date = datetime.now()
    return charity_project


def close_donation(donation: Donation):
    donation.invested_amount = donation.full_amount
    donation.fully_invested = True
    donation.close_date = datetime.now()
    return donation


async def commit_refresh_db(
        session: AsyncSession,
        charity_project: CharityProject = None,
        donation: Donation = None
):
    """
    Обновление базы данных(donation, charity_project)
    """

    await session.commit()
    if charity_project:
        await session.refresh(charity_project)
    if donation:
        await session.refresh(donation)
    return charity_project, donation
