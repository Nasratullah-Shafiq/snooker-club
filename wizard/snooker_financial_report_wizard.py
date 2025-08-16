"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-18 10:21:47
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 11:55:39
FilePath: customization/snooker_reservation/wizard/snooker_financial_report_wizard.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
# from odoo import models, fields
# import xlsxwriter
# import base64
# from io import BytesIO

class SnookerFinancialReportWizard(models.TransientModel):
    _name = "snooker.financial.report.wizard"
    _description = "Generate Financial Report"

    report_file = fields.Binary("Download Report", readonly=True)
    report_name = fields.Char("File Name", default="financial_report.xlsx")

    # def generate_report(self):
    #     data = self.env["snooker.financial.report"].create({})
    #
    #     output = BytesIO()
    #     workbook = xlsxwriter.Workbook(output)
    #     sheet = workbook.add_worksheet("Financial Report")
    #
    #     # Define headers
    #     headers = ["Report Date", "Total Revenue", "Total Expense", "Net Profit"]
    #     for col, header in enumerate(headers):
    #         sheet.write(0, col, header)
    #
    #     # Write data
    #     sheet.write(1, 0, str(data.report_date))
    #     sheet.write(1, 1, data.total_revenue)
    #     sheet.write(1, 2, data.total_expense)
    #     sheet.write(1, 3, data.net_profit)
    #
    #     workbook.close()
    #     output.seek(0)
    #     report_data = base64.b64encode(output.read())
    #
    #     self.write({"report_file": report_data})
    #     return {
    #         "type": "ir.actions.act_window",
    #         "res_model": "snooker.financial.report.wizard",
    #         "view_mode": "form",
    #         "res_id": self.id,
    #         "target": "new",
    #     }
