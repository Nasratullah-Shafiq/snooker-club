"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 14:53:00
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 21:57:07
FilePath: customization/snooker_reservation/models/snooker_revenue.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
from odoo import models, fields, api

class SnookerRevenue(models.Model):
    _name = "snooker.revenue"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance
    _description = "Snooker Club Revenue"

    name = fields.Char("Revenue Name", required=True)
    total_income = fields.Float("Total Income", required=True)
    total_expenses = fields.Float("Total Expenses", compute="_compute_total_expenses", store=True)
    available_balance = fields.Float("Available Balance", compute="_compute_available_balance", store=True)

    @api.depends("total_income", "total_expenses")
    def _compute_available_balance(self):
        """Calculate remaining revenue after expenses"""
        for record in self:
            record.available_balance = record.total_income - record.total_expenses

    @api.depends("total_income")
    def _compute_total_expenses(self):
        """Calculate total expenses deducted from revenue"""
        for record in self:
            record.total_expenses = sum(record.env["snooker.expense"].search([
                ("snooker_revenue_id", "=", record.id),
                ("payment_source", "=", "snooker_fees"),
            ]).mapped("paid_amount"))
