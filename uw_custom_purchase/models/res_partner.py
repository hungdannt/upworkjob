from odoo import models, fields


class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(string='Ref Code')
