from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    cin_number = fields.Char(string='CIN Number')
