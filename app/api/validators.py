from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_crud


async def check_project_name_duplicate(
    name: str, session: AsyncSession
) -> None:
    project_id = await charity_crud.get_project_id_by_name(name, session)
    if project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=f'Имя проекта {name} уже занято',
        )
