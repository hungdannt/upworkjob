from odoo import models, fields, api

class RestaurantBooking(models.Model):
    _name = 'restaurant.booking'
    _description = 'Restaurant Table Booking'
    _inherit = ['pos.load.mixin']
    
    name = fields.Char('Booking Reference', required=True, default='New')
    customer_name = fields.Char('Customer Name', required=True)
    customer_phone = fields.Char('Phone', required=True)
    customer_email = fields.Char('Email')
    booking_date = fields.Date('Date', required=True)
    guest_count = fields.Integer('Guests')
    notes = fields.Char('Notes')
    pos_order_id = fields.Many2one('pos.order', string='POS Order')
    table_id = fields.Many2one('restaurant.table', string='Table')
    slot_id = fields.Many2one("restaurant.time.slot", required=True)
    partner_id = fields.Many2one('res.partner', string='Partner')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('occupied', 'Occupied'),
        ('no_show', 'No Show'),
        ('done', 'Done'),
    ], default='pending')
    
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('restaurant.booking')
        if vals.get('customer_email'):
            partner = self.env['res.partner'].search([("email", "=", vals.get('customer_email'))])
            if partner:
                vals['partner_id'] = partner.id
            else:
                partner = self.env['res.partner'].create({
                    'name': vals.get('customer_name'),
                    'phone': vals.get('customer_phone'),
                    'email': vals.get('customer_email')
                })
                vals['partner_id'] = partner.id
        return super().create(vals)        

    def write(self, vals):
        if 'state' in vals:
            if vals['state'] == 'occupied':
                vals['pos_order_id'] = self.env['pos.order'].search([('booking_id', '=', self.id), ("state", "=", "draft")], limit=1).id
        return super().write(vals)

    @api.model
    def available_slots(self, date, table_id):
        slots = self.env["restaurant.time.slot"].search([("active", "=", True)])
        booked = self.search([("booking_date", "=", date), ("state", "=", "confirmed")])
        booked_slot_ids = booked.mapped("slot_id.id")
        return slots.filtered(lambda s: s.id not in booked_slot_ids)


    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['name', 'customer_name', 'pos_order_id', 'customer_phone', 'customer_email', 'booking_date', 'guest_count', 'table_id', 'slot_id', 'partner_id', 'state']