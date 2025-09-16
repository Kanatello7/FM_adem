from fastapi import FastAPI, HTTPException, Depends, Request, status
from fastapi.responses import JSONResponse
from schemas import TaskStatus

import uvicorn

from dependencies import get_adem_service
from service import AdemService
from logger import logger, request_id_var
from celery_config import app as celery_app, import_report

from typing import Annotated, Optional
import time
from enum import Enum
from math import ceil 


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
        query_params = str(request.query_params)
        
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
    response.headers['X_Process-Time'] = str(duration_ms) + "ms"
    return response

AdemServiceDep = Annotated[AdemService, Depends(get_adem_service)]

@app.post("/import/{report_type}", status_code=status.HTTP_202_ACCEPTED)
async def import_invoice(report_type: ReportType):
    logger.info(f"Starting import task for report type: {report_type.value}")
    try:
        task = import_report.delay(report_type.value)
        logger.info(f"Task queued for report type: {report_type.value}, task_id: {task.id}")
        return {"task_id": task.id, "status": "Task queued", "links": {"status": f"/task/{task.id}"},}
    except ValueError as e:
        logger.warning(f"Import task failed with ValueError: {str(e)}", report_type = report_type.value)
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.exception(
            f"Import task failed: {str(e)}",
            extra={"report_type": report_type.value}
        )
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/task/{task_id}", response_model=TaskStatus)
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    res = AsyncResult(task_id, app=celery_app)
    state = res.state

    if state == "PENDING":
        return {"task_id": task_id, "state": state, "status": "pending"}
    if state == "STARTED":
        return {
            "task_id": task_id, "state": state, "status": "running",
            "meta": res.info if isinstance(res.info, dict) else None,
        }
    if state == "SUCCESS":
        return {"task_id": task_id, "state": state, "status": "completed"}
    if state == "FAILURE":
        return {"task_id": task_id, "state": state, "status": "failed", "meta": {"error": str(res.info)}}
    return {"task_id": task_id, "state": state, "status": state.lower()}

@app.get("/task/{task_id}/result")
async def get_task_result(request: Request, task_id: str, paginate: bool = True, page: Optional[int] = None, page_size: int = 100):
    from celery.result import AsyncResult
    res = AsyncResult(task_id, app=celery_app)
    if res.state != "SUCCESS":
        raise HTTPException(409, f"Task not completed. Current state={res.state}")
    rows = res.result
    if not paginate:
        return rows
    
    total = len(rows)
    pages = max(1, ceil(total / page_size)) if total else 1

    if total == 0 and page > 1:
        raise HTTPException(status_code=404, detail="No results")
    if total > 0 and page > pages:
        raise HTTPException(status_code=404, detail=f"Page {page} out of range (pages={pages})")

    start = (page - 1) * page_size
    end = start + page_size
    page_items = rows[start:end]

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": pages,
        "items": page_items,
    }


@app.get("/")
def read_root():
    logger.info("root route")
    return {"result": "ok"}


if __name__ == '__main__':
    logger.info("Starting FastAPI application", port=8003)
    uvicorn.run("main:app", port=8003, reload=True)