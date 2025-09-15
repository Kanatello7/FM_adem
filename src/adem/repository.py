from sqlalchemy import text, update, select
from sqlalchemy.ext.asyncio import AsyncSession 
import json
import os
from typing import Optional

class AdemRepository():
    def __init__(self, session: AsyncSession):
        self.session = session
        self.config = self.load_config()
    
    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), "query_config.json")
        with open(config_path) as f:
            return json.load(f)
    
    async def execute_query(self, query: str, params: Optional[dict] = None):
        if params:
            res = await self.session.execute(text(query), params) 
        else:
            res = await self.session.execute(text(query))
        return res.mappings().all()
    
    async def get_report_19_33_1(self):
        allowed_dcodes = self.config["report_19_33_1"]['dcodes']
        dcode_placeholders = ','.join([f':dcode_{i}' for i in range(len(allowed_dcodes))])
        query = f"""
            SELECT
                inv_documentno,
                inv_date,
                invoicename2,
                dateinvoiced2,
                c_activity,
                uvalue,
                utverditel,
                bpcompany,
                inv_bpartner,
                invline_product,
                icname,
                bin,
                invoicecreator,
                chname,
                doc_number,
                iik,
                agreement,
                totallines,
                payamt1c,
                payamtwithrefund1c,
                bank,
                typeinvcategory,
                i_docstatus,
                dcode,
                doc_number as document_number,
                docdate as document_date,
                amount,
                iso_code
            FROM adempiere.report_19_33_1_v
            WHERE i_ispaid = :i_ispaid AND dcode IN ({dcode_placeholders})
        """
        params = {"i_ispaid": self.config["report_19_33_1"]["i_ispaid"]}
        for i, dcode in enumerate(allowed_dcodes):
            params[f"dcode_{i}"] = dcode
        
        return await self.execute_query(query, params)

    async def get_report_3_22(self):
        query = """
            SELECT
                bpartner,
                bin
            FROM adempiere.blacklist_v;
            """
        return await self.execute_query(query)
    
    async def get_report_19_20(self):
        # doc_status
        query = """
            SELECT
                documentno,
                docstatus 
            FROM adempiere.report_19_20_v
            """
            
        return await self.execute_query(query)
    
    async def get_report_7_40(self):
        query = """
            SELECT
                odocumentno,
                region
            FROM adempiere.report_7_40_v
        """
        return await self.execute_query(query)
    
    async def get_report_bpartner_v(self):
        query = """
            SELECT 
                name,
                bin,
                iik 
            FROM adempiere.bpartner_v
        """
        return await self.execute_query(query)
    
        