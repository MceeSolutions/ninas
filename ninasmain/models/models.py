# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18
import datetime

from datetime import date, timedelta
from odoo import api, fields, models


class Employee(models.Model):
    _inherit = 'hr.employee'

    fname = fields.Char(string='First Name')
    lname = fields.Char(string='Last Name')
    address = fields.Char(string='street address')
    unit = fields.Char(string='Apartment Unit')
    relationship = fields.Char(string='Relationship')
    telphone = fields.Char(string='Primary Phone')
    phone_id = fields.Char(string='Alternate Phone')
    city = fields.Char(
        string='City')
    state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state')
    zip_code = fields.Char(string='Zip Code')
    email = fields.Char(string='email')
    officail_id = fields.Char(string='Official ID Card')
    spouse_name = fields.Char(string='Spouse Name')
    spouse_employer = fields.Char(string='Spouse Employer')
    spouse_phone = fields.Char(string='Spouse Phone')
    title = fields.Char(string='Title')
    employee = fields.Char(string='Employee ID')
    start_date = fields.Date(string='Start Date')
    salary = fields.Char(string='Salary')
    
class Holidays(models.Model):
    _name = "hr.holidays"
    _inherit = 'hr.holidays'
    

    assigned_to = fields.Many2one(
        comodel_name="hr.employee",
        string='Duties Assigned To', required=True)
    title = fields.Char(string='Title Name')
    agency = fields.Selection(
        [('unido','UNIDO'),('other', 'Others')],
        string='Agency',
        default='unido')
    planned_leave = fields.Selection(
        [('yes','Yes'),('no', 'No')],
        string='Planned Leave')
    
    
class LoanRequest(models.Model):
    _name = 'loan.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'),('reject','Rejected'), ('validate','Validated')],
        string='Status',
        default='new',
        track_visibility='onchange')
    name = fields.Many2one(
        comodel_name="hr.employee",
        string='Person Requesting Loan', required=True)
    purpose = fields.Char(
        string='Purpose of Loan')
    terms_ofloan = fields.Char(
        string='Terma of Loan')
    loan_amount = fields.Char(string='Loan Amount')
    currency = fields.Selection([
        ('naira','Naira'),('dollar','Dollar')],
        string='Currency')
    total = fields.Char(
        string='Total')
    repayment = fields.Selection([
        ('soon','As soon as there is funding'),('other','Other')],
        string='Repayment')
    repayment_period = fields.Selection([
        ('oneoff','One Off'),('other','Other')],
        string='Repayment Period')
    recieved_from = fields.Many2one(
        comodel_name="hr.employee",
        string='Recieved Name', required=True)
    recieved_from_name = fields.Char(
        string='Name')
    date = fields.Date(string='Date')
    
    @api.multi
    def button_reset(self):
        self.write({'state': 'new'})
        return {}
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
    @api.multi
    def button_validate(self):
        self.write({'state': 'validate'})
        return {}    
    
class TravelRequest(models.Model):
    _name = 'travel.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO')],
        string='Status',
        default='new',
        track_visibility='onchange')
    today_date = fields.Date(
        string='Todays Date', readonly=True)
    travelrequest_no = fields.Char(
        string='Travel request Number', readonly=True, required=True, index=True, copy=False, default='New')
    traveller_email = fields.Char(
        string='Travellers Email Address')
    name = fields.Char(string='Name', required=True)
    traveller_job = fields.Char(string='Traveller Job Title')
    traveller_phone = fields.Char(string='Traveller Phone')
    traveller_department = fields.Char(string='Department')
    contact_phone = fields.Char(string='Contact Phone')
    contact_name = fields.Char(string='Contact Name')
    traveller_employee_id = fields.Char(string='Travellers Employee ID')
    purpose = fields.Text(string='Purpose and Benefit of Travel', required=True)
    ninas_employee = fields.Boolean(string='Ninas Employee')
    ninas_expert = fields.Boolean(string='Ninas Expert')
    ninas_assesor = fields.Boolean(string='Ninas Assessor')
    ninas_guest = fields.Boolean(string='Ninas Guest')
    ninas_other = fields.Char(string='Others(Describe)')
    departure_place = fields.Char(string='Departure City/State/Country', required=True,)
    destination_place = fields.Char(string='Destination City/State/Country', required=True,)
    departure_date = fields.Date(string='Departure Date', required=True,)
    return_date = fields.Date(string='Return Date', required=True,)
    rental = fields.Char(string='Rental Car Company')
    residence = fields.Char(string='Hotel Name or Type "Private Residence"')
    non_business_activity = fields.Selection([
        ('yes','Yes'),('no','No')],
        string='Will any days be spent primarily on non-business activities (Yes or No)?')
    non_business_yes = fields.Char(
        string='If yes, type the dates of non-business activity.')
    billed_to = fields.Char(
        string='Travel expenses direct-billed to NiNAS')
    reimbursed_by = fields.Char(
        string='Travel expenses to be reimbursed by NiNAS')
    total_paid = fields.Char(
        string='Total expenditures to be paid or reimbursed by NiNAS')
    thrid_party = fields.Char(
        string='Name of non-NiNAS  third party:')
    traveler_sign = fields.Many2one(
        comodel_name = 'res.users',
        string='Traveler Sign', readonly=True)
    traveler_date = fields.Date(
        string='Date', readonly=True)
    linemanager_sign = fields.Many2one(
        comodel_name = 'res.users',
        string='Line manager Sign', readonly=True)
    linemanager_date = fields.Date(
        string='Date', readonly=True)
    admin_sign = fields.Many2one(
        comodel_name = 'res.users',
        string='Admin and Finance', readonly=True)
    admin_date = fields.Date(
        string='Date')
    ceo_sign = fields.Many2one(
        comodel_name = 'res.users',
        string='CEO Sign', readonly=True)
    ceo_date = fields.Date(
        string='Date')
    
    account_ids = fields.Many2many(
        comodel_name='account.account')
    
    
    @api.multi
    def button_reset(self):
        self.write({'state': 'new'})
        return {}
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        self.today_date = date.today()
        self.traveler_date = date.today()
        self.traveler_sign = self._uid
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        self.linemanager_sign = self._uid
        self.linemanager_date = date.today()
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
    @api.multi
    def button_validate(self):
        self.write({'state': 'validate'})
        self.admin_sign = self._uid
        self.admin_date = date.today()
        return {}
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        self.ceo_sign = self._uid
        self.ceo_date = date.today()
        return {}
    
    @api.model
    def create(self, vals):
        if vals.get('travelrequest_no', 'New') == 'New':
            vals['travelrequest_no'] = self.env['ir.sequence'].next_by_code('travel.request') or '/'
        return super(TravelRequest, self).create(vals)
    
class Hrrecruitment(models.Model):
    _name = 'ninas.hr.recruitment'
    _description = 'NiNAS HR Recruitment'
    _inherit = 'hr.applicant'

    name = fields.Char(
        string='Application ID')

class ConsRecpt(models.Model):
    _name = 'month.consumables'

    name = fields.Many2one(
        comodel_name='hr.employee',
        string='Staff')
    
    month_ids = fields.One2many(
        comodel_name = 'month.consumable',
        inverse_name = 'name_id', 
        string = 'Product')
    
    date = fields.Date(string="Date")
    
class ConsRecpted(models.Model):
    _name = 'month.consumable'

    name_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Staff')
    product_id = fields.Many2one(
        comodel_name='product.template', 
        string='Product')
    date = fields.Date(string="Date")
    quantity = fields.Char(string="Quantity")

class TrainingTracker(models.Model):
    _name = 'ninas.training_tracker'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    _description = 'Employee Training Tracker'
    
    #link to actual employee_id
    name = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Staff',
        required=1
        )
    #pull this from employee records and set required to true
    position = fields.Many2one(
        comodel_name = 'hr.job',
        string='Position',
        required=0
        )
    provider = fields.Char(
        string='Provider',
        required=1
        )
    training_date = fields.Date(
        string = 'Training Date'
        )
    #in case training lasts for days/weeks -- else, duration will be set to less than 20 hours
    start_date = fields.Date(
        string= 'Start Date'
        )
    qualification = fields.Char(
        string='Qualification',
        required=0
        )
    budget = fields.Integer(
        string='Budget',
        required=1
        )
    duration = fields.Selection(
        [(i, i) for i in range(20)],
        string='Duration (hrs)',
        required=1
        )
    unit = fields.Char(
        string='Unit',
        )
    capability = fields.Selection(
        [('100', 'Excellent'), 
        ('200', 'Very Good'), 
        ('300', 'Good'), 
        ('400', 'Fair')],
        string='Capability Level',
        required=0,
        default='400'
        )
    review = fields.Char(
        string ='Review on'
        )
    refresh = fields.Boolean(
        )
    notes = fields.Text(
        string='Notes'
        )
    
    
class AdvanceRequest(models.Model):
    _name = 'ninas.advance_request'
    _description = 'Advance Request Form'
#    _sql_constraints = [('student_uniq',
#                         'UNIQUE(name)',
#                         'Student name must be unique!')]
#    _inherit = 'mail.thread'
    
    #link to actual employee_id
    employee_name = fields.Char(
        #comodel_name = 'hr.employee',
        string ='Requested by',
        required=1
        )
    country_id = fields.Many2one(
        comodel_name='res.country',
        string='Country'
        )
    vendor = fields.Char(
        string='Name of Vendor',
        required=1
        )
    request_date = fields.Date(
        string = 'Date of Request'
        )
    #in case training lasts for days/weeks -- else, duration will be set to less than 20 hours
    invoice_date = fields.Date(
        string= 'Date of Invoice'
        )
    invoice_id = fields.Char(
        string='Invoice No.',
        required=0
        )
    amount = fields.Char(
        string='Amount',
        required=0
        )
    duration = fields.Selection(
        [(i, i) for i in range(20)],
        string='Duration (hrs)',
        required=0
        )
    
    purpose = fields.Char(
        string='Purpose',
        )
    project_manager = fields.Char(
        string ='Project Manager'
        )
    fund = fields.Selection([],
        string = 'Fund'
        )
    grant = fields.Char(
        string = 'FA/Grant'
        )
    cc = fields.Char(
        string = 'CC/WBS'
        )
    sponsored = fields.Char(
        string = 'Commitment Item/Sponsored Class'
        )
    notes = fields.Char(
        string ='Total Value and Currency: \
        (maximum equivalent of EUR 2,500 for\
         Advance and EUR 2,000 for Straight Expenditure)'
        )
    payment_agent = fields.Selection(
        [('undp', 'UNDP'),
         ('imprest', 'Imprest')],
        string = 'Payment Agent'
        )
    payee = fields.Char(
        string ='Payee/Supplier/Funds Custodian: (Index/Staff ID No)'
        )
    expected_date = fields.Date(
        string ='Expected settlement date: (An expense report with \
        attached pdf receipts to be emailed to HQ-FIN for clearing)'
        )
    remarks = fields.Char(
        string = 'Remarks'
        )
    
    approved_by = fields.Char(
        string = 'Approved by: (to be signed by Allotment Holder/Project Manager)'
        )
    
class MissionReport(models.Model):
    _name = 'ninas.mission_report'
    _description = 'Back-to-office Mission Report'


    #link to actual employee_id
    employee_name = fields.Char(
        #comodel_name = 'hr.employee',
        string ='Name',
        required=1
        )
    #pull this from employee records and set required to true
    position = fields.Char(
        string='Position',
        required=1
        )
    mission_date = fields.Date(
        string = 'Date of Mission',
        required=1
        )
    places = fields.Char(
        string='Places Visited',
        required=1
        )
    participants = fields.Char(
        string='Participants',
        )
    purpose = fields.Char(
        string='Purpose',
        required=1
        )
    background = fields.Char(
        string ='Background'
        )
    achievement = fields.Char(
        string = 'Achievements'
        )
    follow_up = fields.Char(
        string= 'Follow-Up Actions Required '
        ) 
    matters = fields.Char(
        string = 'Matters To Be Brought To The Notice Of The Programme Manager'
        )
    signature = fields.Char(
        string = 'Signature',
        required=1
        )
    date = fields.Date(
        string= 'Date',
        readonly=1
        )
    
    
    
    
    
    
    
    
    
    
    
    
    
   