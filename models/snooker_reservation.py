"""
Author: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
Date: 2025-02-17 11:03:57
LastEditors: Safiullah Arian 65605444+safiullah-arian@users.noreply.github.com
LastEditTime: 2025-02-18 22:32:00
FilePath: customization/snooker_reservation/models/snooker_reservation.py
Description: 这是默认设置,可以在设置》工具》File Description中进行配置
"""
from email.policy import default
#
from odoo import models, fields, api
from datetime import datetime
class SnookerTable(models.Model):
    _name = "snooker.table"
    _description = "Snooker Table"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance

    _rec_name = "name"

    name = fields.Char("Table Name", required=True)
    table_type = fields.Selection([("vip", "VIP"), ("regular", "Regular")], string="Table Type", required=True)
    hourly_rate = fields.Float("Hourly Rate", required=True)

    game_rate = fields.Float( store=True)
    status = fields.Selection([("available", "Available"), ("occupied", "Occupied")], default="available")

    def action_add_game(self):
        for record in self:
            print("Available fields:", record._fields.keys())  # Print available fields
            if hasattr(record, 'game_rate'):
                record.game_rate *= 2
                print(f"Updated Game Rate: {record.game_rate}")
            else:
                print("Field 'game_rate' not found!")





class SnookerReservation(models.Model):
    _name = "snooker.reservation"
    _description = "Table Reservation"
    _inherit = ["mail.thread", "mail.activity.mixin"]  # Add inheritance

    _rec_name = "customer_id"

    customer_id = fields.Many2one("res.partner", string="Customer", required=True)
    table_id = fields.Many2one(
        "snooker.table",
        string="Table",
        required=True,
        domain=[('status', '=', 'available')]
    )
    reservation_type = fields.Selection([('hourly', 'Hourly'), ('game', 'Game')], string="Reservation Type", default="hourly",required=True)
    start_time = fields.Datetime("Start Time")
    end_time = fields.Datetime("End Time")
    total_cost = fields.Float("Total Cost", compute="_compute_total_costs", store=True)
    number_of_games = fields.Integer("Number of Games", required=True, default=2)
    game_rate = fields.Float(string="Game Rate", related="table_id.game_rate", store=True, readonly=True)
    duration = fields.Float("Duration (Hours)", compute="_compute_duration", store=True)
    peak_hours = fields.Boolean("Peak Hours", compute="_compute_peak_hours", store=True)
    amount_paid = fields.Float("Amount Paid", default=0.0)
    remaining_balance = fields.Float("Remaining Balance", compute="_compute_remaining_balance", store=True)
    is_fully_paid = fields.Boolean("Fully Paid", store=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ("future_booking", "Future Booking"),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default="draft", tracking=True)

    is_future_booking = fields.Boolean(string="Future Booking", compute="_compute_future_booking", store=True)
    show_remove_game = fields.Integer(
        string="Show Remove Game Button",
        compute="_compute_show_remove_game",
    )

    @api.depends('total_cost', 'remaining_balance')
    def _compute_is_fully_paid(self):
        for record in self:
            record.is_fully_paid = record.total_cost > 0 and record.remaining_balance == 0

    @api.depends('number_of_games')
    def _compute_show_remove_game(self):
        """Show the button only if number_of_games > 1"""
        for record in self:
            record.show_remove_game = record.number_of_games > 1

    @api.depends('number_of_games', 'game_rate')
    def _compute_total_costs(self):
        for record in self:
            # Assuming a fixed cost per game, e.g., 10.0
            # cost_per_game = 10.0   You can change this value as needed
            record.total_cost = record.number_of_games * record.game_rate

    def action_add_game(self):
        """Increment the number of games by 1 when the 'Add Game' button is clicked."""
        for record in self:
            record.number_of_games += 1  # Increment the number of games
            record.message_post(body=f'Number of Games Increased! New Total: {record.number_of_games}')

    def action_remove_game(self):
        """Decrement the number of games, ensuring it doesn't go below 1."""
        for record in self:
            if record.number_of_games > 1:
                record.number_of_games -= 1
            else:
                record.number_of_games = 1  # Ensure it doesn't go below 1

    @api.depends("start_time", "end_time")
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600
            else:
                record.duration = 0.0

    @api.depends("start_time")
    def _compute_peak_hours(self):
        for record in self:
            if record.start_time and 18 <= record.start_time.hour <= 23:
                record.peak_hours = True
            else:
                record.peak_hours = False

    @api.depends("duration", "table_id", "peak_hours", "reservation_type")
    def _compute_total_cost(self):
        for record in self:
            if record.table_id:
                if record.reservation_type == 'hourly' and record.duration:
                    rate = record.table_id.hourly_rate
                    if record.peak_hours:
                        rate += 50
                    record.total_cost = record.duration * rate
                elif record.reservation_type == 'game':
                    record.total_cost = record.table_id.game_rate
                else:
                    record.total_cost = 0.0

    @api.depends("total_cost", "amount_paid")
    def _compute_remaining_balance(self):
        for record in self:
            record.remaining_balance = record.total_cost - record.amount_paid

    @api.depends("start_time")
    def _compute_future_booking(self):
        for record in self:
            if record.start_time and isinstance(record.start_time, datetime):
                record.is_future_booking = record.start_time > datetime.now()
            else:
                record.is_future_booking = False

    def action_register_payment(self, amount_paid):
        if amount_paid <= 0:
            raise models.ValidationError("Amount must be greater than zero.")
        self.amount_paid += amount_paid

    def action_generate_invoice(self):
        invoice_vals = {
            'partner_id': self.customer_id.id,
            'move_type': 'out_invoice',
            'invoice_line_ids': [(0, 0, {
                'name': f'Snooker Table Reservation ({self.start_time})',
                'quantity': self.duration if self.reservation_type == 'hourly' else 1,
                'price_unit': self.table_id.hourly_rate if self.reservation_type == 'hourly' else self.table_id.game_rate,
            })],
        }
        invoice = self.env['account.move'].create(invoice_vals)
        return invoice

    def action_confirm(self):
        if not self.start_time:
            raise models.ValidationError("Start time is not set!")
        if self.start_time > datetime.now():
            self.status = "future_booking"
        else:
            self.status = "confirmed"

    def action_start(self):
        if not self.start_time:
            self.start_time = fields.Datetime.now()
        if self.start_time <= datetime.now():
            self.status = "in_progress"
        else:
            raise models.ValidationError("Cannot start the booking before the scheduled time!")

    def action_complete(self):
        if not self.end_time:
            self.end_time = fields.Datetime.now()
        self.status = "completed"

    def action_cancel(self):
        self.status = "cancelled"

    def check_future_bookings(self):
        now = datetime.now()
        future_bookings = self.search([( "status", "=", "future_booking" ), ( "start_time", "<=", now )])
        for booking in future_bookings:
            booking.status = "confirmed"

    def action_open_payment_wizard(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Register Payment',
            'res_model': 'snooker.payment.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_reservation_id': self.id}
        }


# 
# class SnookerTable(models.Model):
#     _name = "snooker.table"
#     _description = "Snooker Table"
#     _rec_name = "name"
# 
#     name = fields.Char("Table Name", required=True)
#     table_type = fields.Selection([("vip", "VIP"), ("regular", "Regular")], string="Table Type", required=True)
#     hourly_rate = fields.Float("Hourly Rate", required=True)
#     status = fields.Selection([("available", "Available"), ("occupied", "Occupied")], default="available")
# 
# 
# class SnookerReservation(models.Model):
#     _name = "snooker.reservation"
#     _description = "Table Reservation"
#     _rec_name = "customer_id"
# 
#     customer_id = fields.Many2one("res.partner", string="Customer", required=True)
#     table_id = fields.Many2one(
#         "snooker.table",
#         string="Table",
#         required=True,
#         domain=[('status', '=', 'available')]  # Domain to only show available tables
#     )
#     start_time = fields.Datetime("Start Time", )
#     end_time = fields.Datetime("End Time")
#     total_cost = fields.Float("Total Cost", compute="_compute_total_cost", store=True)
# 
#     duration = fields.Float("Duration (Hours)", compute="_compute_duration", store=True)
#     peak_hours = fields.Boolean("Peak Hours", compute="_compute_peak_hours", store=True)
#     amount_paid = fields.Float("Amount Paid", default=0.0)
#     remaining_balance = fields.Float("Remaining Balance", compute="_compute_remaining_balance", store=True)
#     is_fully_paid = fields.Boolean("Fully Paid", store=True)
#     # compute = "_compute_fully_paid",
#     status = fields.Selection([
#         ('draft', 'Draft'),
#         ('confirmed', 'Confirmed'),
#         ("future_booking", "Future Booking"),
#         ('in_progress', 'In Progress'),
#         ('completed', 'Completed'),
#         ('cancelled', 'Cancelled'),
#     ], string="Status", default="draft", tracking=True)
# 
#     is_future_booking = fields.Boolean(string="Future Booking", compute="_compute_future_booking", store=True) \
# 
#     @api.depends("start_time", "end_time")
#     def _compute_duration(self):
#             """Compute the total duration in hours"""
#             for record in self:
#                 if record.start_time and record.end_time:
#                     delta = record.end_time - record.start_time
#                     record.duration = delta.total_seconds() / 3600  # Convert seconds to hours
#                 else:
#                     record.duration = 0.0
# 
#     @api.depends("start_time")
#     def _compute_peak_hours(self):
#         """Determine if reservation falls in peak hours (6 PM - 11 PM)"""
#         for record in self:
#             if record.start_time and 18 <= record.start_time.hour <= 23:
#                 record.peak_hours = True
#             else:
#                 record.peak_hours = False
# 
#     @api.depends("duration", "table_id", "peak_hours")
#     def _compute_total_cost(self):
#         """Compute the total cost based on duration and peak pricing"""
#         for record in self:
#             if record.duration and record.table_id:
#                 rate = record.table_id.hourly_rate
#                 if record.peak_hours:
#                     rate += 50  # Add 50 extra for peak hours
#                 record.total_cost = record.duration * rate
#             else:
#                 record.total_cost = 0.0
# 
#     @api.depends("total_cost", "amount_paid")
#     def _compute_remaining_balance(self):
#         """Compute the remaining balance"""
#         for record in self:
#             record.remaining_balance = record.total_cost - record.amount_paid
# 
#     # @api.depends("remaining_balance")
#     # def _compute_fully_paid(self):
#     #     """Check if the full amount is paid"""
#     #     for record in self:
#     #         record.is_fully_paid = record.remaining_balance <= 0
# 
#     def action_register_payment(self, amount_paid):
#         """Allow users to register payments"""
#         if amount_paid <= 0:
#             raise models.ValidationError("Amount must be greater than zero.")
#         self.amount_paid += amount_paid
# 
#     @api.depends("start_time")
#     def _compute_future_booking(self):
#         """Automatically mark reservations as future bookings if scheduled after the current time"""
#         for record in self:
#             if record.start_time and isinstance(record.start_time, datetime):
#                 record.is_future_booking = record.start_time > datetime.now()
#             else:
#                 record.is_future_booking = False  # Default to False if no start time is set
# 
#     def action_generate_invoice(self):
#         """Automatically generate an invoice for the reservation"""
#         invoice_vals = {
#             'partner_id': self.customer_id.id,
#             'move_type': 'out_invoice',
#             'invoice_line_ids': [(0, 0, {
#                 'name': f'Snooker Table Reservation ({self.start_time})',
#                 'quantity': self.duration,
#                 'price_unit': self.table_id.hourly_rate,
#             })],
#         }
#         invoice = self.env['account.move'].create(invoice_vals)
#         # self.message_post(body=f"Invoice {invoice.name} generated.")
#         return invoice
# 
#     def action_confirm(self):
#         """Confirm the reservation. If the booking is in the future, keep it as a future booking."""
#         if not self.start_time:
#             raise models.ValidationError("Start time is not set!")
# 
#         # Compare start_time with current time
#         if self.start_time > datetime.now():
#             self.status = "future_booking"
#         else:
#             self.status = "confirmed"
# 
#     def action_start(self):
#         """Start the reservation and set start_time only if it's empty."""
#         # Check if start_time is already set
#         if not self.start_time:
#             current_time = fields.Datetime.now()  # Get the current system date and time
#             self.start_time = current_time  # Set start_time to the current time
# 
#         # Check if current time matches or is after the scheduled start time
#         if self.start_time <= datetime.now():
#             self.status = "in_progress"
#         else:
#             raise models.ValidationError("Cannot start the booking before the scheduled time!")
# 
#     # def action_complete(self):
#     #     self.status = "completed"
#     def action_complete(self):
#         """Complete the reservation and set end_time only if it's not already set."""
#         if not self.end_time:  # Check if end_time is empty
#             current_time = fields.Datetime.now()  # Get the current system date and time
#             self.end_time = current_time  # Set end_time to the current time
# 
#         # Change the status to 'completed'
#         self.status = "completed"
# 
#     def action_cancel(self):
#         self.status = "cancelled"
# 
#     @api.depends("start_time", "end_time", "table_id")
#     def _compute_total_cost(self):
#         for record in self:
#             if record.start_time and record.end_time and record.table_id:
#                 duration = (record.end_time - record.start_time).total_seconds() / 3600
#                 record.total_cost = duration * record.table_id.hourly_rate
# 
#     def check_future_bookings(self):
#         """Automatically move future bookings to 'Confirmed' when the scheduled time arrives"""
#         now = datetime.now()
#         future_bookings = self.search([("status", "=", "future_booking"), ("start_time", "<=", now)])
#         for booking in future_bookings:
#             booking.status = "confirmed"
# 
#     def action_open_payment_wizard(self):
#         """Opens the payment wizard to enter payment amount"""
#         return {
#             'type': 'ir.actions.act_window',
#             'name': 'Register Payment',
#             'res_model': 'snooker.payment.wizard',
#             'view_mode': 'form',
#             'target': 'new',
#             'context': {'default_reservation_id': self.id}
#         }
