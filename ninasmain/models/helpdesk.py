 # -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18

import datetime

from datetime import date, timedelta
from odoo import api, fields, models


class Accreditation(models.Model):
    _inherit = 'helpdesk.ticket'
    
    attachment_ids = fields.Many2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'helpdesk.ticket')], string='Attachments')

    assesmentteam_id = fields.Many2many(comodel_name='res.users',
                                     string='Assesment Team')
    
    assesment_type = fields.Selection(
        [('iso2','ISO 2'),('iso1', 'ISO 1')],
        string='Assesment Type',
        default='iso2',
        track_visibility='onchange')
    
    funding = fields.Selection(
        [('not','Not Funded'),('part', 'Partly Funded'),('full', 'Fully Funded')],
        string='Funding',
        default='not',
        track_visibility='onchange')
    
    user_id = fields.Many2one('res.users', string='Lead Assesor', track_visibility='onchange', domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])