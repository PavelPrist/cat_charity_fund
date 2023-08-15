from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseCRUD
from app.models import CharityProject


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


charity_crud = CharityProjectCRUD(CharityProject)
