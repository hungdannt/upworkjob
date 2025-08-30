from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    address = fields.Char(string='Address Line 1')
    cin_number = fields.Char(string='CIN Number')
    gstin = fields.Char(string='GSTIN', help="GST Identification Number")
