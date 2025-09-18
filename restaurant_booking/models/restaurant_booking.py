from odoo import models, fields, api

class RestaurantBooking(models.Model):
    _name = 'restaurant.booking'
    _description = 'Restaurant Table Booking'
    
    name = fields.Char('Booking Reference', required=True, default='New')
    customer_name = fields.Char('Customer Name', required=True)
    customer_phone = fields.Char('Phone', required=True)
    customer_email = fields.Char('Email')
    booking_date = fields.Date('Date', required=True)
    booking_time = fields.Char('Time', required=True)
    guest_count = fields.Integer('Guests', default=2)
    notes = fields.Text('Notes')
    table_ids = fields.Many2many('restaurant.table', string='Tables')
    state = fields.Selection([
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], default='confirmed')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('restaurant.booking') or 'New'
        return super().create(vals)