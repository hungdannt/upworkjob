from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    gstin = fields.Char(string='GSTIN')
    code = fields.Char(string='Ref Code')
