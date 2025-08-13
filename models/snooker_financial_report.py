"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 15:06:10
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 21:57:07
FilePath: customization/snooker_reservation/models/snooker_financial_report.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
        
from odoo import models, fields, api
from datetime import datetime


class SnookerFinancialReport(models.Model):
    _name = "snooker.financial.report"
    _description = "Snooker Financial Report"
    _auto = False  # Prevents automatic table creation, as this is a database view
    _log_access = False  # Prevents Odoo from trying to track create/write timestamps
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance


    name = fields.Char("Month-Year", required=True)
    total_collected = fields.Float("Total Revenue Collected")
    total_expenses = fields.Float("Total Expenses Paid")
    salary_expense = fields.Float("Salary Expense")  
    rent_expense = fields.Float("Rent Expense")  
    electricity_expense = fields.Float("Electricity Expense")  
    maintenance_expense = fields.Float("Maintenance Expense")  
    equipment_expense = fields.Float("Equipment Expense")  # ✅ FIX: Ensure this field exists
    net_balance = fields.Float("Net Balance (Revenue - Expenses)")
    total_revenue = fields.Float("Total Revenue", compute="_compute_financials", store=True)
    report_date = fields.Date("Report Date", default=fields.Date.today)

    @api.depends()
    def _compute_financials(self):
        today = datetime.date.today()
        start_date = today.replace(day=1)

        revenue = self.env["snooker.reservation"].search([("start_time", ">=", start_date)])
        total_revenue = sum(revenue.mapped("total_cost"))

        expenses = self.env["snooker.expense"].search([("date", ">=", start_date)])
        total_expenses = sum(expenses.mapped("amount"))

        for record in self:
            record.total_revenue = total_revenue
            record.total_expenses = total_expenses
            record.net_balance = total_revenue - total_expenses

    @api.model
    def init(self):
        """Create or Update the Financial Report View"""
        self.env.cr.execute("""
            DROP VIEW IF EXISTS snooker_financial_report;
            CREATE VIEW snooker_financial_report AS (
                SELECT
                    to_char(e.date, 'YYYY-MM') AS id,
                    to_char(e.date, 'Month YYYY') AS name,
                    COALESCE(SUM(r.total_income), 0) AS total_collected,
                    COALESCE(SUM(e.paid_amount), 0) AS total_expensess,
                    COALESCE(SUM(CASE WHEN e.category = 'salary' THEN e.paid_amount ELSE 0 END), 0) AS salary_expense,
                    COALESCE(SUM(CASE WHEN e.category = 'rent' THEN e.paid_amount ELSE 0 END), 0) AS rent_expense,
                    COALESCE(SUM(CASE WHEN e.category = 'electricity' THEN e.paid_amount ELSE 0 END), 0) AS electricity_expense,
                    COALESCE(SUM(CASE WHEN e.category = 'maintenance' THEN e.paid_amount ELSE 0 END), 0) AS maintenance_expense,
                    COALESCE(SUM(CASE WHEN e.category = 'equipment' THEN e.paid_amount ELSE 0 END), 0) AS equipment_expense,  -- ✅ FIXED
                    (COALESCE(SUM(r.total_income), 0) - COALESCE(SUM(e.paid_amount), 0)) AS net_balance
                FROM snooker_expense e
                LEFT JOIN snooker_revenue r ON to_char(e.date, 'YYYY-MM') = to_char(r.create_date, 'YYYY-MM')
                GROUP BY to_char(e.date, 'YYYY-MM'), to_char(e.date, 'Month YYYY')
            )
        """)

