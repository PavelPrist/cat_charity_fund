from datetime import datetime
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.models import CharityProject, Donation


class CharityProjectCRUD(BaseCRUD):
    async def get_project_id_by_name(
            self,
            prj_name: str,
            session: AsyncSession
    ) -> Optional[int]:
        project_id = await session.execute(
            select(CharityProject.id).where(
                prj_name == CharityProject.name
            )
        )
        return project_id.scalar_one_or_none()

    async def first_project_for_investments(
            self,
            donation: Donation,
            session: AsyncSession,
    ):
        """
        Поиск первого подходящего проекта для инвестиции согласно FIFO
        """
        remain_prj = (
                CharityProject.full_amount - CharityProject.invested_amount
        )
        charity_projects = await session.execute(
            select(CharityProject).where(
                remain_prj >= donation.full_amount
            )
        )
        return remain_prj, charity_projects.scalars().first_or_none()

    async def close_prject(self, charity_project: CharityProject):
        charity_project.invested_amount = charity_project.full_amount
        charity_project.fully_invested = True
        charity_project.close_date = datetime.now()
        return charity_project


charity_crud = CharityProjectCRUD(CharityProject)
