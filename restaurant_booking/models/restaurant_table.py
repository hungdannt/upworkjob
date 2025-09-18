from odoo import models, fields

class RestaurantTable(models.Model):
    _inherit = "restaurant.table"

    state = fields.Selection([
        ('available', 'Available'),
        ('booked', 'Booked')
    ], default='available')
