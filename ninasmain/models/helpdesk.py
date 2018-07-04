 # -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18

import datetime

from datetime import date, timedelta
from odoo import api, fields, models
#from gevent._ssl3 import name
#from plainbox.impl.unit import file


class Accreditation(models.Model):
    _inherit = 'helpdesk.ticket'
    
    attachment_ids = fields.Many2many('ir.attachment', 'res_id', domain=[('res_model', '=', 'helpdesk.ticket')], string='Attachments')

    assessment_team_ids = fields.Many2many(comodel_name='hr.employee',
                                     string='Assessment Team')
    
    assessment_type_id = fields.Many2one(
        comodel_name='assessment.type',
        string='Assesment Type',
        track_visibility='onchange')
    
    funding = fields.Selection(
        [('not_funded','Not Funded'),('partly_funded', 'Partly Funded'),('fully_funded', 'Fully Funded')],
        string='Funding',
        default='not_funded',
        track_visibility='onchange')
    
    Lead_assessor_id = fields.Many2one(comodel_name='hr.employee', string='Lead Assesor', track_visibility='onchange', domain=lambda self: [('groups_id', 'in', self.env.ref('helpdesk.group_helpdesk_user').id)])


class AssessmentType(models.Model):
    _name = 'assessment.type'
    
    name = fields.Char(string='Assessment Type')
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        relation='ninas_assessment_type_rel',
        column1='assessment_type_id',
        column2='attachment_id',
        string='Attachment')
    

    
    