from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_crud
from app.crud.donation import donation_crud
from app.models import CharityProject, Donation


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
        remain_donation=0
):
    """
    Обновление полей пожертвования(donation) + обновление проекта
    """
    remain_prj = (
            charity_project.full_amount -
            charity_project.invested_amount)
    if donation.full_amount >= remain_prj and remain_prj != 0:
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
        charity_project = await (
            charity_crud.first_project_for_investments(
                donation=donation, session=session
            )
        )
        if charity_project and donation.fully_invested == 0:
            donation, charity_project = await update_donation_and_project(
                donation, charity_project
            )
        else:
            break
    session.add(donation)
    if charity_project:
        session.add(charity_project)
    return donation, charity_project, session


async def taking_donations(
        charity_project,
        session: AsyncSession
):
    """
    Получение пожертвований для проекта
    """
    donations = await donation_crud.not_empty_donations(
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
    return charity_project, session


async def commit_refresh_db(
        session: AsyncSession,
        charity_project: CharityProject,
        donation: Donation
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
