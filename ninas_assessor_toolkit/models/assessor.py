# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import time


"""class AssessorToolkit(models.Model):
    _name = 'ninas.assessor.toolkit'
"""


class AssessmentFeedback(models.Model):
    _name = 'ninas.assessment.feedback'
    _description = 'Ninas Assessment Feedback'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Reference No', 
        required=True,
        track_visibility='onchange',)

    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Accreditation ID',
        required=True,
        track_visibility='onchange',)

    institution_name = fields.Char(
        related='application_id.partner_id.company_name',
        string='Institution',
        store=True,
        track_visibility='onchange',)

    institution_representative = fields.Char(
        related='application_id.partner_id.name',
        string='Institution Representative',
        store=True,
        track_visibility='onchange',)

    assessment_team_ids = fields.Many2many(
        related='application_id.assessment_team_ids',
        track_visibility='onchange',
        )

    lead_assessor_id = fields.Many2one(
        related='application_id.lead_assessor_id',
        store=True,
        track_visibility='onchange',)  

    assessment_date = fields.Date(
        string='Assessment Date', 
        required=True, 
        track_visibility='onchange',
        default=lambda *a: time.strftime('%Y-%m-%d'))

    comments = fields.Text(
        string='Comments', track_visibility='onchange')

    action_completed = fields.Text(
        string='Action Completed', track_visibility='onchange',)

    feedback = fields.Text(
        string='Feedback provided', track_visibility='onchange',)

    notes = fields.Text(
        string='Note', track_visibility='onchange',)

    approval_date = fields.Date(
        string='Approval Date', track_visibility='onchange',)

    state = fields.Selection(
        [('new','New'),('refused','Refused'),('approved','Approved')],
        string='Status',
        default='new')

    def approve(self):
        self.write({'state':'approved', 'approval_date':time.strftime('%Y-%m-%d')})

    def draft(self):
        self.write({'state':'new', 'approval_date':False})

    def refuse(self):
        self.write({'state':'refused'})
