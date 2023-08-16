from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.services.readDB import (
    close_donation,
    close_project,
    first_project_for_investments,
    not_empty_donations
)


def update_project(charity_project, donation_add):
    """
    Обновление полей проекта после прихода пожертвования
    """
    charity_project.invested_amount += donation_add

    if charity_project.invested_amount >= charity_project.full_amount:
        charity_project = close_project(charity_project)
    return charity_project


def update_donation_and_project(
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
        charity_project = update_project(charity_project, remain_prj)
        if donation.invested_amount == donation.full_amount:
            donation = close_donation(donation)
    elif (
            remain_donation <= charity_project.full_amount
            and remain_donation != 0
    ):
        charity_project = update_project(
            charity_project, remain_donation
        )
        donation = close_donation(donation)
    elif (
            remain_donation >= charity_project.full_amount
            and remain_donation != 0
    ):
        charity_project = update_project(
            charity_project, remain_donation)
        donation.invested_amount += (
                remain_donation - charity_project.full_amount)
    else:
        donation = close_donation(donation)
        charity_project = update_project(
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
            first_project_for_investments(session=session)
        )
        if charity_project is not None and donation.fully_invested == False:
            donation, charity_project = update_donation_and_project(
                donation, charity_project
            )
        else:
            break
    session.add(donation)
    if charity_project:
        session.add(charity_project)
    return donation, charity_project, session


async def taking_donations(
        charity_project: CharityProject,
        session: AsyncSession
):
    """
    Получение пожертвований для проекта
    """
    donations = await not_empty_donations(session)
    for donation in donations:
        remain = donation.full_amount - donation.invested_amount

        donation, charity_project = update_donation_and_project(
            donation, charity_project, remain_donation=remain
        )
        session.add(donation)
        if charity_project.fully_invested is True:
            break

    session.add(charity_project)
    return charity_project, session
