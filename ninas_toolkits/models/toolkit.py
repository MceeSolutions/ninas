# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
#from pandas.tseries.offsets import BDay


ISO_STANDARD = [('iso1','ISO1'),('iso2','ISO2')]



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
        string='Identification Description',
        track_visibility='onchange')

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
    _sql_constraints = [
        ('date_check', "CHECK ( (start_date <= end_date))", "The start date must be anterior to the end date.")
    ]

    location = fields.Char(
        string='Location',
        track_visibility='onchange')

    start_date = fields.Date(
        string='Start Date',
        required=True,
        default=lambda *a: time.strftime('%Y-%m-%d'),
        track_visibility='onchange')

    end_date = fields.Date(
        string='End Date',
        required=True,
        track_visibility='onchange')

    duration = fields.Integer(
        string='Duration (days)',
        track_visibility='onchange')

    assessment_type = fields.Selection(
        [('initial_assessment','Initial Assessment'),
         ('re_assessment','Re-assessment'),
         ('extension_scope','Extension Scope'),
         ('on_site_clearance','On-site clearance of findings visit'),
         ('others','Other (specify)')], 
        string='Type of Assessment',
        required=True,
        track_visibility='onchange')

    others = fields.Char(
        string='Others',
        track_visibility='onchange')

    accreditation_standard = fields.Selection(
        ISO_STANDARD,
        string='Accreditation Standard',
        required=True,
        track_visibility='onchange')

    program_type = fields.Char(
        string='Program Type',
        track_visibility='onchange')

    scope = fields.Char(
        string='Scope/Field',
        required=True,
        track_visibility='onchange')

    previous_corrective_actions = fields.Selection(
        [('cleared','Cleared'),('not_cleared','Not Cleared')],
        string='Previous Corrective Actions',
        track_visibility='onchange')

    previous_corrective_action_comments = fields.Text(
        string='Comments',
        track_visibility='onchange')

    num_of_conformites = fields.Integer(
        string='Number of non-conformities',
        track_visibility='onchange')

    unconditional_accreditation = fields.Boolean(
        string='Unconditional accreditation/renewal of accreditation to be granted',
        track_visibility='onchange')

    accreditation_cleared = fields.Boolean(
        string='Accreditation/renewal of acreditation to be deferred until all non-conformances is not recommended',
        track_visibility='onchange')

    accreditation_recommended = fields.Boolean(
        string='Accreditation/renewal of accreditation is not recommended',
        track_visibility='onchange')

    re_assessment_only = fields.Boolean(
        string="""For re-assessment only: Suspension of accreditation status or part thereof. \n<b>Note: </b>
        The period of suspension shall not extend beyond the date of expiry of the Certificate of Accreditation""",
        track_visibility='onchange')

    all_corrective_actions = fields.Boolean(
        string='All corrective actions have been implemented',
        track_visibility='onchange')

    corrective_actions = fields.Boolean(
        string='Corrective actions have not all been implemented/effectively implemented',
        track_visibility='onchange')

    nominated_representative_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Nominated Representative (NR)',
        track_visibility='onchange')

    surveillance_report_witness_ids = fields.One2many(
        comodel_name='ninas.surveillance.report.witness',
        inverse_name='surveillance_report_id',
        string='Surveillance Report Witnesses',
        track_visibility='onchange')

    brief_conclusion = fields.Text(
        string='Brief Conclusion',
        track_visibility='onchange')

    initial_assessment_date = fields.Date(
        string='Initial Assessments, extension of scopes',
        track_visibility='onchange')

    re_assessment_date = fields.Date(
        string='Re-assessment visits',
        track_visibility='onchange')

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


    def compute_duration(self, values):
        duration = 0
        start_date = self.start_date
        end_date = self.end_date
        if 'start_date' in values.keys():
            start_date = values['start_date']
        if 'end_date' in values.keys():
            end_date = values['end_date']
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
        duration = abs((end_date-start_date).days) + 1
        return duration

    @api.model
    def create(self, values):
        duration = self.compute_duration(values)
        values.update({'duration':duration})
        report = super(SurveillanceReport, self).create(values)
        return report

    @api.multi
    def write(self, values):
        duration = self.compute_duration(values)
        values.update({'duration':duration})
        super(SurveillanceReport, self).write(values)
        return True


    @api.onchange('start_date')
    def update_assessment_date(self):
        if self.start_date:
            start_date = datetime.strptime(self.start_date, '%Y-%m-%d')
            self.initial_assessment_date =  start_date + relativedelta(months=+3)
            days = ((start_date + BDay(25)) - start_date).days
            self.re_assessment_date =  start_date + relativedelta(days=+days)

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


class DocumentReviewReport(models.Model):
    _name='ninas.document.review.report'
    _description='Ninas Document Review Report'
    _inherit='ninas.basic.toolkit.data'

    documentation_received = fields.Text(
        string='Documentation Received',
        track_visibility='onchange'
    )

    review_date = fields.Date(
        string='Review Date',
        track_visibility='onchange'
    )

    recommendations = fields.Text(
        string='Recommendations',
        track_visibility='onchange'
    )

    accreditation_standard = fields.Selection(
        ISO_STANDARD,
        string='Accreditation Standard',
        required=True,
        track_visibility='onchange')
    
    report_requirement_ids = fields.One2many(
        comodel_name='ninas.document.review.report.requirement',
        inverse_name='review_report_id',
        string='Report Requirements',
        track_visibility='onchange'
    )

    state = fields.Selection(
        [('new','New'),('refused','Refused'),('reviewed','Reviewed')],
        string='Status',
        default='new',
        track_visibility='onchange')

    def review(self):
        self.write({'state':'reviewed', 'review_date':time.strftime('%Y-%m-%d')})

    def draft(self):
        self.write({'state':'new'})

    def refuse(self):
        self.write({'state':'refused'})

class DocumentReviewReportRequirement(models.Model):
    _name='ninas.document.review.report.requirement'
    _description='Ninas Document Review Report Requirements'
    _order = 'code ASC'

    name = fields.Many2one(
        comodel_name='ninas.document.review.config',
        string='Title',
        required=True
    )

    code = fields.Char(
        string='Code',
        required=True
    )

    title_ids = fields.Many2many(
        related='name.title_ids'
    )

    review_report_id = fields.Many2one(
        comodel_name='ninas.document.review.report',
        string='Review Report',
        ondelete='cascade'
    )

    requirement_section_ids = fields.One2many(
        comodel_name='ninas.document.review.report.requirement.section',
        inverse_name='requirement_id',
        string='Requirement Subsections'
    )

class DocumentReviewReportRequirementSection(models.Model):
    _name = 'ninas.document.review.report.requirement.section'
    _description = 'Ninas Document Review Report Requirement Sections'
    _order = 'code ASC'

    code = fields.Char(
        string='Code',
        required=True
    )

    name = fields.Many2one(
        comodel_name='ninas.document.review.subconfig',
        string='Title',
        required=True
    )

    requirement_id = fields.Many2one(
        comodel_name='ninas.document.review.report.requirement',
        string='Document Review Report Requirement',
        ondelete='cascade'
    )

    subsection_ids = fields.One2many(
        comodel_name='ninas.document.review.report.requirement.subsection',
        inverse_name='section_id',
        string='Subsections'
    )

class DocumentReviewReportRequirementSubSection(models.Model):
    _name = 'ninas.document.review.report.requirement.subsection'
    _description = 'Ninas Document Review Report Requirement Subsections'
    _order = 'code ASC'

    code = fields.Char(
        string='Code',
        required=True
    )

    name = fields.Text(
        string='Description',
        required=True
    )

    section_id = fields.Many2one(
        comodel_name='ninas.document.review.report.requirement.section',
        string='Document Review Report Requirement Section',
        ondelete='cascade'
    )

class DocumentReviewReportConfig(models.Model):
    _name = 'ninas.document.review.config'
    _description = 'Ninas Document Review Config'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Title',
        track_visibility='onchange'
    )

    title_ids = fields.Many2many(
        comodel_name='ninas.document.review.subconfig',
        relation='ninas_document_review_subconfig_rel',
        column1='title',
        column2='sub_title',
        string='Sub Titles',
        track_visibility='onchange'
    )

class DocumentReviewReportSubConfig(models.Model):
    _name = 'ninas.document.review.subconfig'
    _description = 'Ninas Document Review Subconfig'

    name = fields.Char(
        string='Title',
        track_visibility='onchange'
    )

