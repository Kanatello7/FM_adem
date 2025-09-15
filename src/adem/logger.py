import os
import json
import traceback
from loguru import logger
from contextvars import ContextVar

request_id_var = ContextVar("request_id", default=None)

def to_json_message(record):
    log_entry = {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"]
    }
    if request_id := request_id_var.get():
        log_entry["extra"]["request_id"] = request_id
    if record["exception"]:
        exc = record["exception"]
        exc_traceback = "".join(traceback.format_tb(exc.traceback)) if exc.traceback else None
        log_entry["exception"] = {
            "type": exc.type.__name__ if exc.type else None,
            "message": str(exc.value) if exc.value else None,
            "traceback": exc_traceback
        }
    record["message"] = json.dumps(log_entry, ensure_ascii=False)
    record["exception"] = None
logger.remove()

base = logger.bind(service="adem-service")

logger = base.patch(to_json_message)

logger.add(
    "logs/log.jsonl",
    format="{message}",
    enqueue=True,
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    backtrace=False,
    diagnose=False
)