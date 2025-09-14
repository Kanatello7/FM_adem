from fastapi import FastAPI, HTTPException, Depends
from enum import Enum
from dependencies import get_adem_service
from service import AdemService
import uvicorn
from typing import Annotated

class ReportType(str, Enum):
    REPORT_19_33_1 = "19_33_1"
    REPORT_3_22 = "3_22"
    REPORT_19_20 = "19_20"
    REPORT_7_40 = "7_40"
    BPARTNER_V = "bpartner_v"
    
app = FastAPI()
AdemServiceDep = Annotated[AdemService, Depends(get_adem_service)]

@app.get("/import/{report_type}")
async def import_invoice(report_type: ReportType, service: AdemServiceDep):
    try:
        result = await service.import_report(report_type.value)
        return {"res": result}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

if __name__ == '__main__':
    uvicorn.run("main:app", port=8003)