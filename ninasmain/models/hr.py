# -*-coding:utf-8-*-
from odoo import models, fields

class EmployeeCategory(models.Model):
    _inherit = 'hr.employee.category'
    
    is_assessor = fields.Boolean(
        string='Assessor?'
        )