from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation


async def first_project_for_investments(
        self,
        donation: Donation,
        session: AsyncSession,
):
    """
    Поиск первого подходящего проекта для инвестиции согласно FIFO
    """
    remain_for_project = (
            CharityProject.full_amount - CharityProject.invested_amount
    )
    charity_projects = await session.execute(
        select(CharityProject).where(
            remain_for_project >= donation.full_amount
        )
    )
    return remain_for_project, charity_projects.scalars().first_or_none()


async def update_project(charity_project, donation_add ):
    """
    Обновление полей проекта после прихода пожертвования
    """
    charity_project.invested_amount += donation_add

    if charity_project.invested_amount == charity_project.full_amount:
        charity_project.invested_amount = charity_project.full_amount
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()
    return charity_project


async def update_donation_and_project(donation, charity_project, remain_prj):
    """
    Обновление полей пожертвования(donation) + обновление проекта
    """
    if donation.full_amount >= remain_prj:
        donation.invested_amount = remain_prj
        charity_project = await update_project(charity_project, remain_prj)
    else:
        donation.invested_amount = donation.full_amount
        donation.fully_invested = True
        donation.close_date = datetime.now()
        charity_project = await update_project(
            charity_project, donation.full_amount
        )
    return donation, charity_project



async def donation_distribution(
        donation: Donation,
        session: AsyncSession,
):
    """
    Распределение пожертвований по проектам
    """

    while True:
        remain_prj, charity_project = await first_project_for_investments(
            donation=donation, session=session
        )
        if charity_project and donation.fully_invested != True:
            donation, charity_project = await update_donation_and_project(
                donation, charity_project, remain_prj
            )
        else:
            break
    session.add(donation)
    session.add(charity_project)
    return donation, charity_project, session


async def commit_refresh_db(
    charity_project,
    donation,
    session: AsyncSession
):
    """
    Обновление базы данных(donation, charity_project)
    """
    await session.commit()
    await session.refresh(donation)
    await session.refresh(charity_project)
    return charity_project, donation