from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charityproject import charity_crud
from app.models import CharityProject


async def check_project_name_duplicate(
        name: str, session: AsyncSession
) -> None:
    project_id = await charity_crud.get_project_id_by_name(name, session)
    if project_id:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Проект с таким именем уже существует!",
        )


def charity_project_can_be_delete(
        charity_project
) -> None:
    if charity_project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='В проект были внесены средства, не подлежит удалению!',
        )


def charity_project_is_closed(
        charity_project
):
    if charity_project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Закрытый проект нельзя редактировать!',
        )


async def charity_project_exists(
        project_id: int,
        session: AsyncSession
) -> CharityProject:
    charity_project = await charity_crud.get(project_id, session)
    if not charity_project:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail=f'Проект с id {project_id} не найден',
        )
    return charity_project


async def before_edit_charity_project(
        project_id: int,
        obj_new: CharityProject,
        session: AsyncSession
):
    charity_project = await charity_project_exists(project_id, session)
    charity_project_is_closed(charity_project)
    if obj_new.name:
        await check_project_name_duplicate(obj_new.name, session)
    if obj_new.full_amount:
        project_full_amount_not_less_than_invested(
            charity_project,
            obj_new,
        )
    return charity_project


def project_full_amount_not_less_than_invested(
        charity_project,
        obj_in,
):
    if obj_in.full_amount < charity_project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
            detail=f'Невозможно задать требуемую сумму меньше уже вложенной'
                   f' {charity_project.invested_amount}',
        )
