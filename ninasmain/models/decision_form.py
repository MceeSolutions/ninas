# _*_ coding: utf-8 _*_
# @author Atsen
# Date : 02/08/18

from odoo import fields, models
import datetime

class DecisionForm(models.Model):
    _name = 'ninas.decision_form'
    _description = 'Decision Form'

    #this should pull the application info (rep, assessor, institution)
    ref = fields.Char(
        string='Reference No.',
        required=1)

    #link to actual employee_id
    assessor_id = fields.Char(
        #comodel_name = 'hr.employee',
        string ='Assessor Name',
        readonly=1)

    representative = fields.Char(
        string='Name of Institution Representative',
        readonly=1)

    scope = fields.Char(
        string='Accreditation Scope',
        readonly=1)

    institution_name = fields.Char(
        string='Name of Institution',
        readonly=1)

    assess_type = fields.Char(
        string ='Type of Assessment')

    assessment_date = fields.Date(
        string = 'Assessment Date',
        required=1)

    la_recommendation = fields.Char(
        string="Lead Assessor's Recommendation",
        required=1)

    aac_recommendation = fields.Char(
        string="AAC Recommendation",
        required=1)

    da_recommendation = fields.Char(
        string="Director of Accreditation's Recommendation",
        required=1)

    #today's date on change (save)
    date = fields.Date(
        string= 'Date')

    ceo = fields.Selection(
        [('1','Unconditional accreditation/renewal of accreditation to be granted'),
        ('2','Accreditation/renewal of accreditation to be deferred until all non-conformances have been cleared'),
        ('3','Accreditation/renewal of accreditation is not recommended'),
        ('4','For re-assessment only: Suspension of accreditation status or part thereof')],
        string = 'CEO')

    note = fields.Char(
        default='The period of suspension shall not extend beyond the date of expiry of the Certificate of Accreditation',
        readonly=1)
    
    