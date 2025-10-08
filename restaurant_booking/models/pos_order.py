from odoo import models, fields

class PosOrder(models.Model):
    _inherit = "pos.order"

    booking_id = fields.Many2one("restaurant.booking", string="Booking Ref")

    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'paid':
                self.booking_id.state = 'done'
        return super(PosOrder, self).write(vals)
            
