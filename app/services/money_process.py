from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CharityProject, Donation
from app.services.readDB import not_empty_obj, update_obj


def update_project_and_donation(
        donation,
        charity_project
):
    """
    Функция обновления объектов при распределении пожертвований
    """
    remain_prj = (
            charity_project.full_amount -
            charity_project.invested_amount)
    remain_don = donation.full_amount - donation.invested_amount

    charity_project = update_obj(
        charity_project, remain_don
    )
    donation = update_obj(
        donation, remain_prj
    )
    return donation, charity_project


async def investing_process(
        session: AsyncSession
):
    """
    Распределение пожертвований по проектам
    """
    donations = await not_empty_obj(Donation, session)
    charity_projects = await not_empty_obj(CharityProject, session)

    for donation in donations:
        for charity_project in charity_projects:

            donation, charity_project = update_project_and_donation(
                donation, charity_project
            )
            session.add(donation)
            session.add(charity_project)
    return session
