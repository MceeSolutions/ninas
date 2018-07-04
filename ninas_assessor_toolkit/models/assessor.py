# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class AssessorToolkit(models.Model):
    _name = 'ninas.assessor.toolkit'


class AssessmentFeedback(models.Model):
    _name = 'ninas.assessment.feedback'
    _description = 'Ninas Assessment Feedback'

    name = fields.Char(
        string='Reference No', 
        required=True)

    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Accreditation ID',
        required=True)

    institution_name = fields.Char(
        related='application_id.partner_id.company_name',
        string='Institution',
        store=True)

    institution_representative = fields.Char(
        related='application_id.partner_id.name',
        string='Institution Representative',
        store=True)

    assessment_team_ids = fields.Many2many(
        related='application_id.assessment_team_ids',
        )

    lead_assessor_id = fields.Many2one(
        related='application_id.lead_assessor_id',
        store=True)  

    assessment_date = fields.Date(
        string='Assessment Date', 
        required=True)

    comments = fields.Text(
        string='Comments')

    action_completed = fields.Text(
        string='Action Completed')

    feedback = fields.Text(
        string='Feedback provided')

    notes = fields.Text(
        string='Note')

    approval_date = fields.Date(
        string='Approval Date')