# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import time


class AssessorToolkit(models.Model):
    _name = 'ninas.assessor.toolkit'


class BasicToolkitData(models.Model):
    _name = 'ninas.basic.toolkit.data'
    _description = 'Ninas Basic Toolkit Data'
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



class AssessmentClientFeedback(models.Model):
    _name = 'ninas.assessment.client.feedback'
    _description = 'Ninas Assessment Client Feedback'
    _inherit = 'ninas.basic.toolkit.data'

    

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


class AssessmentAssessorFeedback(models.Model):
    _name = 'ninas.assessment.assessor.feedback'
    _inherit = 'ninas.assessment.client.feedback'
    _description = 'Ninas Assessment Assessor Feedback'


    matter_raised = fields.Selection(
        [('technical_committee','Technical Committee'), ('ninas_director','NiNAS Director'),
         ('ninas_administrator', 'NiNAS Administrator')],
         string='Matters to be raise with the:',track_visibility='onchange')

    organization_change = fields.Boolean(
        string='Change in organization details',track_visibility='onchange')

    details = fields.Text(
        string='Details',track_visibility='onchange')



class AssessmentWitnessTemplate(models.Model):
    _name = 'ninas.witness.template'
    _description = 'Ninas Witness Template'
    _inherit = 'ninas.basic.toolkit.data'

    description = fields.Text(
        string='Identification Description')

    person_observed = fields.Many2one(
        comodel_name='hr.employee',
        string='Name of Person Observed',
        track_visibility='onchange')

    additional_comments = fields.Text(
        string='Additional Comments',
        track_visibility='onchange')

    internal_comments = fields.Text(
        string='Internal Comments',
        track_visibility='onchange')

    reference_comments = fields.Text(
        string='Reference Comments',
        track_visibility='onchange')

    uncertainty_comments = fields.Text(
        string='Uncertainty Comments',
        track_visibility='onchange')

    training_comments = fields.Text(
        string='Training Comments',
        track_visibility='onchange')

    accomodation_comments = fields.Text(
        string='Accomodation Comments',
        track_visibility='onchange')

    recommendation_comments = fields.Text(
        string='Recommendation Comments',
        track_visibility='onchange')

    state = fields.Selection(
        [('new','New'),('refused','Refused'),('lead_approved','Lead Approved'), 
        ('technical_approved','Technical Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')

    def lead_approve(self):
        self.write({'state':'lead_approved'})

    def technical_approve(self):
        self.write({'state':'technical_approved'})

    def draft(self):
        self.write({'state':'new', 'approval_date':False})

    def refuse(self):
        self.write({'state':'refused'})