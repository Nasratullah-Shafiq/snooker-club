"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 14:14:14
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 11:25:44
FilePath: customization/snooker_reservation/models/snooker_expense.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""


from odoo import models, fields, api
from datetime import datetime


class SnookerExpense(models.Model):
    _name = "snooker.expense"
    _description = "Snooker Club Expenses"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance

    name = fields.Char("Expense Name", required=True)
    category = fields.Selection([
        ("rent", "Rent"),
        ("salary", "Salary"),
        ("electricity", "Electricity"),
        ("maintenance", "Maintenance"),
        ("equipment", "Equipment Purchase"),
        ("other", "Other"),
    ], string="Category", required=True)
    amount = fields.Float("Amount", required=True)
    paid_amount = fields.Float("Paid Amount", default=0.0)
    remaining_balance = fields.Float("Remaining Balance", compute="_compute_remaining_balance", store=True)
    is_fully_paid = fields.Boolean("Fully Paid", compute="_compute_fully_paid", store=True)
    date = fields.Date("Expense Date", required=True, default=fields.Date.today)
    payment_source = fields.Selection([
        ("snooker_fees", "Snooker Fee Collection"),
        ("cash", "Cash Payment"),
        ("bank", "Bank Transfer"),
        ("other", "Other"),
    ], string="Payment Source", required=True, default="snooker_fees")
    description = fields.Text("Description")
    snooker_revenue_id = fields.Many2one("snooker.revenue", string="Revenue Source")  # Connects to Snooker Revenue

   
    @api.depends("remaining_balance")
    def _compute_fully_paid(self):
        """Check if expense is fully paid"""
        for record in self:
            record.is_fully_paid = record.remaining_balance <= 0

    def action_register_expense_payment(self):
        """Apply payment to an expense from snooker revenue"""
        for record in self:
            amount = record.remaining_balance  # Auto-pay remaining balance if amount is not provided

            if amount <= 0:
                raise models.ValidationError("Payment amount must be greater than zero.")
            if amount > record.remaining_balance:
                raise models.ValidationError("Payment exceeds the remaining balance.")

            # Deduct from Snooker Revenue if selected
            if record.payment_source == "snooker_fees":
                if not record.snooker_revenue_id:
                    raise models.ValidationError("No snooker revenue linked for this payment.")
                if record.snooker_revenue_id.available_balance < amount:
                    raise models.ValidationError("Not enough revenue available to cover this expense.")
                record.snooker_revenue_id.available_balance -= amount  # Deduct from revenue

            record.paid_amount += amount
            record.message_post(body=f"Expense Payment of {amount} recorded from {record.payment_source}.")
    
    def get_monthly_expense(self):
        """Calculate total expenses for the current month"""
        today = datetime.today()
        start_date = today.replace(day=1)
        expenses = self.search([('date', '>=', start_date), ('date', '<=', today)])
        return sum(expenses.mapped("amount"))
