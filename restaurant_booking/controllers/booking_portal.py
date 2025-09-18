# controllers/table_booking.py
from odoo import http
from odoo.http import request
import json
import logging
from datetime import datetime

_logger = logging.getLogger(__name__)

class TableBookingController(http.Controller):
    
    @http.route('/booking', type='http', auth='public', website=True, csrf=False)
    def table_booking_page(self, **kwargs):
        return request.render('restaurant_booking.table_selection_template')
    
    @http.route('/get_floors', type='json', auth='public', methods=['POST'], csrf=False)
    def get_floors(self, **kwargs):
        try:
            floors = request.env['restaurant.floor'].sudo().search([])
            return {
                'success': True,
                'floors': [{
                    'id': floor.id,
                    'name': floor.name,
                    'table_count': len(floor.table_ids)
                } for floor in floors]
            }
        except Exception as e:
            _logger.error(f"Error getting floors: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/get_tables/<int:floor_id>', type='json', auth='public', methods=['POST'], csrf=False)
    def get_tables(self, floor_id, **kwargs):
        try:
            tables = request.env['restaurant.table'].sudo().search([
                ('floor_id', '=', floor_id)
            ])
            
            return {
                'success': True,
                'tables': [{
                    'id': table.id,
                    'name': table.table_number,
                    'table_number': table.table_number,
                    'seats': getattr(table, 'seats', 4),
                    'state': table.state,
                    'position_h': getattr(table, 'position_h', 0),
                    'position_v': getattr(table, 'position_v', 0),
                } for table in tables]
            }
        except Exception as e:
            _logger.error(f"Error getting tables: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/create_booking', type='json', auth='public', methods=['POST'], csrf=False)
    def create_booking(self, **kwargs):
        try:
            # Validate
            required_fields = ['customer_name', 'customer_phone', 'booking_date', 'booking_time', 'table_ids']
            for field in required_fields:
                if not kwargs.get(field):
                    return {'success': False, 'error': f'Missing: {field}'}
            
            table_ids = kwargs.get('table_ids', [])
            
            # Check if tables are still available
            tables = request.env['restaurant.table'].sudo().browse(table_ids)
            booked_tables = tables.filtered(lambda t: t.state == 'booked')
            if booked_tables:
                return {
                    'success': False, 
                    'error': f'Tables {", ".join(booked_tables.mapped("name"))} are no longer available'
                }
            
            # Mark tables as booked
            tables.write({'state': 'booked'})
            
            # Create booking record (if model exists)
            try:
                booking = request.env['restaurant.booking'].sudo().create({
                    'customer_name': kwargs.get('customer_name'),
                    'customer_phone': kwargs.get('customer_phone'),
                    'customer_email': kwargs.get('customer_email', ''),
                    'booking_date': kwargs.get('booking_date'),
                    'booking_time': kwargs.get('booking_time'),
                    'guest_count': int(kwargs.get('guest_count', 2)),
                    'notes': kwargs.get('notes', ''),
                    'table_ids': [(6, 0, table_ids)],
                    'state': 'confirmed',
                })
                
                return {
                    'success': True,
                    'booking_id': booking.id,
                    'booking_ref': f'BK{booking.id:06d}',
                }
                
            except Exception as model_error:
                # If booking model doesn't exist, just log
                _logger.info(f"Booking: {kwargs} - Tables {table_ids} marked as booked")
                
                return {
                    'success': True,
                    'booking_id': abs(hash(str(kwargs))) % 10000,
                    'booking_ref': f'BK{abs(hash(str(kwargs))) % 10000:06d}',
                }
                
        except Exception as e:
            _logger.error(f"Booking error: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    @http.route('/booking_success/<int:booking_id>', type='http', auth='public', website=True)
    def booking_success(self, booking_id, **kwargs):
        try:
            booking = request.env['restaurant.booking'].sudo().browse(booking_id)
            if booking.exists():
                return request.render('restaurant_booking.booking_success_template', {
                    'booking': booking
                })
            else:
                request.render('website.404')
        except Exception as e:
            return request.render('website.404')
    
    @http.route('/reset_tables', type='http', auth='public', website=True)
    def reset_tables(self, **kwargs):
        """Debug route để reset tất cả bàn về available"""
        try:
            tables = request.env['restaurant.table'].sudo().search([])
            tables.write({'state': 'available'})
            return f"Reset {len(tables)} tables to available"
        except Exception as e:
            return f"Error: {str(e)}"