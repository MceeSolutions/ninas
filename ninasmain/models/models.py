# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18
import datetime

from datetime import date, timedelta
from odoo import api, fields, models
from docutils.nodes import organization


class Employee(models.Model):
    _inherit = 'hr.employee'
    
    employee = fields.Char(
        string='Employee ID', readonly=True, index=True, copy=False, default='New')
    
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
#    employee = fields.Char(string='Employee ID')
    start_date = fields.Date(string='Start Date')
    salary = fields.Char(string='Salary')
    Training_date = fields.Date(string='Next Training Date')
    levelof_exp = fields.Selection([
        ('0', 'All'),
        ('1', 'Beginner'),
        ('2', 'Intermediate'),
        ('3', 'Professional')], string='Level Of Expertise',
        default='1')
    
    @api.model
    def create(self, vals):
        if vals.get('employee', 'New') == 'New':
            vals['employee'] = self.env['ir.sequence'].next_by_code('hr.employee') or '/'
        return super(Employee, self).create(vals)
    
class HrAppraisals(models.Model):
    _inherit = "hr.appraisal"
    
    Training_date = fields.Date(string='Training Date')
    
class Holidays(models.Model):
    _name = "hr.holidays"
    _inherit = 'hr.holidays'
    

    assigned_to = fields.Many2one(
        comodel_name="hr.employee",
        string='Duties Assigned To', required=False)
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
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('paid','Paid'), ('confirm','Confirmed')],
        string='Status',
        default='new',
        track_visibility='onchange')
    name = fields.Many2one(
        comodel_name="hr.employee",
        string='Person Requesting Loan', required=True)
    purpose = fields.Char(
        string='Purpose of Loan', required=True)
    terms_ofloan = fields.Char(
        string='Terms of Loan')
    repayment = fields.Text(
        string='Repayment')
    repayment_period = fields.Char(
        string='Repayment Period')
    
    start_date = fields.Datetime(string='Start Date')
    end_date = fields.Datetime(string='End Date')
    
    
    recieved_from = fields.Many2one(
        comodel_name="hr.employee",
        string='Recieved Name', readonly=True)
    recieved_from_name = fields.Many2one(
        comodel_name="hr.employee",
        string='Name', readonly=True)
    date_recevfrom = fields.Date(string='Date', readonly=True)
    date_recevfromname = fields.Date(string='Date', readonly=True)
    
    currency_id = fields.Many2one('res.currency', 'Currency')
    amount_total = fields.Monetary(compute='_total_naira',
        string='Total Amount', readonly=True, store=True)
    
    loan_line_ids = fields.One2many(
        comodel_name='loan.req',
        inverse_name='employee_id')
    
    loan_amt = fields.Monetary(
        string='Loan Amount')
    
    @api.multi
    def button_reset(self):
        self.write({'state': 'new'})
        return {}
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        return {}
    
    @api.multi
    def button_paid(self):
        self.write({'state': 'paid'})
        self.recieved_from = self._uid
        self.date_recevfrom = date.today()
        return {}
    
    @api.multi
    def button_confirm(self):
        self.write({'state': 'confirm'})
        self.recieved_from_name = self._uid
        self.date_recevfromname = date.today()
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
    @api.depends('loan_line_ids.loan_amount')
    def _total_naira(self):
        amount_total = 0.0
        for line in self.loan_line_ids:
            self.amount_total += line.loan_amount

class LoanReq(models.Model):
    _name = 'loan.req'
    
    loan_amount = fields.Monetary(string='Loan Amount')
    description = fields.Char(string='Month Repaid')
    
    currency_id = fields.Many2one('res.currency', 'Currency')
    
    employee_id = fields.Many2one('loan.request', 'Employee', invisible=True)

        
    
class TravelRequest(models.Model):
    _name = 'travel.request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
    today_date = fields.Date(
        string='Todays Date', readonly=True)
    travelrequest_no = fields.Char(
        string='Travel request Number', readonly=True, required=True, index=True, copy=False, default='New')
    traveller_email = fields.Char(
        related='name.work_email',
        string='Travellers Email Address', readonly=True)
    name = fields.Many2one(
        comodel_name="hr.employee",
        string='Travellers Name', required=True)
    traveller_job = fields.Char(related='name.job_id.name',string='Traveller Job Title', readonly=True)
    traveller_phone = fields.Char(related='name.work_phone',string='Traveller Phone', readonly=True)
    traveller_department = fields.Char(related='name.department_id.name',string='Department', readonly=True)
    contact_phone = fields.Char(related='name.telphone',string='Contact Phone', readonly=True)
    contact_name = fields.Char(related='name.fname',string='Contact Name', readonly=True)
    traveller_employee_id = fields.Char(related='name.employee',string='Travellers Employee ID', readonly=True)
    purpose = fields.Text(string='Purpose and Benefit of Travel', required=True)
    
    classification_of_traveller = fields.Selection([
        ('employee','Ninas Employee'),('expert','Ninas Expert'),('assessor','Ninas Assessor'),('guest','Ninas Guest'),('other','Others(Describe)')])
    
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
        string='Will any days be spent primarily on non-business activities (Yes or No)?', default='no')
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
        string='Date', readonly=True)
    ceo_sign = fields.Many2one(
        comodel_name = 'res.users',
        string='CEO Sign', readonly=True)
    ceo_date = fields.Date(
        string='Date', readonly=True)
    
    account_ids = fields.One2many(
        comodel_name='ninas.travel.account',
        inverse_name='travel_request_id')
    
    total_unit_price = fields.Float(string='Total Unit Price', compute='_total_unit', readonly=True)
    total_amount = fields.Char(string='Total Amount')
    
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
    
    
    @api.depends('account_ids.unit_price')
    def _total_unit(self):
        total_unit_price = 0.0
        for line in self.account_ids:
            self.total_unit_price += line.unit_price
            
class TravelAccount(models.Model):
    _name = 'ninas.travel.account'
    
    travel_request_id =fields.Many2one(
        comodel_name='travel.request')
    
    type = fields.Char(string='Type Of Expense')
    account_id = fields.Many2one(
        comodel_name='account.account', string='Account')
    grant = fields.Char(string='Grant')
    unit = fields.Char(string='Unit(s)')
    unit_price = fields.Float(string='Unit Price')
    amount = fields.Float(string='Sub Amount', readonly=True)

    
    
class Hrrecruitment(models.Model):
    _name = 'ninas.hr.recruitment'
    _description = 'NiNAS HR Recruitment'
    _inherit = 'hr.applicant'

    name = fields.Char(string='Application ID')
    first_name = fields.Char(string='First Name')
    last_name = fields.Char(string='Last Name')
    address = fields.Char(string='Address')
    job_discovery = fields.Selection([('',''),('newspaper','Newspaper'),('website', 'Website'), ('word of mouth','Word of Mouth')],
        string='How did you hear about this post or where did you see it advertised:',
        default='',
        track_visibility='onchange')

class ConsRecpted(models.Model):
    _name = 'month.consumable'

    name_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Staff', required=True)
    product_id = fields.Many2one(
        comodel_name='product.template', 
        string='Product', required=True)
    date = fields.Date(string="Date", required=True)
    
    quantity = fields.Selection(
        [(i, i) for i in range(100)],
        string='Quantity',
        required=False)
    
    order_id = fields.Many2one(
        comodel_name='month.consumables',
        string='order id')

class ConsRecpt(models.Model):
    _name = 'month.consumables'

    name = fields.Many2one(
        comodel_name='hr.employee',
        string='Staff')
    
    month_ids = fields.One2many(
        comodel_name = 'month.consumable',
        inverse_name = 'order_id', 
        string = 'Product')
    
    date = fields.Date(string="Date")
    

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
    position = fields.Char(
        related='name.job_id.name',
        readonly=True,
        string='Position',
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
    budget = fields.Many2one(
        comodel_name='account.account',
        string='Expense Account',
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
    review = fields.Date(
        string ='Next Training Date'
        )
    refresh = fields.Boolean(
        )
    notes = fields.Text(
        string='Notes'
        )
    
    
class AdvanceRequest(models.Model):
    _name = 'ninas.advance_request'
    _description = 'Advance Request Form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
#    _sql_constraints = [('student_uniq',
#                         'UNIQUE(name)',
#                         'Student name must be unique!')]
#    _inherit = 'mail.thread'
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
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
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
class MissionReport(models.Model):
    _name = 'ninas.mission_report'
    _description = 'Back-to-office Mission Report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
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
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
class NinasBankVoucher(models.Model):
    _name = 'ninas.bank_voucher'
    _description = 'Bank Payment Voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
    #link to actual employee_id
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee',
        required=1
        )
    method = fields.Selection(
        [('cash','Cash'),('chq','Cheque')],
        string='Payment Method',
        required=1
        )
    chq_number = fields.Integer(
        string='Cheque Number',
        required=1
        )
    voucher_number = fields.Integer(
        string='Voucher Number',
        required=1
        )
    item_date = fields.Date(
        string = 'Date',
        required=1
        )
    item = fields.Char(
        string='Item (Description)',
        required=0
        )
    ref_number = fields.Integer(
        string='Ref. No.',
        )
    unit_code = fields.Char(
        string='Unit Code',
        required=1
        )
    fund_code = fields.Char(
        string ='Fund Code'
        )
    budget_line = fields.Char(
        string = 'Activity/Budget Line Code'
        )
    account_code = fields.Char(
        string= 'Account Code'
        ) 
    
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)
    
    amount = fields.Monetary(
        string = 'Amount (NGN)'
        )
    
    total = fields.Monetary(
        string='Total Amount',
        store=True, readonly=True
        )
    
    prepared = fields.Char(
        string='Prepared by',
        required=1
        )
    reviewed = fields.Char(
        string ='Reviewed by'
        )
    authorised = fields.Char(
        string = 'Authorised Manager/Signatory'
        )
    account_number = fields.Char(
        string= 'Account Number'
        ) 
    tin = fields.Integer(
        string = 'TIN'
        )
    bank = fields.Char(
        string ='Bank Name'
        )
    signature = fields.Char(
        string = 'Signature'
        )
    date = fields.Date(
        string= 'Date'
        )
    bank_voucher = fields.One2many(
        comodel_name='bank.voucher',
        inverse_name='employee_id',
        string='Bank Voucher'
        )
    
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
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
class BankVoucher(models.Model):
    _name = 'bank.voucher'
    
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee'
        )
    item_date = fields.Date(
        string = 'Date',
        required=1
        )
    item = fields.Char(
        string='Item (Description)',
        required=0
        )
    ref_number = fields.Integer(
        string='Ref. No.',
        )
    unit_code = fields.Char(
        string='Unit Code',
        required=1
        )
    fund_code = fields.Char(
        string ='Fund Code'
        )
    budget_line = fields.Char(
        string = 'Activity/Budget Line Code'
        )
    account_code = fields.Char(
        string= 'Account Code'
        ) 
    amount = fields.Integer(
        string = 'Amount (NGN)'
        )
    total = fields.Integer(
        string='Total Amount',
        )
    
    
class NinasExpenseClaim(models.Model):
    _name = 'ninas.expense_claim'
    _description = 'Expense Claim form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
    #link to actual employee_id
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee',
        required=1
        )
    employee_code = fields.Integer(
        string='Employee Code',
        )
    ref_number = fields.Integer(
        string='Ref. No. (Receipts to be numbered serially)',
        )
    amount_received = fields.Float(
        string='Amount Received From Finance'
        )
    item_date = fields.Date(
        string = 'Date',
        required=1
        )
    item = fields.Char(
        string='Item (Description)',
        required=0
        )
    unit_code = fields.Char(
        string='Unit Code',
        required=1
        )
    fund_code = fields.Char(
        string ='Fund Code'
        )
    budget_line = fields.Char(
        string = 'Activity/Budget Line Code'
        )
    account_code = fields.Char(
        string= 'Account Code'
        ) 
    amount = fields.Integer(
        string = 'Amount (NGN)'
        )
    total = fields.Integer(
        string='Total Amount Spent',
        )
    balance = fields.Float(
        string='Balance (Due to)/ Due from Employee'
        )
    prepared = fields.Char(
        string='Prepared by',
        required=1
        )
    reviewed = fields.Char(
        string ='Reviewed by'
        )
    authorised = fields.Char(
        string = 'Authorised Manager/Signatory'
        )
    account_number = fields.Char(
        string= 'Account Number'
        ) 
    tin = fields.Integer(
        string = 'TIN'
        )
    bank = fields.Char(
        string ='Bank Name'
        )
    signature = fields.Char(
        string = 'Signature'
        )
    date = fields.Date(
        string= 'Date'
        )
    expense_claim = fields.One2many(
        comodel_name='expense.claim',
        inverse_name='employee_id',
        string='Expense Claim'
        )
    
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
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
class ExpenseClaim(models.Model):
    _name = 'expense.claim'
    
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee', required=True
        )
    ref_number = fields.Integer(
        string='Ref. No.'
        )
    employee_code = fields.Integer(
        string='Employee Code'
        )
    item_date = fields.Date(
        string = 'Date',
        required=1
        )
    item = fields.Char(
        string='Item (Description)',
        required=0
        )
    unit_code = fields.Char(
        string='Unit Code',
        required=1
        )
    fund_code = fields.Char(
        string ='Fund Code'
        )
    budget_line = fields.Char(
        string = 'Activity/Budget Line Code'
        )
    account_code = fields.Char(
        string= 'Account Code'
        ) 
    amount = fields.Integer(
        string = 'Amount (NGN)'
        )
    total = fields.Integer(
        string='Total Amount',
        )

class StoreReqEdit(models.Model):
    _name = "stock.picking"
    _inherit = 'stock.picking'
    
    location_id = fields.Many2one(
        'stock.location', "Source Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_src_id,
        readonly=False, required=True,
        states={'draft': [('readonly', False)]})
    location_dest_id = fields.Many2one(
        'stock.location', "Destination Location",
        default=lambda self: self.env['stock.picking.type'].browse(self._context.get('default_picking_type_id')).default_location_dest_id,
        readonly=True, required=True,
        states={'draft': [('readonly', False)]})
    
    @api.multi
    def manager_confirm(self):
        for order in self:
            order.write({'man_confirm': True})
        return True
    
    def _default_owner(self):
        return self.env.context.get('default_employee_id') or self.env['res.users'].browse(self.env.uid).partner_id
    
    def _default_employee(self):
        self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)])
    
    owner_id = fields.Many2one('res.partner', 'Owner',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, default=_default_owner,
        help="Default Owner")
    
    employee_id = fields.Many2one('hr.employee', 'Employee',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, default=_default_employee,
        help="Default Owner")
    
    man_confirm = fields.Boolean('Manager Confirmation', track_visibility='onchange')
    
    @api.multi
    def button_reset(self):
        self.mapped('move_lines')._action_cancel()
        self.write({'state': 'draft'})
        return {}


class DieselConsumption(models.Model):
    _name = 'ninas.diesel.consumption'

    date_input=fields.Date(
        string='Date',
        required=True
        )
    diesel_level_start=fields.Float(
        string='Diesel Level Start',
        default=0,
        )
    time_started=fields.Datetime(
        string='Time Started',
        default=0,
        )
    engine_temp_start=fields.Float(
        string='Engine Temperature',
        default=0,
        )
    oil_level_start=fields.Float(
        string='Oil Level',
        default=0,
        )
    battery_voltage_start=fields.Float(
        string='Battery Voltage',
        default=0,
        )
    diesel_level_end=fields.Float(
        string='Diesel Level End',
        default=0,
        )
    time_ended=fields.Datetime(
        string='Time Ended',
        default=0,
        )
    engine_temp_end=fields.Float(
        string='Engine Temperature',
        default=0,
        )
    oil_level_end=fields.Float(
        string='Oil Level',
        default=0,
        )
    battery_voltage_end=fields.Float(
        string='Battery Voltage',
        default=0,
        )
    diesel_available=fields.Float(
        compute='_subtract_',
        string='Diesel Level'
        )

    @api.multi
    def _subtract_(self):
        for num in self:
            diesel_available = num.diesel_level_start - num.diesel_level_end
            num.diesel_available = diesel_available



class CodeofConduct(models.Model):
    _name = 'ninas.code.conduct'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('accept', 'Accepted'), ('approve','Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    agreement = fields.Boolean(
        string='I have read and concur with NiNAS’s Code of Conduct (Sections 1-7).',
        required=True
        )
    date = fields.Date(
        )
    date_today = fields.Date(
        )
    description = fields.Text(
        )
    name = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee Printed name:',
        readonly=True)
    date_signed = fields.Date(
        string='Date',
        readonly=True)

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.date_signed = date.today()
        self.name = self._uid
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        return {}
    
class ConflictofInterest(models.Model):
    _name = 'ninas.conflict.interest'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('accept', 'Accepted'), ('approve','Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    agreement = fields.Boolean(
        string='I have read and concur with NiNAS’s Code of Conduct (Sections 2-7).',
        required=True
        )
    date = fields.Date(
        )
    date_today = fields.Date(
        )
    description = fields.Text(
        )
    name = fields.Char(
        string='Name of Institution or Persone:')
    
    printed_name = fields.Char(related='name',readonly=True,
        string='Printed Name')
    
    location = fields.Char(
        string='Location')
    date_signed = fields.Date(
        string='Date',
        readonly=True)

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.date_signed = date.today()
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        return {}


class Confidentiality(models.Model):
    _name = 'ninas.confidentiality'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    agreement = fields.Boolean(
        required=True
        )
    
    state = fields.Selection(
        [('new','New'),('accept', 'Accepted'), ('approve','Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    name = fields.Char(
        string='Name of Institution or Persone:',required=True)
    location = fields.Char(
        string='Location',required=True)
    name_rep = fields.Char(
        string='Name of Person:',required=True)
    
    date = fields.Date(
        )
    description = fields.Text(
        )
    
    signed = fields.Char(related='name_rep',readonly=True,
        string='Signed')

    date_signed = fields.Date(
        string='Date',
        readonly=True)

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.date_signed = date.today()
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        return {}


class PettyCash(models.Model):
    _name = 'ninas.petty_cash'

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected')],
        string='Status',
        default='new',
        track_visibility='onchange')

    date_entered=fields.Date(
        string='Date',
        required=True
        )
    ref_no=fields.Char(
        string='Ref No'
        )
    name_of_payee=fields.Char(
        string='Name of Payee',
        required=True
        )
    amount_naira=fields.Integer(
        string='Amount (Naira)',
        required=False
        )
    description=fields.Text(
        string='Description of Payment',
        required=True
        )
    accounts_charge=fields.Char(
        string='Account Chargeable'
        )
    grant=fields.Char(
        string='Grant'
        )
    budget_line=fields.Char(
        string='Budget line'
        )
    gl=fields.Char(
        string='GL'
        )
    prepared_by=fields.Many2one(
        comodel_name="hr.employee",
        string='Prepared by',
        readonly=True
        )
    approved_by=fields.Many2one(
        comodel_name="hr.employee",
        string='Approved by',
        readonly=True
        )

    @api.multi
    def button_submit(self):
        self.write({'state':'submit'})
        self.prepared_by = self._uid
        return {}

    @api.multi
    def button_approve(self):
        self.write({'state':'approve'})
        self.approved_by = self._uid
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state':'reject'})
        return {}


class ContractAgreement(models.Model):
    _name = 'ninas.contract.agreement'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    date = fields.Date(string='Effective Date', required=True)
    name = fields.Char(string='Name', required=True)
    
    contract_line_ids = fields.One2many(
        comodel_name='ninas.contract.agreement.items',
        inverse_name='item')
    
    currency_id = fields.Many2one('res.currency', 'Currency')
    amount_total = fields.Monetary(compute='_total_amount',
        string='Total', readonly=True, store=True)
    
    assessor_name = fields.Char(string='Name')
    organization_name = fields.Char(string='Organizatoin Name')
    assessor_address = fields.Char(string='Physical & postal Address')
    city_country = fields.Char(string='City/Country')
    
    contract_date = fields.Date(string='Date')
    
    assessor_expert_name = fields.Char(string='Assessor/Expert’s (Name)')
    management_rep = fields.Char(string="On behalf of NINAS (Management Representative)")
    assessor_sign = fields.Date(string='Assessor/Expert’s (Sign)')
    assessor_ref = fields.Char(string='Assessor/Expert’s Ref No')
    

    @api.depends('contract_line_ids.amount')
    def _total_amount(self):
        amount_total = 0.0
        for line in self.contract_line_ids:
            self.amount_total += line.amount

    
class ContractAgreementItems(models.Model):
    _name = 'ninas.contract.agreement.items'
    
    item=fields.Char(string='Item')
    amount=fields.Monetary(string='Amount')
    currency_id = fields.Many2one('res.currency', 'Currency')
    
class ActivityBudget(models.Model):
    _name = 'ninas.activity_budget'
    _description = 'Activity Budget Template'

    employee_id= fields.Char(
        #related = 'Employee Name'
        #required=1,
        )
    employee = fields.Integer(
        #related = ''
        string='Employee Code',
        #required=1,
        readonly=1
        )
    purpose = fields.Text(
        string="Purpose/Description of Activity",
        required=1
        )
    date = fields.Date(
        string = 'Activity Date',
        required=1,
        )
    total = fields.Float(
        compute = 'sum',
        string="Total Amount",
        readonly=1
        )
    activity_budget = fields.One2many(
        comodel_name = 'activity.budget',
        inverse_name = 'name',
        string = 'Activity Budget'
        )

    @api.one
    def sum(self):
        total = 0.0
        for line in self.activity_budget:
            self.total += line.amount
         
class ABudget(models.Model):
    _name = 'activity.budget'
    
    name = fields.Char(
        string=""
        )
    employee_id = fields.Many2one(  
        comodel_name = 'hr.employee',
        string ='',
        required=0
        )
    item = fields.Char(
        string='Items',
        required=0
        )
    units = fields.Integer(
        string = 'No. of Units',
        required=0
        )
    cost = fields.Float(
        string = 'Unit Cost',
        required=0
        )
    amount = fields.Float(
        compute = 'mul',
        string = 'Amount',
        readonly=1
        )
    remarks = fields.Char(
        string = 'Remarks',
        required=0
        )
    fund_code = fields.Char(
        #related = 'Employee Name'
        string = 'Fund Code',
        #required=1
        )
    budget_code = fields.Char(
        #related = 'Employee Name',
        string = 'Budget Line Code',
        #required=1
        )

    @api.one
    def mul(self):
        self.amount = self.units  *  self.cost
        return True
    
    
class OpenClose(models.Model):
    _name = 'ninas.open_close'
    _description = 'Opening and Closing Agenda'

    org = fields.Char(
        #related = ''
        string = 'Organization'
        )
    location = fields.Char(
        string = 'Location'
        )
    la = fields.Many2one(
        comodel_name = 'hr.employee',
        string = 'Lead Assessor'
        )
    today = fields.Date(
        string = 'Date',
        default= date.today(),
        readonly=1
        )
    oc = fields.One2many(
        comodel_name = 'open.close',
        inverse_name = 'name',
        string = 'Opening Agenda'
        )
    oc2 = fields.One2many(
        comodel_name = 'open.close2',
        inverse_name = 'name',
        string = 'Closing Agenda'
        )
    attendance = fields.One2many(
        comodel_name = 'ninas.attendance',
        inverse_name = 'name',
        string = 'Attendance'
    )

class OC(models.Model):
    _name = 'open.close'
    
    name = fields.Char(
        string=""
        )
    employee_id = fields.Many2one(  
        comodel_name = 'hr.employee',
        string ='Name of Payee',
        required=0
        )
    sn = fields.Integer(
        string="S/N"
        )
    agenda = fields.Char(
        string = 'Activity',
        required=0
        )

class OC2(models.Model):
    _name = 'open.close2'
    
    name = fields.Char(
        string=""
        )
    employee_id = fields.Many2one(  
        comodel_name = 'hr.employee',
        string ='Name of Payee',
        required=0
        )
    sn = fields.Integer(
        string="S/N"
        )
    agenda = fields.Char(
        string = 'Activity',
        required=0
        )
    
class NinasAttendance(models.Model):
    _name = 'ninas.attendance'

    name = fields.Char(
        string=""
        )
    attendee = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Attendee',
        required=0
    )
    position = fields.Char(
        related = 'attendee.job_id.name',
        string = 'Position',
        readonly = 1
    )
    open = fields.Boolean(
        string = 'Open'
    )
    close = fields.Boolean(
        string = 'Close'
    )
    
class MedicalLab(models.Model):
    _name = 'ninas.medical'
    _description = 'Medical Laboratory'

    #name of institution
    institution = fields.Char(
        string = 'Name of Laboratory',
        required=1
        )
    address = fields.Char(
        string = 'Address of Laboratory',
        readonly=1
        )
    #auto generate eg: M0001
    name = fields.Char(
        string="Schedule No.",
        readonly=1
        )
    issue1 = fields.Date(
        string = 'Issue No. 1',
        required=1
        )
    valid = fields.Date(
        string="Valid To",
        required=1
        )
    med_lab = fields.One2many(
        comodel_name = 'med.lab',
        inverse_name = 'name',
        string = 'Medical Laboratory'
        )

class MedLab(models.Model):
    _name = 'med.lab'
    
    name = fields.Char(
        string=""
        )
    employee_id = fields.Many2one(  
        comodel_name = 'hr.employee',
        string ='',
        required=0
        )
    sample = fields.Char(
        string='Type of Sample',
        required=1
        )
    tests = fields.Char(
        string = 'Type of Tests',
        required=1
        )
    equipment = fields.Char(
        string = 'Equipment',
        required=1
        )
    method = fields.Char(
        string='Method Used',
        required=1
        )    
    
class CalibrationLab(models.Model):
    _name = 'ninas.calibration'
    _description = 'Calibration Laboratory'

    #name of institution
    institution = fields.Char(
        string = 'Name of Laboratory',
        required=1
        )
    address = fields.Char(
        string = 'Address of Laboratory',
        readonly = 1
        )
    #auto generate eg: C0001
    name = fields.Char(
        string="Schedule No.",
        required=0
        )
    issue1 = fields.Date(
        string = 'Issue No. 1',
        required=1
        )
    valid = fields.Date(
        string="Valid To",
        required=1
        )
    cal_lab = fields.One2many(
        comodel_name = 'cal.lab',
        inverse_name = 'name',
        string = 'Calibration Laboratory'
        )

class CalLab(models.Model):
    _name = 'cal.lab'
    
    name = fields.Char(
        string=""
        )
    employee_id = fields.Many2one(  
        comodel_name = 'hr.employee',
        string ='',
        required=0
        )
    mqty = fields.Char(
        string='Measured Quantity',
        required=1
        )
    range = fields.Float(
        string = 'Range',
        required=1
        )
    cmc = fields.Float(
        string = 'Calibration and Measurement Capacity',
        required=1
        )
    method = fields.Char(
        string='Brief Description of Calibration Method',
        required=1
        )
    equipment = fields.Char(
        string='Brief Description of Calibration Equipment',
        required=1
        )
    
class ChemicalLab(models.Model):
    _name= 'ninas.chemical_lab'
    _description= 'Chemical Testing Laboratory'
    
    issue_no= fields.Date(
        string='Issue No. 1',
        required=1
    )
    institution= fields.Char(
        string= 'Name of Laboratory',
        required=1
    )
    address= fields.Char(
        string='Address of Laboratory',
        required=1
    )
    schedule_number= fields.Char(
        string='Schedule No.',
        required=1
    ) 
    valid_no= fields.Date(
        string='Valid To',
        required=1
    )
    chem_lab= fields.One2many(
        comodel_name='chem.lab',
        inverse_name='name',
        string='Chemical Laboratory'
    )
class ChemLab(models.Model):
    _name= 'chem.lab'
    
    name= fields.Char(
        string="Name",
        required=1
    )
    employee_id= fields.Many2one(
        comodel_name='hr.employee',
        string='',
        required=0
    )
    products= fields.Char(
        string='Materials/ Products Tested',
        required=1
    )
    tests= fields.Char(
        string='Type of Tests/ Property Measured /Range of Managements',
        required=1
    )
    standards= fields.Char(
        string='Standard Specifications',
        required=1
    )
    techniques= fields.Char(
        string='Techniques Used',
        required=1
    )
    