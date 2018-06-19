# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18

import datetime

from datetime import date, timedelta
from odoo import api, fields, models


class Accreditation(models.Model):
    _inherit = 'hr.employee'

    fname = fields.Char(string='First Name')
    lname = fields.Char(string='Last Name')
    address = fields.Char(string='street address')
    unit = fields.Char(string='Apartment Unit')
    relationship = fields.Char(string='Relationship')
    telphone = fields.Char(string='Primary Phone')
    phone_id = fields.Char(string='Alternate Phone')
    city = fields.Char(
        string='City')
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state')
    zip_code = fields.Char(string='Zip Code')
    email = fields.Char(string='email')
    officail_id = fields.Char(string='Official ID Card')
    spouse_name = fields.Char(string='Spouse Name')
    spouse_employer = fields.Char(string='Spouse Employer')
    spouse_phone = fields.Char(string='Spouse Phone')
    title = fields.Char(string='Title')
    employee = fields.Char(string='Employee ID')
    start_date = fields.Date(string='Start Date')
    salary = fields.Char(string='Salary')