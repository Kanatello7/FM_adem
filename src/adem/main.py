from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from enum import Enum
from dependencies import get_adem_service
from service import AdemService
import uvicorn
from typing import Annotated
import time
from logger import logger
from celery_config import app as celery_app, get_task_processor

class ReportType(str, Enum):
    REPORT_19_33_1 = "19_33_1"
    REPORT_3_22 = "3_22"
    REPORT_19_20 = "19_20"
    REPORT_7_40 = "7_40"
    BPARTNER_V = "bpartner_v"
    
app = FastAPI()

@app.middleware("http")
async def add_log(request: Request, call_next):
    import uuid 
    request_id = str(uuid.uuid4())[:8]
    logger.info(
        "Request started",
        request_id = request_id,
        method = request.method,
        path = request.url.path,
        
    )
    start_time = time.perf_counter()
    response = None 
    status_code = 500
    try:
        response = await call_next(request)
        status_code = response.status_code
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        logger.info(
            "Request completed successfully",
            
            request_id = request_id,
            status_code = status_code,
            duration_ms = duration_ms
            
        )
    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        logger.exception(
            "Request failed with exception",
            
            request_id = request_id,
            duration_ms = duration_ms,
            exception_type = type(e).__name__
            
        )

        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id}
        )
        status_code = 500
    return response

AdemServiceDep = Annotated[AdemService, Depends(get_adem_service)]

@app.get("/import/{report_type}")
async def import_invoice(report_type: ReportType):
    logger.info(f"Starting import task for report type: {report_type.value}")
    try:
        task_func = get_task_processor(report_type.value)
        task = task_func.delay()
        logger.info(f"Task queued for report type: {report_type.value}, task_id: {task.id}")
        return {"task_id": task.id, "status": "Task queued"}
    except ValueError as e:
        logger.warning(f"Import task failed with ValueError: {str(e)}", extra={"report_type": report_type.value})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(f"Import task failed: {str(e)}", extra={"report_type": report_type.value})
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/task/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    task_result = AsyncResult(task_id, app=celery_app)
    if task_result.state == 'PENDING':
        return {"task_id": task_id, "status": "Pending"}
    elif task_result.state == 'SUCCESS':
        return {"task_id": task_id, "status": "Completed", "result": task_result.get()}
    elif task_result.state == 'FAILURE':
        return {"task_id": task_id, "status": "Failed", "error": str(task_result.get(propagate=False))}
    else:
        return {"task_id": task_id, "status": task_result.state}

@app.get("/")
def read_root():
    return {"ok": True}

if __name__ == '__main__':
    logger.info("Starting FastAPI application", port=8003)
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=True)