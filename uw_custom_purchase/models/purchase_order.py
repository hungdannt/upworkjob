from odoo import models, fields, api
import logging

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning(
        "num2words library not installed. Install with: pip install num2words")
    num2words = None


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    # Additional fields for the report
    quote_ref = fields.Char(string='Quote Reference',
                            help="Vendor quote reference")
    delivery_terms = fields.Text(
        string='Delivery Terms', default='As per Schedule')
    other_terms = fields.Text(string='Other Terms')
    requested_by = fields.Many2one(
        'res.users', string='Requested By', default=lambda self: self.env.user)

    def _amount_to_words(self, amount):
        """Convert amount to words"""
        if not num2words:
            return "Amount conversion not available"

        try:
            # Convert to integer for whole number conversion
            whole_amount = int(amount)
            currency_name = self.currency_id.name or 'Rupees'

            if currency_name.upper() == 'INR':
                currency_name = 'Rupees'

            amount_words = num2words(whole_amount, lang='en').title()
            return f"{currency_name} {amount_words} only"
        except:
            return f"{self.currency_id.name or 'Rupees'} {amount} only"

    @api.model
    def _get_tax_totals(self):
        """Calculate tax totals for the report"""
        tax_lines = []
        for line in self.order_line:
            for tax in line.taxes_id:
                tax_amount = (line.price_subtotal * tax.amount) / 100
                tax_lines.append({
                    'name': tax.name,
                    'rate': tax.amount,
                    'amount': tax_amount
                })
        return tax_lines

    def _get_report_filename(self):
        return 'Purchase Order %s' % (self.name)


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Add discount field
    discount = fields.Float(string='Discount (%)',
                            digits='Discount', default=0.0)
    part_name = fields.Char(
        string='Part Name', related='product_id.default_code', store=True)

    @api.depends('product_qty', 'price_unit', 'discount', 'taxes_id')
    def _compute_amount(self):
        """Override to include discount calculation"""
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(
                price, line.order_id.currency_id, line.product_qty,
                product=line.product_id
            )
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
