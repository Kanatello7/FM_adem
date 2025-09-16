from celery import Celery 
import os 
from dependencies import get_adem_service_for_celery
import asyncio

backend_url = os.getenv("BACKEND_URL")
broker_url = os.getenv("BROKER_URL")
app = Celery(
    'adem_tasks',
    broker=broker_url,
    backend=backend_url 
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)

@app.task(name="imports.run_report")
def import_report(report_type: str):
    async def run():
        async for service in get_adem_service_for_celery():
            return await service.import_report(report_type)
            
    return asyncio.run(run())