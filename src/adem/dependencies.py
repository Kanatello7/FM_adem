from fastapi import Depends
from service import AdemService
from repository import AdemRepository
from db import get_session, AsyncSession, get_session_for_celery
from typing import Annotated

async def get_repository(session: Annotated[AsyncSession, Depends(get_session)]):
    return AdemRepository(session)
    

async def get_adem_service(repository: Annotated[AdemRepository, Depends(get_repository)]):
    return AdemService(repository)
 
async def get_adem_service_for_celery():
    async for session in get_session_for_celery():
        repo = AdemRepository(session)
        yield AdemService(repo)