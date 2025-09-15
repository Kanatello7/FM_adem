from repository import AdemRepository
import typing

class AdemService():
    def __init__(self, repo: AdemRepository):
        self.repo = repo 
        self.processors = {
            "19_33_1": self.import_19_33_1,
            "3_22": self.import_3_22,
            "19_20": self.import_19_20,
            "7_40": self.import_7_40,
            "bpartner_v": self.import_bpartner_v,
        }
    async def import_report(self, report_type: str):
        if report_type not in self.processors:
            raise ValueError(f"Report type {report_type} not supported")

        return await self.processors[report_type]()
    
    async def import_19_33_1(self) -> list[dict[str, typing.Any]]:
        rows = await self.repo.get_report_19_33_1()
        result = []
        for row in rows:
            result.append(
                {
                    "supporting_document": row.get("inv_documentno"),
                    "supporting_document_date": row.get("inv_date"),
                    "invoice_number": row.get("invoicename2"),
                    "invoice_date": row.get("dateinvoiced2"),
                    "project": row.get("c_activity"),
                    "responsible": row.get("uvalue"),
                    "approver": row.get("utverditel"),
                    "llc": row.get("bpcompany"),
                    "counterparty": row.get("inv_bpartner"),
                    "comment": row.get("invline_product"),
                    "invoice_category": row.get("icname"),
                    "bin_or_iin": row.get(
                        "bin"
                    ),  # Здесь возможно нужно уточнить источник bin
                    "invoice_creator": row.get("invoicecreator"),
                    "income_expense_item": row.get("chname"),
                    "sales_orders": row.get("doc_number"),
                    "iic": row.get("iik"),
                    "agreement": row.get("agreement"),
                    "invoice_amount": row.get("totallines"),
                    "previously_paid_amount": row.get("payamtwithrefund1c"),
                    "bank": row.get("bank"),
                    "invoice_type": row.get("typeinvcategory"),
                    "subdivision": row.get("dcode"),
                    "document_number": row.get("document_number"),
                    "document_date": row.get("document_date"),
                    "status": row.get("i_docstatus"),
                    "closing_document_provided_amount": row.get("amount"),
                    "currency": row.get("iso_code"),
                }
            )
        return result

    async def import_3_22(self):
        rows = await self.repo.get_report_3_22()
        result = []
        for row in rows:
            result.append(
                {
                    "name": row.get("bpartner"),
                    "bin_or_iin": row.get("bin"),
                }
            )
        return result
        #output = f"Записи чёрного списка посажены успешно: {len(result)}"
        #try:
        #    await self.repo.update_CounterParty(result)
        #except Exception as e:
        #    output = f"Ошибка, записи не были посажены: {e}"
        #return output
        
    async def import_19_20(self):
        rows = await self.repo.get_report_19_20()
        result = []
        for row in rows:
            result.append(
                {
                    "number": row.get("documentno"),
                    "status": row.get("docstatus"),
                }
            )
        return result

    async def import_7_40(self):
        rows = await self.repo.get_report_7_40()
        result = []
        for row in rows:
            result.append(
                {
                    "number": row.get("odocumentno"),
                    "region": row.get("region"),
                }
            )
        return result
    
    async def import_bpartner_v(self):
        rows = await self.repo.get_report_bpartner_v()
        result = []
        for row in rows:
            result.append(
                {
                    "name": row.get("name"),
                    "bin_or_iin": row.get("bin"),
                    "iic": row.get("iik")
                }
            )
        return result