from celery import Celery 
import os 
from dependencies import get_adem_service_for_celery
import asyncio

backend_url = os.getenv("BACKEND_URL")
broker_url = os.getenv("BROKER_URL")
app = Celery(
    'adem_tasks',
    broker=backend_url,
    backend=backend_url 
)

app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

def get_task_processor(report_type: str):
    processors = {
            "19_33_1": import_19_33_1,
            "3_22": import_3_22,
            "19_20": import_19_20,
            "7_40": import_7_40,
            "bpartner_v": import_bpartner_v,
    }
    
    if report_type not in processors:
        raise ValueError(f"Report type {report_type} not supported")

    return processors[report_type]

@app.task
def import_19_33_1():
    async def run():
        async for service in get_adem_service_for_celery():
            result = await service.import_19_33_1()  
            return result
    return asyncio.run(run())

@app.task
def import_3_22():
    async def run():
        async for service in get_adem_service_for_celery():
            result = await service.import_19_33_1()  
            return result
    return asyncio.run(run())

@app.task
def import_19_20():
    async def run():
        async for service in get_adem_service_for_celery():
            result = await service.import_19_33_1()  
            return result
    return asyncio.run(run())

@app.task
def import_7_40():
    async def run():
        async for service in get_adem_service_for_celery():
            result = await service.import_19_33_1()  
            return result
    return asyncio.run(run())

@app.task
def import_bpartner_v():
    async def run():
        async for service in get_adem_service_for_celery():
            result = await service.import_19_33_1()  
            return result
    return asyncio.run(run())