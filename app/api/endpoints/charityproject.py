from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_project_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.models import CharityProject
from app.schemas.charityproject import CharityProjectCreate, CharityProjectDB
from app.services.money_process import money_process

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
    charity_project_new = await charity_crud.create(charity_project, session)
    await money_process(session)
    await session.refresh(charity_project_new)
    return charity_project_new

