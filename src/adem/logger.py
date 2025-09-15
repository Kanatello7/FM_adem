import os, json
from loguru import logger

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
    if record["exception"]:
        exc = record["exception"]
        log_entry["exception"] = {
            "type": exc.type.__name__ if exc.type else None,
            "message": str(exc.value) if exc.value else None,
            "traceback": str(exc.info) if exc.info else None,
        }
    record["message"] = json.dumps(log_entry, ensure_ascii=False)

logger.remove()

base = logger.bind(
    service="adem-service",
)

logger = base.patch(to_json_message)

logger.add(
    "logs/log.jsonl",
    format="{message}",   
    enqueue=True,           
    rotation="100 MB",
    retention="30 days",
    compression="zip",
    backtrace=True,
    diagnose=True,
)