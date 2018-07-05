# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import time

ISO_STANDARD = [('iso1','ISO1'),('iso2','ISO2')]



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
        track_visibility='onchange')

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
        self.write({'state':'new'})

    def refuse(self):
        self.write({'state':'refused'})


class SurveillanceReport(models.Model):
    _name = 'ninas.surveillance.report'
    _description = 'Ninas Surveillance Report'
    _inherit = 'ninas.basic.toolkit.data'

    location = fields.Char(
        string='Location')

    start_date = fields.Date(
        string='Start Date',
        required=True)

    end_date = fields.Date(
        string='End Date',
        required=True)

    duration = fields.Integer(
        string='Duration (days)')

    assessment_type = fields.Selection(
        [('initial_assessment','Initial Assessment'),
         ('re_assessment','Re-assessment'),
         ('extension_scope','Extension Scope'),
         ('on_site_clearance','On-site clearance of findings visit'),
         ('others','Other (specify)')], 
        string='Type of Assessment',
        required=True)

    others = fields.Char(
        string='Others')

    accreditation_standard = fields.Selection(
        ISO_STANDARD,
        string='Accreditation Standard',
        required=True)

    program_type = fields.Char(
        string='Program Type')

    scope = fields.Char(
        string='Scope/Field',
        required=True)

    previous_corrective_actions = fields.Selection(
        [('cleared','Cleared'),('not_cleared','Not Cleared')],
        string='Previous Corrective Actions')

    previous_corrective_action_comments = fields.Text(
        string='Comments')

    num_of_conformites = fields.Integer(
        string='Number of non-conformities')

    unconditional_accreditation = fields.Boolean(
        string='Unconditional accreditation/renewal of accreditation to be granted')

    accreditation_cleared = fields.Boolean(
        string='Accreditation/renewal of acreditation to be deferred until all non-conformances is not recommended')

    accreditation_recommended = fields.Boolean(
        string='Accreditation/renewal of accreditation is not recommended')

    re_assessment_only = fields.Boolean(
        string="""For re-assessment only: Suspension of accreditation status or part thereof. \n<b>Note: </b>
        The period of suspension shall not extend beyond the date of expiry of the Certificate of Accreditation""")

    all_corrective_actions = fields.Boolean(
        string='All corrective actions have been implemented')

    corrective_actions = fields.Boolean(
        string='Corrective actions have not all been implemented/effectively implemented')

    nominated_representative_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Nominated Representative (NR)')

    surveillance_report_witness_ids = fields.One2many(
        comodel_name='ninas.surveillance.report.witness',
        inverse_name='surveillance_report_id',
        string='Surveillance Report Witnesses')

    brief_conclusion = fields.Text(
        string='Brief Conclusion')

    initial_assessment_date = fields.Date(
        string='Initial Assessments, extension of scopes')

    re_assessment_date = fields.Date(
        string='Re-assessment visits')

    state = fields.Selection(
        [('new','New'),('refused','Refused'),('lead_approved','Lead Approved'), 
        ('director_approved','Director Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')

    def lead_approve(self):
        self.write({'state':'lead_approved'})

    def director_approve(self):
        self.write({'state':'director_approved'})

    def draft(self):
        self.write({'state':'new'})

    def refuse(self):
        self.write({'state':'refused'})



    def create(self, values):
        #calculate duration with start_date and end_date
        report = super(SurveillanceReport, self).create(values)
        return report

    def write(self, values):
        #calculate duration with start_date and end_date
        super(SurveillanceReport, self).write(values)
        return True


class SurveillanceReportWitness(models.Model):
    _name = 'ninas.surveillance.report.witness'

    surveillance_report_id = fields.Many2one(
        comodel_name='ninas.surveillance.report',
        string='Surveillance Report', ondelete='cascade')

    witness_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Witnessed technical analyst / mythologist')

    witness_scope = fields.Text(
        string='Witness scopes')
