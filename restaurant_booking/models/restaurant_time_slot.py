from odoo import models, fields, api

class RestaurantTimeSlot(models.Model):
    _name = "restaurant.time.slot"
    _description = "Restaurant Time Slot"
    _inherit = ['pos.load.mixin']

    name = fields.Char()
    start_time = fields.Float(string="Start Time", required=True)  
    end_time = fields.Float(string="End Time", required=True)     
    active = fields.Boolean(default=True)
    
    @api.onchange("start_time", "end_time")
    def _onchange_times(self):
        if self.start_time and self.end_time:
            self.name = f"{int(self.start_time):02d}:00 - {int(self.end_time):02d}:00"