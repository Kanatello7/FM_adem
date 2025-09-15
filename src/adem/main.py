from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
import uvicorn

from dependencies import get_adem_service
from service import AdemService
from logger import logger, request_id_var
from celery_config import app as celery_app, get_task_processor

from typing import Annotated
import time
from enum import Enum


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
    token = request_id_var.set(request_id)
    logger_with_context = logger.bind(request_id=request_id)
    logger_with_context.info(
        "Request started",
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
        if 200 <= status_code < 300:
            logger_with_context.info(
                "Request completed successfully",
                status_code=status_code,
                duration_ms=duration_ms
            )
        else:
            logger_with_context.error(
                "Request failed with non-success status",
                status_code=status_code,
                duration_ms=duration_ms
            )
    except Exception as e:
        duration_ms = round((time.perf_counter() - start_time) * 1000.0, 2)
        logger_with_context.exception(
            "Request failed with unexpected exception",
            duration_ms=duration_ms,
            exception_type=type(e).__name__
        )
        response = JSONResponse(
            status_code=500,
            content={"detail": "Internal server error", "request_id": request_id}
        )
    finally:
        request_id_var.reset(token)
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
        logger.warning(f"Import task failed with ValueError: {str(e)}", report_type = report_type.value)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(
            f"Import task failed: {str(e)}",
            extra={"report_type": report_type.value}
        )
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
    logger.info("root route")
    return {"result": "ok"}

if __name__ == '__main__':
    logger.info("Starting FastAPI application", port=8003)
    uvicorn.run("main:app", port=8003, reload=True)