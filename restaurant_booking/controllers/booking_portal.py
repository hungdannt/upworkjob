from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class TableBookingController(http.Controller):
    
    @http.route('/booking', type='http', auth='public', website=True, csrf=False)
    def table_booking_page(self, **kwargs):
        return request.render('restaurant_booking.table_selection_template')

    @http.route('/admin/booking', type='http', auth='user', website=True, csrf=False)
    def admin_booking_page(self, **kwargs):
        return request.render('restaurant_booking.admin_floor_layout_template')

    @http.route('/restaurant/timeslots', type='json', auth='public')
    def get_time_slots(self, date):
        try:
            slots = request.env["restaurant.time.slot"].sudo().search([("active", "=", True)])
            tables = request.env['restaurant.table'].sudo().search([('active', '=', True)])
            available_slots = []

            for slot in slots:
                exist_bookings = request.env['restaurant.booking'].sudo().search([
                    ('booking_date', '=', date),
                    ('slot_id', '=', slot.id),
                    ('state', '=', 'confirmed')
                ])
                booked_table_ids = set(exist_bookings.mapped('table_id.id'))

                available_tables = tables.filtered(lambda t: t.id not in booked_table_ids)
                if available_tables:
                    available_slots.append(slot)

            if not available_slots:
                return {'success': False, 'error': 'No available time slots'}

            return {'success': True, 'slots': [{"id": s.id, "name": s.name} for s in available_slots]}

        except Exception as e:
            _logger.error(f"Error getting time slots: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/create_booking', type='json', auth='public', methods=['POST'], csrf=False)
    def create_booking(self, **kwargs):
        try:
            required_fields = ['customer_name', 'customer_phone', 'booking_date', 'booking_time']
            for field in required_fields:
                if not kwargs.get(field):
                    return {'success': False, 'error': f'Missing: {field}'}
            
            booking = request.env['restaurant.booking'].sudo().create({
                'customer_name': kwargs.get('customer_name'),
                'customer_phone': kwargs.get('customer_phone'),
                'customer_email': kwargs.get('customer_email', ''),
                'booking_date': kwargs.get('booking_date'),
                'slot_id': kwargs.get('booking_time'),
                'guest_count': int(kwargs.get('guest_count', 2)),
                'notes': kwargs.get('notes', ''),
                'state': 'pending',
            })
            
            return {
                'success': True,
                'booking_id': booking.id,
                'booking_ref': f'MV{booking.id:06d}',
            }
                
        except Exception as e:
            _logger.error(f"Booking error: {str(e)}")
            return {'success': False, 'error': str(e)}

    @http.route('/booking_success/<int:booking_id>', type='http', auth='public', website=True)
    def booking_success(self, booking_id, **kwargs):
        booking = request.env['restaurant.booking'].sudo().browse(booking_id)
        if booking.exists():
            return request.render('restaurant_booking.booking_success_template', {
                'booking': booking,
                'message': "Thank you for your table reservation request. We will confirm your booking shortly"
            })
        else:
            return request.render('website.404')

    @http.route('/admin/booking/floors', type='json', auth='user')
    def admin_get_floors(self):
        floors = request.env['restaurant.floor'].sudo().search([])
        return {'floors': [{'id': f.id, 'name': f.name} for f in floors]}

    @http.route('/admin/booking/tables/<int:floor_id>', type='json', auth='user')
    def admin_get_tables(self, floor_id):
        tables = request.env['restaurant.table'].sudo().search([('floor_id', '=', floor_id), ('active', '=', True)])
        # get bookings on that floor for relevant date range or all
        bookings = request.env['restaurant.booking'].sudo().search([])
        return {
            'tables': [t.read(['id','table_number','seats','shape','position_h','position_v','width','height'])[0] for t in tables],
            'bookings': [b.read(['id','name','booking_date','create_date','customer_name','customer_phone','customer_email','slot_id','state','table_id','guest_count','notes'])[0] for b in bookings],
        }

    @http.route('/admin/booking/assign_table', type='json', auth='user', methods=['POST'])
    def admin_assign_table(self, booking_id, table_id):
        try:
            b = request.env['restaurant.booking'].sudo().browse(int(booking_id))
            if not b.exists():
                return {'success': False, 'error': 'Booking not found'}
            b.sudo().write({'table_id': int(table_id), 'state': 'confirmed'})
            b.table_id.sudo().write({'state': 'booked'})
            return {'success': True}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    @http.route('/admin/booking/available_tables/<int:floor_id>', type='json', auth='user')
    def get_tables_for_booking(self, booking_id, floor_id):
        booking = request.env['restaurant.booking'].sudo().browse(booking_id)
        tables = request.env['restaurant.table'].sudo().search([('floor_id', '=', floor_id), ('active', '=', True)])

        conflict_bookings = request.env['restaurant.booking'].sudo().search([
            ('booking_date', '=', booking.booking_date),
            ('slot_id', '=', booking.slot_id.id),
            ('state', '=', 'confirmed')
        ])
        booked_table_ids = set(conflict_bookings.mapped('table_id.id'))

        table_data = []
        for t in tables:
            table_data.append({
                'id': t.id,
                'table_number': t.table_number,
                'seats': t.seats,
                'shape': t.shape,
                'position_h': t.position_h,
                'position_v': t.position_v,
                'width': t.width,
                'height': t.height,
                'state': 'booked' if t.id in booked_table_ids else 'available',
                'disabled': t.id in booked_table_ids,
            })

        return {'tables': table_data}

