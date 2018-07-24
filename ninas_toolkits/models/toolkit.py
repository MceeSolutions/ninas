# -*- coding: utf-8 -*-
# © 2018 Intelligenti <http://www.intelligenti.io>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, SUPERUSER_ID
import time
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from pandas.tseries.offsets import BDay
from odoo.exceptions import ValidationError


ISO_STANDARD = [('iso1','ISO1'),('iso2','ISO2')]
COMPLIANCE = [('C','Compliance'),('NC', 'Non-Compliance'),('NA','Not Applicable')]
COMPLIANCE_STANDARD = [('C','Compliance'),('NC', 'Non-Compliance')]
KEYS = [('5','Excellent'),('4','Very Good'), ('3','Good'),('2','Fair'),('1','Poor')]

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

class VerticalAssessmentLaboratory(models.Model):
    _name = 'ninas.vertical.assessment.lab'
    _description = 'Ninas Vertial Assessment Laboratory'
    _inherit = 'ninas.basic.toolkit.data'

    evaluation_date = fields.Date(
        string='Date of Evaluation',
        default=lambda *a: time.strftime('%Y-%m-%d'), 
        track_visibility='onchange')

    laboratory = fields.Char(
        string='Laboratory',
        track_visibility='onchange'
    )

    operation_area = fields.Char(
        string='Field / Area of Operation',
        track_visibility='onchange'
    )

    lab_representative = fields.Char(
        string='Lab Representative',
        track_visibility='onchange'
    )

    certificate_report = fields.Text(
        string='Certificate / Report',
        track_visibility='onchange'
    )

    technical_record_text_1 = fields.Selection(
        COMPLIANCE,
        string='4.13.2.1 - Raw data/original observations, calculations, derivations',
        track_visibility='onchange'
    )

    technical_record_text_2 = fields.Selection(
        COMPLIANCE,
        string='4.13.2.1 - Traceability to the person performing the test /',
        track_visibility='onchange'
    )

    technical_record_text_3 = fields.Selection(
        COMPLIANCE,
        string='4.13.2.3 - calibration Records permanent, corrections legible and',
        track_visibility='onchange'
    )

    technical_record_text_4 = fields.Selection(
        COMPLIANCE,
        string='5.4.7.1 - authorized Appropriate calculation checks. Randomly recalculate',
        track_visibility='onchange'
    )

    correctness = fields.Text(
        string='Randomly check correctness of data transfers. Laboratory’s control checks appropriate/effective.',
        track_visibility='onchange'
    )

    training_record_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.2.5 - Operator/s identified as competent for the work and is proof of competence available.',
        track_visibility='onchange'
    )

    training_record_text_2 = fields.Selection(
        COMPLIANCE,
        string='5.2.5 - Proven competent at the time that the work was performed. Appropriate method of determination ofcompetence.',
        track_visibility='onchange'
    )

    performance_capability_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.4.2 - Proof of confirmation of proper operation of standard methods',
        track_visibility='onchange'
    )

    performance_capability_text_2 = fields.Selection(
        COMPLIANCE,
        string='5.4.3 - Proof of confirmation of proper operation of laboratory developed methods',
        track_visibility='onchange'
    )

    performance_capability_text_3 = fields.Selection(
        COMPLIANCE,
        string='5.4.4 - Proof of confirmation of proper operation of non-standard methods',
        track_visibility='onchange'
    )

    performance_capability_text_4 = fields.Selection(
        COMPLIANCE,
        string='5.4.5.2 - Methods validated and availability of performance capability',
        track_visibility='onchange'
    )

    performance_capability_text_5 = fields.Selection(
        COMPLIANCE,
        string='5.4.5.3 - Capability appropriate for use. Statistical application appropriate – (e.g. where relevant significant figure or rounding off policy for final results)',
        track_visibility='onchange'
    )

    performance_capability_text_6 = fields.Selection(
        COMPLIANCE,
        string='5.4.5.6.2 - Testing laboratories – Method uncertainty or specification tolerances',
        track_visibility='onchange'
    )

    performance_capability_text_7 = fields.Selection(
        COMPLIANCE,
        string='5.4.6.1 -  Calibration laboratories – Results within MC and availability of supporting calculations',
        track_visibility='onchange'
    )

    assurance_validity_text_1 = fields.Selection(
        COMPLIANCE,
        string='a -  Indicate how the laboratory monitors results',
        track_visibility='onchange'
    )

    assurance_validity_text_2 = fields.Selection(
        COMPLIANCE,
        string='b - Appropriate and effective for ensuring the controlled performance of the accredited work',
        track_visibility='onchange'
    )

    assurance_validity_text_3 = fields.Selection(
        COMPLIANCE,
        string='c - Monitoring data suitably recorded (e.g. control charts), evaluated reviewed',
        track_visibility='onchange'
    )

    assurance_validity_text_4 = fields.Selection(
        COMPLIANCE,
        string='d - Effective control limits or tolerances been established',
        track_visibility='onchange'
    )

    assurance_validity_text_5 = fields.Selection(
        COMPLIANCE,
        string='e - Evidence of actions implemented when breaches have occurred',
        track_visibility='onchange'
    )

    proficiency_testing_text_1 = fields.Selection(
        COMPLIANCE,
        string='Appropriateness for the work performed',
        track_visibility='onchange'
    )

    proficiency_testing_text_2 = fields.Selection(
        COMPLIANCE,
        string='Evaluate results – action on anomalies or outliers',
        track_visibility='onchange'
    )

    additional_comments = fields.Text(
        string='Additional Comments',
        track_visibility='onchange'
    )

    calibration_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.5.2 Appropriateness of calibration and verification programmes, cover operating range',
        track_visibility='onchange'
    )
    calibration_text_2 = fields.Selection(
        COMPLIANCE,
        string='5.5.8 Calibration status',
        track_visibility='onchange'
    )
    calibration_text_3 = fields.Selection(
        COMPLIANCE,
        string='5.5.5 Records of calibration and verification complete, tolerances appropriate',
        track_visibility='onchange'
    )
    calibration_text_4 = fields.Selection(
        COMPLIANCE,
        string='5.5.10 In-house verification techniques sufficient to ensure validity of calibration',
        track_visibility='onchange'
    )
    calibration_text_5 = fields.Selection(
        COMPLIANCE,
        string='5.5.11 Suitable application of correction factors',
        track_visibility='onchange'
    )
    calibration_text_6 = fields.Selection(
        COMPLIANCE,
        string='5.6.2.1 Traceability to national standards',
        track_visibility='onchange'
    )
    calibration_text_7 = fields.Selection(
        COMPLIANCE,
        string='5.6.2.2 Traceability to appropriate measurement standards',
        track_visibility='onchange'
    )
    calibration_text_8 = fields.Selection(
        COMPLIANCE,
        string='5.6.2.1.1 External calibration services used – demonstrated competence, measurement capability and traceability, certificates contain measurement results, measurement uncertainty',
        track_visibility='onchange'
    )

    calibration_text_9 = fields.Selection(
        COMPLIANCE,
        string='5.6.3.1 Reference standards traceable calibration, not invalidate performance when used',
        track_visibility='onchange'
    )

    calibration_text_10 = fields.Selection(
        COMPLIANCE,
        string='5.6.3.2 Reference materials – traceable, SI, CRMs, Internal reference materials – checked',
        track_visibility='onchange'
    )
    
    calibration_text_11 = fields.Selection(
        COMPLIANCE,
        string='5.6.3.3 Intermediated checks – reference, primary, transfer and working standards',
        track_visibility='onchange'
    )

    calibration_text_12 = fields.Selection(
        COMPLIANCE,
        string='5.5 / 5.6 Equipment maintenance and operation',
        track_visibility='onchange'
    )

    calibration_text_13 = fields.Selection(
        COMPLIANCE,
        string='5.5.3 Instructions on use and maintenance',
        track_visibility='onchange'
    )

    calibration_text_14 = fields.Selection(
        COMPLIANCE,
        string='5.5.5 Records complete',
        track_visibility='onchange'
    )

    calibration_text_15 = fields.Selection(
        COMPLIANCE,
        string='5.5.6 - 5.5.3.4 Handling / transport / storage / use to prevent contamination/deterioration of –equipment and standard/ reference materials',
        track_visibility='onchange'
    )

    calibration_comments = fields.Text(
        string='Additional / General Comments',
        track_visibility='onchange'
    )

    accomodation_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.3.1 - Critical areas of accommodation/environmental control which would affect the performance of the accredited work. (e.g. Special room, Dust filtration, Positive pressure, Lighting, Static, Electric screening, Air lock entrance, Cleanliness, Vibration level, EMI, Dedicated Earth, etc.)',
        track_visibility='onchange'
    )

    accomodation_text_2 = fields.Selection(
        COMPLIANCE,
        string='5.3.3 -  Monitored, controlled and auctioned when required',
        track_visibility='onchange'
    )

    accomodation_text_3 = fields.Selection(
        COMPLIANCE,
        string='5.3.4 -  Effective segregation of tests/ equipment/ standards and consumables Adequate storage areas',
        track_visibility='onchange'
    )

    accomodation_comments = fields.Text(
        string='Accomodation Comments',
        track_visibility='onchange'
    )

    purchasing_text_1 = fields.Selection(
        COMPLIANCE,
        string='4.6.2 - Supplies verified prior to use to meet the quality criteria as required for the methods accredited',
        track_visibility='onchange'
    )

    purchasing_text_2 = fields.Selection(
        COMPLIANCE,
        string='4.6 - System ensure supplies for the uninterrupted performance of work documented and effective – e.g. stock control, requisitioning, ordering and storage',
        track_visibility='onchange'
    )

    purchasing_comments = fields.Text(
        string='Purchasing Comments',
        track_visibility='onchange'
    )

    calibration_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.8.2 - Uniquely identified, ensure that there can be no confusion regarding the identify at any time',
        track_visibility='onchange'
    )

    calibration_text_2 = fields.Selection(
        COMPLIANCE,
        string='5.8.3 - Condition of the item noted, where applicable',
        track_visibility='onchange'
    )

    calibration_text_3 = fields.Selection(
        COMPLIANCE,
        string='5.8.4 - System avoid deterioration/ damage during storage, handling, preparation, and calibration or test',
        track_visibility='onchange'
    )

    calibration_comments = fields.Text(
        string='Calibration Comments',
        track_visibility='onchange'
    )

    report_text_1 = fields.Selection(
        COMPLIANCE,
        string='5.10 - If not full report, written agreement and all data available in laboratory',
        track_visibility='onchange'
    )

    report_comments = fields.Text(
        string='Report Comments',
        track_visibility='onchange'
    )

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



class ProficiencyTesting(models.Model):
    _name = 'ninas.proficiency.testing'
    _description = 'NiNAS Proficiency Testing'
    _inherit='ninas.basic.toolkit.data'

    evaluation_date = fields.Date(
        string='Date of Evaluation',
        track_visibility='onchange'
    )

    laboratory = fields.Char(
        string='Laboratory',
        track_visibility='onchange'
    )

    laboratory_representative = fields.Char(
        string='Laboratory Representative',
        track_visibility='onchange'
    )

    operation_field = fields.Char(
        string='Area/field of operation',
        track_visibility='onchange'
    )

    proficiency_testing_text = fields.Selection(
        COMPLIANCE_STANDARD,
        string='5.6.3 - Proficiency testing: Has the laboratory participated in Proficiency Testing (PT) or Inter-laboratory Comparisons for all parameters on the Schedule of Accreditation?',
        track_visibility='onchange'
    )

    proficiency_details_text_1 = fields.Text(string='Provide details of the PT/ILC/EQA activity that the laboratory has participated in, particularly since the application/last assessment. Issues to be addressed include: what was covered; were the results satisfactory; who arranged the PT/ILAC/EQA:',
        track_visibility='onchange')
    proficiency_details_text_2 = fields.Text(string='If the laboratory has not participated in PT activities because PT is either not practical or none existent.',
        track_visibility='onchange')
    proficiency_details_text_3 = fields.Text(string='1. List the tests not covered by PT/ILC',
        track_visibility='onchange')
    proficiency_details_text_4 = fields.Text(string='2. What are the reasons for not participating in PT/ILC activities, and are they valid verifiable reasons?',
        track_visibility='onchange')
    proficiency_details_text_5 = fields.Text(string='3. Have suitable alternative activities been proposed by the laboratory and agreed to by NiNAS?',
        track_visibility='onchange')
    proficiency_details_text_6 = fields.Text(string='4. Which alternative activities are being used by the laboratory?',
        track_visibility='onchange')
    proficiency_details_text_7 = fields.Text(string='5. Comment on the suitability of the alternative activities used in assuring the quality of Test and Calibration results',
        track_visibility='onchange')
    proficiency_details_text_8 = fields.Text(string='6. Appropriateness of PT/ILC/EQA Activity: How are the following addressed/implemented?',
        track_visibility='onchange')
    proficiency_details_text_9 = fields.Text(string='7. Is the amount of PT/ILC/EQA activity (or alternative activities) appropriate to the volume and associated risk for the testing and or calibration activities of the laboratory?',
        track_visibility='onchange')
    proficiency_comments = fields.Text(string='Comment on Appropriateness',
        track_visibility='onchange')
    proficiency_details_text_10 = fields.Text(string='Analysis of results of PT/ILC/EQA testing: How are the following addressed/implemented? Has the laboratory analyzed the results of the PT/ILC/EQA results (or alternatives) and have appropriate steps been taken when results are not satisfactory (En>1, or Z score>3)',
        track_visibility='onchange')
    proficiency_details_text_11 = fields.Text(string='Comment on analysis of results, provide information on what actions the laboratory has taken where the results were found to be unsatisfactory:',
        track_visibility='onchange')
    proficiency_details_text_12 = fields.Text(string='Is the laboratory experiencing any problems with participating in PT/ILC/EQA?',
        track_visibility='onchange')
    proficiency_details_text_13 = fields.Text(string='What difficulties, if any, has the laboratory experienced in participation? Are there any issues that need to be referred to the technical committee?',
        track_visibility='onchange')
    proficiency_details_text_14 = fields.Text(string='What difficulties, if any, has the laboratory experienced in participation? Are there any issues that need to be referred to the technical committee?',
        track_visibility='onchange')
    
    calibration_text_1 = fields.Text(string='1. Has the laboratory prepared and implemented an activity plan that indicated how and when PT and/or ILC activities are to be implemented for the next 5 years?',
        track_visibility='onchange')
    calibration_text_2 = fields.Text(string='2. Does the activity plan cover all the major parameters and instruments listed on the laboratory’s schedule of accreditation?',
        track_visibility='onchange')
    
    medical_text_1 = fields.Text(string='1. Has the laboratory prepared and implemented a plan that indicates how and when PT/ILC/EQA activities are to be implemented for at least 2 accreditation cycles ie, the activity schedule for the past accreditation cycle (where possible) and the plan for the subsequent accreditation cycle?',
        track_visibility='onchange')
    medical_text_2 = fields.Text(string='2. Does the activity plan cover all accredited activities listed on the laboratory’s schedule of accreditation, and in a period not exceeding one accreditation cycle?',
        track_visibility='onchange')
    medical_comments = fields.Text(string='Comment on activity pan, does it cover the full scope of accredited activities?',
        track_visibility='onchange')
    calibration_testing_comments = fields.Text(string='Comment on ILC/PT/EQA reports received. Where requirements have not been met, what was missing or incorrectly reported?',
        track_visibility='onchange')
    
    review_date = fields.Date(string='Reviewed Date', track_visibility='onchange')
    
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


class AssessmentConfirmation(models.Model):
    _name = 'ninas.assessment.confirmation'
    _description = 'Ninas Assessment Confirmation'
    _inherit = 'ninas.basic.toolkit.data'
    _sql_constraints = [
        ('date_check', "CHECK ( (start_date <= end_date))", "The start date must be anterior to the end date.")
    ]

    start_date = fields.Date(
        string='Start Date',
        track_visibility='onchange',
        required=True
    )

    end_date = fields.Date(
        string='End Date',
        track_visibility='onchange',
        required=True
    )

    days = fields.Integer(
        string='Day(s)',
        track_visibility='onchange',
    )

    related_days = fields.Integer(
        related='days'
    )

    related_start_date = fields.Date(
        related='start_date'
    )

    related_end_date = fields.Date(
        related='end_date'
    )

    confirmation_assessor_ids = fields.One2many(
        comodel_name = 'ninas.assessment.confirmation.assessor',
        inverse_name = 'assessment_confirmation_id',
        string='Confirmation Assessor(s)'
    )

    approval_date = fields.Date(string='Approval Date', track_visibility='onchange')
    
    state = fields.Selection(
        [('new','New'),('refused','Refused'),('approved','Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')

    def approve(self):
        self.write({'state':'approved', 'approval_date':time.strftime('%Y-%m-%d')})

    def draft(self):
        self.write({'state':'new'})

    def refuse(self):
        self.write({'state':'refused'})


    @api.model
    def create(self, values):
        confirmation = super(AssessmentConfirmation, self).create(values)
        confirmation.days = confirmation.get_days(confirmation.start_date, confirmation.end_date) 
        return confirmation
    
    @api.multi
    def write(self, values):
        super(AssessmentConfirmation, self).write(values)
        if 'start_date' in values.keys():
            start_date = values.get('start_date')
        else:
            start_date = self.start_date
        if 'end_date' in values.keys():
            end_date = values.get('end_date')
        else:
            end_date = self.end_date
        values = {}
        values.update({'days':self.get_days(start_date, end_date)})
        super(AssessmentConfirmation, self).write(values)
        return True

    def get_days(self, start_date, end_date):
        start_date = start_date.split('-')
        end_date = end_date.split('-')
        d0 = date(int(start_date[0]), int(start_date[1]), int(start_date[2]))
        d1 = date(int(end_date[0]), int(end_date[1]), int(end_date[2]))
        delta = d1 - d0
        return delta.days + 1

class AssessmentConfirmationAssessor(models.Model):
    _name = 'ninas.assessment.confirmation.assessor'
    _description = 'Ninas Assessment Confirmation Assessors'
    _inherit = ['mail.thread']

    capacity = fields.Selection(
        [('lead_assessor','Lead Assessor'), ('technical_assessor_trainee','Technical Assessor (Trainee)')],
        string='Capacity', 
        required=True, 
        track_visibility='onchange'
    )

    name = fields.Many2one(
        comodel_name = 'hr.employee',
        string='Name',
        required=True,
        track_visibility='onchange'
    )

    employed_by = fields.Selection(
        [('ninas','NiNAS')],
        string='Employed By', 
        required=True,
        default='ninas',
        track_visibility='onchange'
    )

    scope_assess = fields.Char(
        string='Scopes to be assess',
        track_visibility='onchange',
        required=True
    )

    days = fields.Integer(
        related='assessment_confirmation_id.days',
        track_visibility='onchange'
    )

    assessment_confirmation_id = fields.Many2one(
        comodel_name = 'ninas.assessment.confirmation',
        string='Assessment Confirmation',
        ondelete='cascade',
        track_visibility='onchange'
    )

    assessment_option = fields.Selection(
        [('institution_representative','Institution Representative'),
        ('assessor_expert','Assessor/Expert'),
        ('observer','Observer'),
        ('trainee_mentor','Trainee Mentor/Monitor')],
        string='Assessment Option',
        track_visibility='onchange'
    )

    state = fields.Selection(
        [('pending','Pending'),('declined','Declined'),('accepted','Accepted')],
        string='Status',
        default='pending',
        track_visibility='onchange')
    
    accepted_date = fields.Date(
        string='Accepted Date',
        track_visibility='onchange'
    )

    @api.model
    def create(self, values):
        assessor = super(AssessmentConfirmationAssessor, self).create(values)
        partner_id = assessor.name.user_id.partner_id.id 
        reg = { 
            'res_id': assessor.id, 
            'res_model': 'ninas.assessment.confirmation.assessor', 
            'partner_id': partner_id,
        } 
        if not self.env['mail.followers'].search([('res_id','=',assessor.id),('res_model','=','crm.lead'),('partner_id','=',partner_id)]): 
            self.env['mail.followers'].create(reg)
        return assessor

    def accept(self):
        if self.env.user.id != SUPERUSER_ID and self.name.user_id.id != self.env.user.id:
            raise ValidationError('You cannot accept this as you are not the assessor for this document!') 
        if not self.assessment_option:
            raise ValidationError('You must select an assessment option!')         
        self.write({'state':'accepted', 'accepted_date':time.strftime('%Y-%m-%d')})

    def draft(self):
        self.write({'state':'pending'})

    def decline(self):
        self.write({'state':'declined'})


class AppraisalReportLeadAssessor(models.Model):
    _name = 'ninas.appraisal.report.lead.assessor'
    _description = 'NiNAS Appraisal Report Lead Assessor'
    _inherit = 'ninas.basic.toolkit.data'

    assessment_type = fields.Selection(
        [('initial','Initial'), ('surveillance','Surveillance'), ('extension','Extension'),('re','Re-')],
        string='Type of Assessment',
        required=True,
        track_visibility='onchange'
    )

    assessment_date = fields.Date(
        string='Date of Assessment',
        track_visibility='onchange',
        default = lambda *a: time.strftime('%Y-%m-%d'),
        required=True,
    )

    standard_used = fields.Char(
        string='Guide / Standard used',
        required=True,
        track_visibility='onchange'
    )

    state = fields.Selection(
        [('new','Draft'),('refused','Refused'),('approved','Approved'), ('director_approved','Director Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')

    personal_attributes_criteria_1 = fields.Selection(KEYS,string='1.1 - Ethical, i.e. fair, truthful, sincere, honest and discrete.', track_visibility='onchange')
    personal_attributes_criteria_comments_1 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_2 = fields.Selection(KEYS,string='1.2 - Open-minded, i.e. willing to consider alternative ideas or points of view.', track_visibility='onchange')
    personal_attributes_criteria_comments_2 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_3 = fields.Selection(KEYS,string='1.3 - Diplomatic, i.e. tactful in dealing with people.', track_visibility='onchange')
    personal_attributes_criteria_comments_3 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_4 = fields.Selection(KEYS,string='1.4 - Observant, i.e. actively aware of physical surroundings and activities.', track_visibility='onchange')
    personal_attributes_criteria_comments_4 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_5 = fields.Selection(KEYS,string='1.5 - Perceptive, i.e. instinctively aware of and able to understand situations.', track_visibility='onchange')
    personal_attributes_criteria_comments_5 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_6 = fields.Selection(KEYS,string='1.6 - Versatile, i.e. adjusts readily to different situations.', track_visibility='onchange')
    personal_attributes_criteria_comments_6 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_7 = fields.Selection(KEYS,string='1.7 - Tenacious, i.e. persistent, focused on achieving objectives.', track_visibility='onchange')
    personal_attributes_criteria_comments_7 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_8 = fields.Selection(KEYS,string='1.8 - Decisive, i.e. reaches timely conclusions based on logical reasoning and analysis.', track_visibility='onchange')
    personal_attributes_criteria_comments_8 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_9 = fields.Selection(KEYS,string='1.9 - Self-reliant, i.e. acts and functions independently while interacting effectively with others.', track_visibility='onchange')
    personal_attributes_criteria_comments_9 = fields.Char(string='Comments', track_visibility='onchange')
    personal_attributes_criteria_10 = fields.Selection(KEYS,string='1.10 - Effective in communication with others.', track_visibility='onchange')
    personal_attributes_criteria_comments_10 = fields.Char(string='Comments', track_visibility='onchange')

    knowledge_assessment_skill_1 = fields.Selection(KEYS,string='2.1 - Apply assessment principles, procedures and techniques.', track_visibility='onchange')
    knowledge_assessment_skill_comments_1 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_2 = fields.Selection(KEYS,string='2.2 - Plan and organize the work effectively.', track_visibility='onchange')
    knowledge_assessment_skill_comments_2 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_3 = fields.Selection(KEYS,string='2.3 - Conduct the assessment within the agreed time schedule.', track_visibility='onchange')
    knowledge_assessment_skill_comments_3 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_4 = fields.Selection(KEYS,string='2.4 - Prioritize and focus on matters of significance.', track_visibility='onchange')
    knowledge_assessment_skill_comments_4 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_5 = fields.Selection(KEYS,string='2.5 - Collect information through effective interviewing, listening, observing and reviewing documents, records and data.', track_visibility='onchange')
    knowledge_assessment_skill_comments_5 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_6 = fields.Selection(KEYS,string='2.6 - Understand the appropriateness and consequences of using sampling techniques for assessment.', track_visibility='onchange')
    knowledge_assessment_skill_comments_6 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_7 = fields.Selection(KEYS,string='2.7 - Verify the accuracy of collected information.', track_visibility='onchange')
    knowledge_assessment_skill_comments_7 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_8 = fields.Selection(KEYS,string='2.8 - Confirm the sufficiency and appropriateness of assessment evidence to support assessment findings and conclusions.', track_visibility='onchange')
    knowledge_assessment_skill_comments_8 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_9 = fields.Selection(KEYS,string='2.9 - Prepare assessment reports', track_visibility='onchange')
    knowledge_assessment_skill_comments_9 = fields.Char(string='Comments', track_visibility='onchange')
    knowledge_assessment_skill_10 = fields.Selection(KEYS,string='2.10 - Maintain the confidentiality and security of information.', track_visibility='onchange')
    knowledge_assessment_skill_comments_10 = fields.Char(string='Comments', track_visibility='onchange')
    
    skill_assessment_leadership_1 = fields.Selection(KEYS,string='3.1 - Plan the assessment and make effective use of resources during the assessment.', track_visibility='onchange')
    skill_assessment_leadership_comments_1 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_leadership_2 = fields.Selection(KEYS,string='3.2 - Represent the assessment team in communications with the CAB’s personnel.', track_visibility='onchange')
    skill_assessment_leadership_comments_2 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_leadership_3 = fields.Selection(KEYS,string='3.3 - Organize and direct assessment team members.', track_visibility='onchange')
    skill_assessment_leadership_comments_3 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_leadership_4 = fields.Selection(KEYS,string='3.4 - Lead the assessment team to reach the assessment conclusion.', track_visibility='onchange')
    skill_assessment_leadership_comments_4 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_leadership_5 = fields.Selection(KEYS,string='3.5 - Prevent and resolve conflict.', track_visibility='onchange')
    skill_assessment_leadership_comments_5 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_leadership_6 = fields.Selection(KEYS,string='3.6 - Prepare and complete the assessment report.', track_visibility='onchange')
    skill_assessment_leadership_comments_6 = fields.Char(string='Comments', track_visibility='onchange')
    
    skill_assessment_reporting_1 = fields.Selection(KEYS,string='4.1 - Interpretation of requirements', track_visibility='onchange')
    skill_assessment_reporting_comments_1 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_reporting_2 = fields.Selection(KEYS,string='4.2 - Documentation of evidence', track_visibility='onchange')
    skill_assessment_reporting_comments_2 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_reporting_3 = fields.Selection(KEYS,string='4.3 - Clarity of writing', track_visibility='onchange')
    skill_assessment_reporting_comments_3 = fields.Char(string='Comments', track_visibility='onchange')
    skill_assessment_reporting_4 = fields.Selection(KEYS,string='4.4 - Timeliness of delivery', track_visibility='onchange')
    skill_assessment_reporting_comments_4 = fields.Char(string='Comments', track_visibility='onchange')
    
    recommendations = fields.Text(string='Recommendations', track_visibility='onchange')
    approval_date = fields.Date(string='Approval Date', track_visibility='onchange')
    director_approval_date = fields.Date(string='Director Approval Date', track_visibility='onchange')

    def approve(self):         
        self.write({'state':'approved', 'approval_date':time.strftime('%Y-%m-%d')})
    
    def director_approve(self):         
        self.write({'state':'director_approved', 'director_approval_date':time.strftime('%Y-%m-%d')})

    def draft(self):
        self.write({'state':'new'})

    def refuse(self):
        self.write({'state':'refused'})