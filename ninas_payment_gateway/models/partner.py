# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.exceptions import Warning

class ResPartner(models.Model):
    _inherit = 'res.partner'

    code = fields.Char(string='Code')

    @api.constrains('code')
    def check_code(self):
        if self.code:
            if self.search([('code','=',self.code),('id','!=',self.id)]):
                return Warning('Code must be unique!')