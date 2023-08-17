from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    before_edit_charity_project, charity_project_can_be_delete,
    charity_project_exists,
    charity_project_is_closed, check_project_name_duplicate
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.schemas.charityproject import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate
)
from app.services.money_process import investing_process
from app.services.readDB import commit_refresh_db

router = APIRouter()


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
        charity_project: CharityProjectCreate,
        session: AsyncSession = Depends(get_async_session),
) -> CharityProjectDB:
    await check_project_name_duplicate(charity_project.name, session)
    charity_project = await charity_crud.create(charity_project, session)
    session = await investing_process(session)
    await commit_refresh_db(session, charity_project)
    return charity_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True
)
async def get_charity_projects(
        session: AsyncSession = Depends(get_async_session)
) -> list[CharityProjectDB]:
    charity_projects = await charity_crud.get_multi(session)
    return charity_projects


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def delete_charity_project(
        project_id: int,
        session: AsyncSession = Depends(get_async_session)
) -> CharityProjectDB:
    charity_project = await charity_project_exists(
        project_id,
        session)
    charity_project_can_be_delete(charity_project)
    charity_project_is_closed(charity_project)
    charity_project = await charity_crud.delete(charity_project, session)
    return charity_project


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    dependencies=[Depends(current_superuser)]
)
async def update_charity_project(
    project_id: int,
    obj_in: CharityProjectUpdate,
    session: AsyncSession = Depends(get_async_session)
) -> CharityProjectDB:
    charity_project = await before_edit_charity_project(
        project_id, obj_in, session
    )
    charity_project = await charity_crud.update(
        charity_project, obj_in, session
    )
    return charity_project
