from odoo import models, fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    booking_id = fields.Many2one("restaurant.booking", string="Booking Ref")
