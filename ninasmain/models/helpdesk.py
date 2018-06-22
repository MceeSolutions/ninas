# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18

import datetime

from datetime import date, timedelta
from odoo import api, fields, models


class Accreditation(models.Model):
    _inherit = 'helpdesk.ticket'

    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'helpdesk.ticket')], string='Attachments')