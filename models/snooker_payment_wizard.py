"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 12:43:37
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 21:57:07
FilePath: customization/snooker_reservation/models/snooker_payment_wizard.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""

from odoo import models, fields, api

class SnookerPaymentWizard(models.TransientModel):
    _name = "snooker.payment.wizard"
    _description = "Snooker Payment Wizard"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance

    _rec_name = "reservation_id"

    reservation_id = fields.Many2one("snooker.reservation", string="Reservation", required=True)
    amount = fields.Float("Payment Amount", required=True)

    def action_register_payment(self):
        """Register the payment for the reservation"""
        if self.amount <= 0:
            raise models.ValidationError("Payment amount must be greater than zero.")

        self.reservation_id.amount_paid += self.amount
        # self.reservation_id.message_post(body=f"Payment of {self.amount} recorded.")
        # return {'type': 'ir.actions.act_window_close'}
    

