"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 14:24:45
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 21:57:07
FilePath: customization/snooker_reservation/models/snooker_expense_payment_wizard.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
from odoo import models, fields, api

class SnookerExpensePaymentWizard(models.TransientModel):
    _name = "snooker.expense.payment.wizard"
    _description = "Expense Payment Wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance


    expense_id = fields.Many2one("snooker.expense", string="Expense", required=True)
    amount = fields.Float("Payment Amount", required=True)

    def action_register_payment(self):
        """Register payment for an expense"""
        if self.amount <= 0:
            raise models.ValidationError("Payment amount must be greater than zero.")

        self.expense_id.paid_amount += self.amount
        self.expense_id.message_post(body=f"Payment of {self.amount} recorded.")
        return {'type': 'ir.actions.act_window_close'}
