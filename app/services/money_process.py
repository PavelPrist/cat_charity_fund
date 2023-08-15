from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_crud
from app.crud.donation import donation_crud
from app.models import Donation


async def update_project(charity_project, donation_add):
    """
    Обновление полей проекта после прихода пожертвования
    """
    charity_project.invested_amount += donation_add

    if charity_project.invested_amount >= charity_project.full_amount:
        charity_project = await charity_crud.close_prject(charity_project)
    return charity_project


async def update_donation_and_project(
        donation,
        charity_project,
        remain_prj=0,
        remain_donation=0
):
    """
    Обновление полей пожертвования(donation) + обновление проекта
    """
    if donation.full_amount >= remain_prj != 0:
        donation.invested_amount = remain_prj
        charity_project = await update_project(charity_project, remain_prj)
    elif (
            remain_donation <= charity_project.full_amount
            and remain_donation != 0
    ):
        charity_project = await update_project(
            charity_project, remain_donation
        )
        donation = await donation_crud.close_donation(donation)
    elif (
            remain_donation >= charity_project.full_amount
            and remain_donation != 0
    ):
        charity_project = await update_project(
            charity_project, remain_donation)
        donation.invested_amount += (
                remain_donation - charity_project.full_amount)
    else:
        donation = await donation_crud.close_donation(donation)
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
        remain_prj, charity_project = await (
            charity_crud.first_project_for_investments(
                donation=donation, session=session
            )
        )
        if charity_project and donation.fully_invested is not True:
            donation, charity_project = await update_donation_and_project(
                donation, charity_project, remain_prj=remain_prj
            )
        else:
            break
    session.add(donation)
    session.add(charity_project)
    return donation, charity_project, session


async def taking_donations(
        charity_project,
        session: AsyncSession
):
    """
    Получение пожертвований для проекта
    """
    donations = await donation_crud.first_not_empty_donation(
        session=session
    )
    for donation in donations:
        remain = donation.full_amount - donation.invested_amount

        donation, charity_project = await update_donation_and_project(
            donation, charity_project, remain_donation=remain
        )
        session.add(donation)
        await session.commit()
        if charity_project.fully_invested is True:
            break
    session.add(charity_project)
    return charity_project, donation, session


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
