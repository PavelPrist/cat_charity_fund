from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_project_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.schemas.charityproject import CharityProjectCreate, CharityProjectDB
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
