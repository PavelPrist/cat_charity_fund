from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import check_project_name_duplicate
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud.charityproject import charity_crud
from app.schemas.charityproject import CharityProjectCreate, CharityProjectDB
from app.services.money_process import commit_refresh_db, taking_donations

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
    charity_project_new, donation, session = await taking_donations(
        charity_project_new, session
    )
    charity_project_new, donation = await commit_refresh_db(
        donation, charity_project_new, session
    )
    return charity_project_new
