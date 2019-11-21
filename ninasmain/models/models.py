# -*- coding: utf-8 -*-

#@author mcee
#Date: 4/06/18
import datetime

from datetime import date, timedelta
from odoo import api, fields, models, _
from docutils.nodes import organization
from odoo.exceptions import ValidationError, Warning
from ast import literal_eval
from odoo.exceptions import UserError, RedirectWarning
#from pbr.tests.testpackage.pbr_testpackage.wsgi import application

class Partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    @api.multi
    def _get_default_country(self):
        default_country = self.env['res.country'].sudo().search([('name','=','Nigeria')], limit=1).id
        return default_country
    
    vendor_tin = fields.Char('TINs')
    vendor_code = fields.Char('Code/Vendor No.')
    
    country_id = fields.Many2one('res.country', string='Countryu', ondelete='restrict', required=True, readonly=True,  default =_get_default_country)
    
    #partner_confidentiality = fields.Many2one(comodel_name="ninas.confidentiality")
    #partner_conflict = fields.Many2one(comodel_name="ninas.conflict.interest")
    
    attachment_count = fields.Integer(compute="_compute_attachment_count", string="Attachments")
    
    def _compute_attachment_count(self):
        Attachment = self.env['ir.attachment']
        for partner in self:
            partner.attachment_count = Attachment.search_count([('res_model', '=', 'res.partner'), ('res_id', '=', partner.id)])
            
    @api.multi
    def view_attachments(self):
        self.ensure_one()
        attachments = self.env['ir.attachment'].search([('res_model', '=', 'res.partner'), ('res_id', '=', self.id)])
        action = self.env.ref('base.action_attachment').read()[0]
        action['domain'] = [('id', 'in', attachments.ids)]
        action['context'] = {'default_res_model': 'res.partner', 'default_res_id': self.id}
        return action
    
    car_ids = fields.One2many('car.report', 'partner_id', string='CARs', readonly=True, copy=False)
    
class DocumentType(models.Model):
    _name = "document.type"
    _description = "Document Type"

    name = fields.Char(string='Document Name', required=True)
    available = fields.Boolean('Available on Portal')


class IrAttachment(models.Model):
    _inherit = "ir.attachment"

    document_type = fields.Many2one(comodel_name='document.type', string='Document Type')
    document_available = fields.Boolean(related="document_type.available", store=True)
    
class Employee(models.Model):
    _inherit = 'hr.employee'
    
    employee = fields.Char(
        string='Employee ID', readonly=False, index=True, copy=False, default='New')
    
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
    salary = fields.Float(string='Salary')
    
    
    Training_date = fields.Date(string='Next Training Date')
    
    levelof_exp = fields.Selection([
        ('0', 'All'),
        ('1', 'Beginner'),
        ('2', 'Intermediate'),
        ('3', 'Professional')], string='Level Of Expertise',
        default='1')
    
    employee_tin = fields.Char(string='Employee Tin Number')
    
    emergency_fname = fields.Char(string='First Name')
    emergency_lname = fields.Char(string='Last Name')
    emergency_address = fields.Char(string='street address')
    emergency_unit = fields.Char(string='Apartment Unit')
    emergency_relationship = fields.Char(string='Relationship')
    emergency_telphone = fields.Char(string='Primary Phone')
    emergency_phone_id = fields.Char(string='Alternate Phone')
    emergency_city = fields.Char(
        string='City')
    emergency_state_id = fields.Many2one(
        string='State',
        comodel_name='res.country.state')
    emergency_zip_code = fields.Char(string='Zip Code')
    
    employee_resignation_date = fields.Date(string='Date Of Resignation')
    comments_on_resignation = fields.Text(string='Comments On Resignation')
    duties_temporarily_assigned = fields.Many2one(comodel_name='hr.employee', string='Duties Temporarily Assigned to')
    notice_period = fields.Char(string='Notice Period', help='notice period given by employee before leaving/resignation')
    
    @api.model
    def create(self, vals):
        if vals.get('employee', 'New') == 'New':
            vals['employee'] = self.env['ir.sequence'].next_by_code('hr.employee') or '/'
        return super(Employee, self).create(vals)
    
    @api.constrains('employee')
    def check_code(self):
        if self.employee:
            if self.search([('employee','=',self.employee),('id','!=',self.id)]):
                return Warning('Employee ID must be unique!')
    
    @api.multi
    def send_birthday_mail(self):
        test = False
        employees = self.env['hr.employee'].search([])
        
        for self in employees:
            if self.active == True:
                if self.birthday:
                    test = datetime.datetime.strptime(self.birthday, "%Y-%m-%d")
                    
                    birthday_day = test.day
                    birthday_month = test.month
                    
                    today = datetime.datetime.now().strftime("%Y-%m-%d")
                    
                    test_today = datetime.datetime.today().strptime(today, "%Y-%m-%d")
                    birthday_day_today = test_today.day
                    birthday_month_today = test_today.month
                    
                    if birthday_month == birthday_month_today:
                        if birthday_day == birthday_day_today:
                            config = self.env['mail.template'].sudo().search([('name','=','Birthday Reminder')], limit=1)
                            mail_obj = self.env['mail.mail']
                            if config:
                                values = config.generate_email(self.id)
                                mail = mail_obj.create(values)
                                if mail:
                                    mail.send()
                                return True
        return
    
    
    @api.multi
    def send_birthday_reminder_mail(self):

        employees = self.env['hr.employee'].search([])
        
        current_dates = False
        
        for self in employees:
            if self.birthday:
                
                current_dates = datetime.datetime.strptime(self.birthday, "%Y-%m-%d")
                current_datesz = current_dates - relativedelta(days=3)
                print(current_datesz)
                
                date_start_day = current_datesz.day
                date_start_month = current_datesz.month
                date_start_year = current_datesz.year
                
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                
                test_today = datetime.datetime.today().strptime(today, "%Y-%m-%d")
                date_start_day_today = test_today.day
                date_start_month_today = test_today.month
                date_start_year_today = test_today.year
                
                
                if date_start_month == date_start_month_today:
                    if date_start_day == date_start_day_today:
                        config = self.env['mail.template'].sudo().search([('name','=','Birthday Reminder HR')], limit=1)
                        mail_obj = self.env['mail.mail']
                        if config:
                            values = config.generate_email(self.id)
                            mail = mail_obj.create(values)
                            if mail:
                                mail.send()
                            return True
        return
    
class HrAppraisals(models.Model):
    _inherit = "hr.appraisal"
    
    Training_date = fields.Date(string='Training Date')
    
class Holidays(models.Model):
    _name = "hr.holidays"
    _inherit = 'hr.holidays'
    
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('cancel', 'Cancelled'),
        ('confirm', 'To Approve'),
        ('refuse', 'Refused'),
        ('validate1', 'Second Approval'),
        ('validate', 'Validated'),
        #('ceo','CEO Approval')
        ], string='Status', readonly=True, track_visibility='onchange', copy=False, default='confirm',
            help="The status is set to 'To Submit', when a leave request is created." +
            "\nThe status is 'To Approve', when leave request is confirmed by user." +
            "\nThe status is 'Refused', when leave request is refused by manager." +
            "\nThe status is 'Approved', when leave request is approved by manager.")
    
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
    
    compute_field = fields.Boolean(string="check field", compute='get_user', default=True)
    ceo_approval = fields.Boolean(string="Ceo Approved", track_visibility='onchange')
    
    @api.model
    def create(self, vals):
        result = super(Holidays, self).create(vals)
        result.send_mail()
        return result
    
    @api.multi
    def send_mail(self):
        if self.state in ['confirm']:
            config = self.env['mail.template'].sudo().search([('name','=','Leave Approval Request Template')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
    
    @api.onchange('employee_id')
    def get_user(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.employee_id.parent_id:
            self.compute_field = False
        else:
            self.compute_field = True
    
    @api.multi
    def send_manager_approved_mail(self):
        config = self.env['mail.template'].sudo().search([('name','=','Leave Manager Approval')], limit=1)
        mail_obj = self.env['mail.mail']
        if config:
            values = config.generate_email(self.id)
            mail = mail_obj.create(values)
            if mail:
                mail.send()
    
    @api.multi
    def send_hr_approved_mail(self):
        config = self.env['mail.template'].sudo().search([('name','=','Leave HR Approval')], limit=1)
        mail_obj = self.env['mail.mail']
        if config:
            values = config.generate_email(self.id)
            mail = mail_obj.create(values)
            if mail:
                mail.send()
    
    @api.multi
    def send_hr_notification(self):
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_admin_finance_officer')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Leave Request for {} is Ready for Second Approval".format(self.display_name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    
    @api.multi
    def _check_security_action_validate(self):
        #current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if not self.env.user.has_group('hr_holidays.group_hr_holidays_user'):
            raise UserError(_('Only an HR Officer or Manager can approve leave requests.'))
    
    @api.multi
    def _check_line_manager(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.employee_id:
            raise UserError(_('Only your line manager can approve your leave request.'))
    
    '''
    date_from = fields.Date('Start Date', readonly=True, index=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    date_to = fields.Date('End Date', readonly=True, copy=False,
        states={'draft': [('readonly', False)], 'confirm': [('readonly', False)]}, track_visibility='onchange')
    '''
    
    @api.multi
    def button_ceo(self):
        self.ceo_approval = True
        subject = "CEO has Approved leave for {} ".format(self.display_name)
        partner_ids = []
        for partner in self.message_partner_ids:
            partner_ids.append(partner.id)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return {}
    
    @api.multi
    def action_approve(self):
        # if double_validation: this method is the first approval approval
        # if not double_validation: this method calls action_validate() below
        self._check_security_action_approve()
        #self._check_line_manager()

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state != 'confirm':
                raise UserError(_('Leave request must be confirmed ("To Approve") in order to approve it.'))

            if holiday.double_validation:
                holiday.send_manager_approved_mail()
                holiday.send_hr_notification()
                holiday.write({'state': 'validate1', 'first_approver_id': current_employee.id})
            else:
                holiday.action_validate()
    
    @api.multi
    def action_validate(self):
        self._check_security_action_validate()

        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        for holiday in self:
            if holiday.state not in ['confirm', 'validate1']:
                raise UserError(_('Leave request must be confirmed in order to approve it.'))
            if holiday.state == 'validate1' and not holiday.env.user.has_group('hr_holidays.group_hr_holidays_manager'):
                raise UserError(_('Only an HR Manager can apply the second approval on leave requests.'))

            holiday.write({'state': 'validate'})
            holiday.send_hr_approved_mail()
            if holiday.double_validation:
                holiday.write({'second_approver_id': current_employee.id})
            else:
                holiday.write({'first_approver_id': current_employee.id})
            if holiday.holiday_type == 'employee' and holiday.type == 'remove':
                holiday._validate_leave_request()
            elif holiday.holiday_type == 'category':
                leaves = self.env['hr.holidays']
                for employee in holiday.category_id.employee_ids:
                    values = holiday._prepare_create_by_category(employee)
                    leaves += self.with_context(mail_notify_force_send=False).create(values)
                # TODO is it necessary to interleave the calls?
                leaves.action_approve()
                if leaves and leaves[0].double_validation:
                    leaves.action_validate()
        return True
    
    @api.multi
    def send_leave_notification_mail(self):

        employees = self.env['hr.holidays'].search([])
        
        current_dates = False
        
        for self in employees:
            if self.date_from:
                
                current_dates = datetime.datetime.strptime(self.date_from, "%Y-%m-%d")
                current_datesz = current_dates - relativedelta(days=3)
                
                date_start_day = current_datesz.day
                date_start_month = current_datesz.month
                date_start_year = current_datesz.year
                
                today = datetime.datetime.now().strftime("%Y-%m-%d")
                
                test_today = datetime.datetime.today().strptime(today, "%Y-%m-%d")
                date_start_day_today = test_today.day
                date_start_month_today = test_today.month
                date_start_year_today = test_today.year
                
                
                if date_start_month == date_start_month_today:
                    if date_start_day == date_start_day_today:
                        if date_start_year == date_start_year_today:
                            config = self.env['mail.template'].sudo().search([('name','=','Leave Reminder')], limit=1)
                            mail_obj = self.env['mail.mail']
                            if config:
                                values = config.generate_email(self.id)
                                mail = mail_obj.create(values)
                                if mail:
                                    mail.send()
                                return True
        return

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
    balance = fields.Monetary(string='Loan Balance', currency_field='currency_id', compute='_get_balance', store=True)
    currency_id = fields.Many2one(related='name.user_id.company_id.currency_id', store=True)
    amount_total = fields.Monetary(compute='_total_naira',
        string='Total Amount', readonly=True, store=True)
    
    loan_line_ids = fields.One2many(
        comodel_name='loan.req',
        inverse_name='employee_id')
    
    loan_amt = fields.Monetary(
        string='Loan Amount')

    @api.model
    def create(self, values):
        req = self.search([('name','=',values['name']),('state','!=','paid')])
        if not req:
            return super(LoanRequest, self).create(values)
        else:
            raise ValidationError('You cannot have more than one loan request.')

    @api.depends('state', 'loan_line_ids', 'loan_line_ids.loan_amount', 'loan_line_ids.loan_paid')
    def _get_balance(self):
        for request in self:
            request.balance = sum(request.loan_line_ids.mapped('loan_amount')) - sum(request.loan_line_ids.mapped('loan_paid'))
    
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
    
    loan_paid = fields.Monetary(string='Amount Paid')
    currency_id = fields.Many2one(related='employee_id.currency_id', store=True)
    
    employee_id = fields.Many2one('loan.request', 'Employee', invisible=True)
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), 
        ('reject','Rejected'), ('paid','Paid'), ('confirm','Confirmed')],
        related='employee_id.state', store=True)
        
    
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
    def _check_line_manager(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.name:
            raise UserError(_('Only your line manager can approve your leave request.'))
    
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
        if self.state in ['submit']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_hr_line_manager')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Travel request from {} has been made".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_approve(self):
        self._check_line_manager()
        self.write({'state': 'approve'})
        self.linemanager_sign = self._uid
        self.linemanager_date = date.today()
        if self.state in ['approve']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_admin_finance_officer')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Travel request from {} has been approved by line manager".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def send_vehicle_request_done_message(self):
        if self.state in ['validate']:
            config = self.env['mail.template'].sudo().search([('name','=','travel request approved')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
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
        if self.state in ['validate']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Travel request from {} has been Validated by Finance".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        self.ceo_sign = self._uid
        self.ceo_date = date.today()
        self.send_vehicle_request_done_message()
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
            self.total_unit_price += line.amount
            
class TravelAccount(models.Model):
    _name = 'ninas.travel.account'
    
    travel_request_id =fields.Many2one(
        comodel_name='travel.request')
    
    type = fields.Char(string='Type Of Expense')
    account_id = fields.Many2one(
        comodel_name='account.account', string='General Ledger')
    grant = fields.Char(string='Grant')
    unit = fields.Integer(string='Unit(s)')
    unit_price = fields.Float(string='Unit Price')
    amount = fields.Float(string='Sub Amount', readonly=True, compute='_sub_amount')

    @api.depends('unit','unit_price')
    def _sub_amount(self):
        amount = 0.0
        for self in self:
            self.amount = self.unit_price * self.unit
    
class Hrrecruitment(models.Model):
    _name = 'ninas.hr.recruitment'
    _description = 'NiNAS HR Recruitment'
    _inherit = 'hr.applicant'

    name = fields.Char(string='Application ID')
    
    partner_first_name = fields.Char(string='First Name', required=0)
    partner_last_name = fields.Char(string='Last Name', required=0)
    #partner_phone
    #partner_mobile
    partner_work = fields.Char(string='Work', required=0)
    mode_of_contact = fields.Selection([('home','Home'),('mobile','Mobile'),('work','Work')], 
        string="Preferred mode of contact",
        track_visibility='onchange')
    partner_address = fields.Char(string='Address')
    partner_sub_address = fields.Char(string='Where are you living now if not at this address')

    job_discovery = fields.Selection([('newspaper','Newspaper'),('website', 'Website'), ('word of mouth','Word of Mouth'), ('others','Others')],
        string='How did you hear about this post',
        track_visibility='onchange')

    referee1 = fields.Char(string="Referee")
    referee1_position = fields.Char(string="Referee Position")
    referee1_email = fields.Char(string="Referee Email")
    ref1_contact_before_interview = fields.Selection([('no','No'),('yes', 'Yes')],
        string='May we contact this person before your interview')
    ref1_contact_before_offer = fields.Selection([('no','No'),('yes', 'Yes')],
        string='May we contact this person before your offer')
    
    referee2 = fields.Char(string="Referee")
    referee2_position = fields.Char(string="Referee Position")
    referee2_email = fields.Char(string="Referee Email")
    ref2_contact_before_interview = fields.Selection([('no','No'),('yes', 'Yes')],
        string='May we contact this person before your interview')
    ref2_contact_before_offer = fields.Selection([('no','No'),('yes', 'Yes')],
        string='May we contact this person before your offer')

    last_position = fields.Char(string="Position Held / Job Title")
    employer_name = fields.Char(string="Employer Name (organisation, company, etc")
    employed_from = fields.Char(string="Date Employed From", readonly=1)
    employed_to = fields.Char(string="Date Employed To", readonly=1)
    previous_work_address = fields.Char(string="Address or Work Location")
    reason_for_leaving = fields.Char(string="Reason for leaving / wanting to leave")
    notice_period = fields.Char(string="How much notice must you give your present employer")
    main_responsibilities = fields.Char(string="Describe your main responsibilities")

    prev_employment_ids = fields.One2many(comodel_name='ninas.prev.employment',
        inverse_name='prev_employment_id')

class PreviousEmployment(models.Model):
    _name = 'ninas.prev.employment'

    prev_employment_id = fields.Many2one(comodel_name='hr.applicant')
    job_title = fields.Char(string="Position Held / Job Title")
    prev_emp_name = fields.Char(string="Employer Name (organisation, company, etc")
    emp_from = fields.Char(string="Date Employed From", readonly=1)
    emp_to = fields.Char(string="Date Employed To", readonly=1)
    leaving = fields.Char(string="Reason for leaving / wanting to leave")

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
    
    state = fields.Selection(
        [('new','New'), ('validate','HR Approved'), ('approve','Line Manager Approved'), ('reject','Rejected')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
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
        string='Position'
        )
    provider = fields.Many2one(
        comodel_name = 'res.partner',
        string='Provider',
        required=1
        )
    training_date_end = fields.Datetime(
        string = 'Training End Date'
        )
    #in case training lasts for days/weeks -- else, duration will be set to less than 20 hours
    training_start_date = fields.Datetime(
        string= 'Training Start Date'
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
    
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'validate'})
        return {}
    
    @api.multi
    def button_approve_lm(self):
        self.write({'state': 'approve'})
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
class AdvanceRequest(models.Model):
    _name = 'ninas.advance_request'
    _description = 'Advance Request Form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
#    _sql_constraints = [('student_uniq',
#                         'UNIQUE(name)',
#                         'Student name must be unique!')]
#    _inherit = 'mail.thread'
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation'), ('confirmed','Payment Confirmed')],
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
    
    @api.multi
    def button_confirm_payment(self):
        self.write({'state': 'confirmed'})
        return {}
    
class MissionReport(models.Model):
    _name = 'ninas.mission_report'
    _description = 'Back-to-office Mission Report'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Approved')],
        string='Status',
        default='new',
        track_visibility='onchange')
    #link to actual employee_id
    employee_name = fields.Many2one(
        comodel_name="hr.employee",
        string='Name', required=True)
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
    purpose = fields.Text(
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
    signature = fields.Many2one(comodel_name = 'res.users', string='Signature', readonly=True)
    
    date = fields.Date(
        string= 'Date',
        readonly=1
        )
    
    travel_request_id = fields.Many2one(comodel_name="travel.request", string='Travel Request', required=False)
    
    @api.multi
    def button_reset(self):
        self.write({'state': 'new'})
        return {}
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        self.signature = self._uid
        self.date = date.today()
        if self.state in ['submit']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_hr_line_manager')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Travel request from {} has been made".format(self.employee_name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_approve(self):
        self._check_line_manager()
        self.write({'state': 'approve'})
        if self.state in ['approve']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_admin_finance_officer')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Mission Report from {} has been approved by line manager".format(self.employee_name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
    @api.multi
    def button_validate(self):
        self.write({'state': 'validate'})
        if self.state in ['validate']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Mission Report from {} has been Validated by Finance".format(self.employee_name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
    @api.onchange('travel_request_id')
    def _onchange_partner_id(self):
        self.employee_name = self.travel_request_id.name
        self.position = self.travel_request_id.name.job_id.name
        self.places = self.travel_request_id.destination_place
        self.purpose = self.travel_request_id.purpose
        return {}
    
    @api.multi
    def _check_line_manager(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.employee_name:
            raise UserError(_('Only your line manager can approve your leave request.'))
    
class NinasBankVoucher(models.Model):
    _name = 'ninas.bank_voucher'
    _description = 'Bank Payment Voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    def _default_employee(self):
        self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)])
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    #link to actual employee_id
    employee_id = fields.Many2one(
        comodel_name = 'res.partner',
        string ='Name of Payee',
        required=0)
    
    method = fields.Selection(
        [('cash','Cash'),('chq','Cheque'),('O_T','Online Transfer'),('other','Other'),],
        string='Payment Method',
        required=1
        )
    chq_number = fields.Char(
        string='Reference',
        required=0
        )
    voucher_number = fields.Char(
        string='Voucher Number', readonly=False, required=True, index=True, copy=False, default='New')
    item_date = fields.Date(
        string = 'Date', default=date.today(),
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
        required=0
        )
    fund_code = fields.Char(
        string ='Fund Code'
        )
    budget_line = fields.Char(
        string = 'Activity/Budget Line Code'
        )
    account_code = fields.Many2one(
        comodel_name = 'account.account',
        string= 'Account Code'
        ) 
    
    currency_id = fields.Many2one('res.currency', 'Currency', required=True,\
        default=lambda self: self.env.user.company_id.currency_id.id)
    
    amount = fields.Monetary(
        string = 'Amount (NGN)'
        )
    
    total = fields.Monetary(
        string='Total Amount',compute='_total_unit',
        store=True, readonly=True
        )
    
    prepared = fields.Many2one(comodel_name='hr.employee',
        string='Prepared by', default=_default_employee, 
        required=0
        )
    reviewed = fields.Many2one(comodel_name='res.users',
        string ='Reviewed by'
        )
    authorised = fields.Many2one(comodel_name='res.users',
        string = 'Authorised Manager/Signatory'
        )
    account_number = fields.Char(
        string= 'Account Number',
        ) 
    tin = fields.Char(
        string = 'TIN', related="employee_id.vendor_tin"
        )
    bank = fields.Char(
        string ='Bank Name'
        )
    signature = fields.Char(
        string = 'Signature'
        )
    date_prepared = fields.Date(
        string= 'Date', default=date.today()
        )
    date_reviewed = fields.Date(
        string= 'Date'
        )
    date_authorised = fields.Date(
        string= 'Date'
        )
    date_sign = fields.Date(
        string= 'Date'
        )
    bank_voucher = fields.One2many(
        comodel_name='bank.voucher',
        inverse_name='bank_voucher_id',
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
        self.date_reviewed = date.today()
        self.reviewed = self._uid
        return {}
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        self.date_authorised = date.today()
        self.authorised = self._uid
        return {}
    
    @api.model
    def create(self, vals):
        if vals.get('voucher_number', 'New') == 'New':
            vals['voucher_number'] = self.env['ir.sequence'].next_by_code('ninas.bank_voucher') or '/'
        return super(NinasBankVoucher, self).create(vals)
    
    @api.depends('bank_voucher.amount')
    def _total_unit(self):
        total_unit_price = 0.0
        for line in self.bank_voucher:
            self.total += line.amount
    
class BankVoucher(models.Model):
    _name = 'bank.voucher'
    
    def _default_employee(self):
        self.env['hr.employee'].search([('user_id','=',self.env.uid)])
        return self.env['hr.employee'].search([('user_id','=',self.env.uid)])
    
    bank_voucher_id = fields.Many2one(
        comodel_name = 'ninas.bank_voucher',
        string ='Bank Voucher')
    
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee', default=_default_employee)
    
    item_date = fields.Date(
        string = 'Date', default=date.today(),
        required=1
        )
    item = fields.Char(
        string='Item (Description)',
        required=1
        )
    ref_number = fields.Char(
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
    account_code = fields.Many2one(
        comodel_name = 'account.account',
        string= 'Account Code'
        ) 
    amount = fields.Float(
        string = 'Amount (NGN)',
        required=1
        )
    #total = fields.Integer(
     #   string='Total Amount',
      #  )
    
    
class NinasExpenseClaim(models.Model):
    _name = 'ninas.expense_claim'
    _description = 'Expense Claim form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']

    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected'), ('validate','Validated'), ('ceo','CEO Validation'), ('confirmed','Payment Confirmed')],
        string='Status',
        default='new',
        track_visibility='onchange')
    #link to actual employee_id
    employee_id = fields.Many2one(
        comodel_name = 'hr.employee',
        string ='Name of Payee',
        required=1
        )
    employee_code = fields.Char(
        related='employee_id.employee',
        string='Employee Code'
        )
    ref_number = fields.Integer(
        string='Ref. No. (Receipts to be numbered serially)',
        )
    amount_received = fields.Float(
        string='Amount Received From Finance'
        )
    prepared = fields.Char(
        string='Prepared by',
        readonly=True
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
        readonly=True
        )
    reviewed = fields.Char(
        string ='Reviewed by',
        readonly=True
        )
    authorised = fields.Char(
        string = 'Authorised Manager/Signatory',
        readonly=True
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
    date_prepared = fields.Date(
        string= 'Date',
        readonly=True
        )
    date_reviewed = fields.Date(
        string= 'Date',
        readonly=True
        )
    date_authorised = fields.Date(
        string= 'Date',
        readonly=True
        )
    
    date = fields.Date(
        string= 'Date',
        readonly=True
        )
    
    description = fields.Text(
        string='Description',
        required=True
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
        self.prepared = self._uid
        self.date_prepared = date.today()
        return {}
    
    @api.multi
    def button_approve(self):
        self.write({'state': 'approve'})
        self.reviewed = self._uid
        self.date_reviewed = date.today()
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        return {}
    
    @api.multi
    def button_validate(self):
        self.write({'state': 'validate'})
        self.authorised = self._uid
        self.date_authorised = date.today()
        return {}
    
    @api.multi
    def button_ceo(self):
        self.write({'state': 'ceo'})
        return {}
    
    @api.multi
    def button_confirm_payment(self):
        self.write({'state': 'confirmed'})
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
        string='Item',
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
    
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Application ID',
        readonly=False)
    
    agreement = fields.Boolean(
        string='I have read and concur with NiNAS’s Code of Conduct (Sections 1-7).',
        required=True
        )
    date = fields.Char(
        )
    date_today = fields.Char(
        )
    description = fields.Text(
        )
    name = fields.Many2one(
        comodel_name='res.users',
        string='Employee Printed name:',
        readonly=False)
    date_signed = fields.Char(
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
    
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Application ID',
        readonly=False)
    
    partner_id = fields.Many2one(comodel_name='res.partner', related='application_id.partner_id', string='Applicant', readonly=True)
    
    number = fields.Char(
        string='Number', related="application_id.lab_number")
    street = fields.Char(
        string='Street', related="application_id.lab_street")
    city = fields.Char(
        string='City', related="application_id.lab_city")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related="application_id.lab_state_id")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related="application_id.lab_country_id")
    
    agreement = fields.Boolean(
        string='I have read and concur with NiNAS’s Code of Conduct (Sections 2-7).',
        required=True
        )
    date = fields.Date(default=date.today()
        )
    date_today = fields.Date(
        )
    description = fields.Text(
        )
    name = fields.Many2one('res.users',
        string='Name of Institution or Person:', default=lambda self: self.env.user, readonly=True)
    
    printed_name = fields.Many2one('res.users',readonly=True,
        string='Printed Name')
    
    location = fields.Char(
        string='Location')
    date_signed = fields.Date(
        string='Date',
        readonly=True)

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.printed_name = self._uid
        self.date_signed = date.today()
        '''
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_director_accreditation')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Assessor {} has signed Conflict of Interest Form and is awaiting approval".format(self.name.name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
        '''
    
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
    
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket',
        string='Application ID',
        readonly=False)
    
    partner_id = fields.Many2one(comodel_name='res.partner', related='application_id.partner_id', string='Applicant', readonly=True)
    
    number = fields.Char(
        string='Number', related="application_id.lab_number")
    street = fields.Char(
        string='Street', related="application_id.lab_street")
    city = fields.Char(
        string='City', related="application_id.lab_city")
    state_id = fields.Many2one("res.country.state", string='State', ondelete='restrict', related="application_id.lab_state_id")
    country_id = fields.Many2one('res.country', string='Country', ondelete='restrict', related="application_id.lab_country_id")
    
    
    name = fields.Many2one('res.users',
        string='Name of Institution or Person:', default=lambda self: self.env.user, readonly=True)
    location = fields.Char(
        string='Location',required=False)
    name_rep = fields.Many2one('res.users',
        string='Name of Person:',required=True, default=lambda self: self.env.user, readonly=True)
    
    date = fields.Date(
        )
    description = fields.Text(
        )
    
    signed = fields.Many2one('res.users',readonly=True,
        string='Signed')

    date_signed = fields.Date(
        string='Date',
        readonly=True)

    @api.multi
    def button_accept(self):
        self.write({'state': 'accept'})
        self.signed = self._uid
        self.date_signed = date.today()
        '''
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_director_accreditation')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Assessor {} has signed Confidentiality Form and is awaiting approval".format(self.name.name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
        '''
    
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
        required=True, default = date.today()
        )
    ref_no=fields.Char(
        string='Ref No'
        )
    name_of_payee=fields.Many2one(
        comodel_name='hr.employee',
        string='Name of Payee',
        required=True
        )
    amount_naira=fields.Integer(
        string='Amount (Naira)',
        required=True
        )
    description=fields.Text(
        string='Description of Payment',
        required=True
        )
    accounts_charge=fields.Many2one(
        comodel_name='account.account',
        string='Account Chargeable'
        )
    grant=fields.Char(
        string='Grant'
        )
    budget_line=fields.Char(
        string='Budget line'
        )
    gl=fields.Char(
        string='General Ledger'
        )
    prepared_by=fields.Many2one(
        comodel_name="res.users",
        string='Prepared by',
        readonly=True
        )
    approved_by=fields.Many2one(
        comodel_name="res.users",
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

    employee_id= fields.Many2one(
        comodel_name = 'hr.employee',
        required=1,
        )
    
    employee_code = fields.Char(
        related='employee_id.employee',
        string='Employee Code',
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

    org = fields.Many2one(
        comodel_name = 'res.partner',
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
        readonly=0
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
    
      
class AssessmentPlan(models.Model):
    _name = 'ninas.assessment_plan'
    _description = 'Assessment Plan Form'
    
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Accreditation ID',
        required=True,
        track_visibility='onchange',)
    
    reference_number = fields.Char(string='Reference Number', readonly=True, required=True, index=True, copy=False, default='New') #auto-sgenerated?
    organisation = fields.Char(related='application_id.laboratory_legal_name', string='Organisation', readonly=1)
    contact_person = fields.Char(related='application_id.partner_name', string='Contact Person', required=1)
    address = fields.Char(string='Address')
    
    lab_number = fields.Char(related='application_id.lab_number', string='Number')
    lab_street = fields.Char(related='application_id.lab_street', string='Street')
    lab_city = fields.Char(related='application_id.lab_city', string='City')
    lab_state_id = fields.Many2one(related='application_id.lab_state_id',comodel_name="res.country.state", string='State')
    lab_country_id = fields.Many2one(related='application_id.lab_country_id',comodel_name='res.country', string='Country')
    
    telephone = fields.Char(related='application_id.telephone_number', string='Telephone')
    company_rep = fields.Char(related='application_id.partner_id.name', string='Company Representative', required=1)
    
    assessment_date = fields.Date(string='Assessment Date', required=0)
    lead_assessor = fields.Many2one(related='application_id.lead_assessor_id', comodel_name='hr.employee', string='Lead Assessor')
    technical_assessor = fields.Many2one(related='application_id.tech_assessor_id',comodel_name='hr.employee', string='Technical Assessor')
    
    assessment_date_from = fields.Date(related='application_id.assessment_date_from',track_visibility='onchange')
    assessment_date_to = fields.Date(related='application_id.assessment_date_to',track_visibility='onchange')
    assessment_number_of_days = fields.Integer(related='application_id.assessment_number_of_days')
    
    day1_ids = fields.One2many(
        comodel_name='ninas.assessment.plan.activity',
        inverse_name='assessment_plan_id')
    day2_ids = fields.One2many(
        comodel_name='ninas.assessment.plan.activity',
        inverse_name='assessment_plan_id_2')
    day3_ids = fields.One2many(
        comodel_name='ninas.assessment.plan.activity',
        inverse_name='assessment_plan_id_3')
    day4_ids = fields.One2many(
        comodel_name='ninas.assessment.plan.activity',
        inverse_name='assessment_plan_id_4')
    # @api.depends('reference_number')
    # def generate_ref(self):
    #     added = 0
    #     for ref in self:
    #         added+=1
    #         ref.reference_number = reference_number + added
    
    @api.model
    def create(self, vals):
        if vals.get('reference_number', 'New') == 'New':
            vals['reference_number'] = self.env['ir.sequence'].next_by_code('ninas.assessment_plan') or '/'
        return super(AssessmentPlan, self).create(vals)
    
class AssessmentActivity(models.Model):
    _name = 'ninas.assessment.plan.activity'
    assessment_plan_id = fields.Many2one(comodel_name='ninas.assessment_plan')
    assessment_plan_id_2 = fields.Many2one(comodel_name='ninas.assessment_plan')
    assessment_plan_id_3 = fields.Many2one(comodel_name='ninas.assessment_plan')
    assessment_plan_id_4 = fields.Many2one(comodel_name='ninas.assessment_plan')
    start_time = fields.Float(string='Start Time')
    end_time = fields.Float(string='End Time')
    activity = fields.Char(string='Activity') 
    
    
    
class DecisionForm(models.Model):
    _name = 'ninas.decision_form'
    _description = 'Decision Form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    #this should pull the application info (rep, assessor, institution)
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Accreditation ID',
        required=True,
        track_visibility='onchange',)
    
    partner_id = fields.Many2one(comodel_name='res.partner', related='application_id.partner_id', string='Applicant', readonly=True)
    
    ref = fields.Char(
        string='Reference No.',related='application_id.name',
        required=1)
    
    #link to actual employee_id
    assessor_id = fields.Many2one(
        comodel_name = 'hr.employee',
        related='application_id.lead_assessor_id',
        string ='Assessor Name',
        readonly=1)
    
    representative = fields.Char(
        related='application_id.partner_id.name',
        string='Name of Institution Representative',
        store=True,
        readonly=1)
    
    scope = fields.Char(
        string='Accreditation Scope',
        readonly=1)
    
    institution_name = fields.Char(
        related='application_id.laboratory_legal_name',
        string='Name of Institution',
        store=True,
        readonly=1)
    
    assess_type = fields.Many2one(
        related='application_id.assessment_type_id',
        string ='Type of Assessment', readonly=1)
    
    assessment_date = fields.Date(
        related='application_id.assessment_date',
        string="Accreditation Date",
        track_visibility='onchange')
    
    assessment_date_from = fields.Date(related='application_id.assessment_date_from',track_visibility='onchange')
    assessment_date_to = fields.Date(related='application_id.assessment_date_to',track_visibility='onchange')
    assessment_number_of_days = fields.Integer(related='application_id.assessment_number_of_days', string='Number of Days', store=True, track_visibility='onchange')
    
    la_recommendation = fields.Text(
        string="Lead Assessor's Recommendation",
        required=0)
    
    aac_recommendation = fields.Text(
        string="AAC Recommendation",
        required=0)
    da_recommendation = fields.Text(
        string="Director of Accreditation's Recommendation",
        required=0)
    
    #today's date on change (save)
    date = fields.Date(
        string= 'Date', default=date.today())
    
    ceo = fields.Selection(
        [('1','Unconditional accreditation/renewal of accreditation to be granted'),
        ('2','Accreditation/renewal of accreditation to be deferred until all non-conformances have been cleared'),
        ('3','Accreditation/renewal of accreditation is not recommended'),
        ('4','For re-assessment only: Suspension of accreditation status or part thereof')],
        string = 'Reommendation')
    
    note = fields.Char(
        default='The period of suspension shall not extend beyond the date of expiry of the Certificate of Accreditation',
        readonly=1)
    
    state = fields.Selection(
        [
            #('la_recommendation', "Lead Assessor's Recommendation"), ('aac_recommendation','AAC Recommendation'), 
            ('da_recommendation',"Director of Accreditation's Recommendation")],
        string='Status',
        default='da_recommendation',
        track_visibility='onchange')
    
    invoice_count = fields.Integer(compute="_invoice_count", string="Invoices", store=False)
    checklist_count = fields.Integer(compute="_checklist_count",string="Checklist", store=False)
    car_count = fields.Integer(compute="_car_count",string="C.A.R")
    
    confidentiality_count = fields.Integer(compute="_confidentiality_count",string="Confidentiality", store=False)
    conflict_count = fields.Integer(compute="_conflict_count",string="Checklist", store=False)
    recommendation_count = fields.Integer(compute="_recommendation_count",string="Recommendation", store=False)
    update_record = fields.Boolean(string='Update')
    overule = fields.Boolean(string="overule", default=False)
    submitted_to_ceo = fields.Boolean(string="Submitted To CEO", default=False)
    approved_by_ceo = fields.Boolean(string="Approved By CEO", default=False)
    
    @api.multi
    def button_awaiting_approval(self):
        sub = self.env['ninas.recommendation.form'].search([('application_id','=',self.application_id.id), ('partner_id', '=', self.partner_id.id), ('state','=','done'),], limit=3)
        print(sub)
        if self.recommendation_count == 0:
            raise Warning('Recommendation Forms has not been Filled!')
        elif self.recommendation_count < 3:
            raise Warning('Recommendation Forms has not been Completely Filled!')
        else:
            for line in sub:
                mylist = len(sub)
                print(mylist)
                if mylist >= 3:
                    if self.ceo == '1':
                        self.application_id.button_approved_app()
                        self.approved_by_ceo = True
                    else:
                        self.application_id.button_reject_app()
                        #self.overule = True
                        raise Warning('Recommendation has not been Approved for this Application')
                else:
                    raise Warning('Recommendation Form for this Application has being confirmed(Done)')
            return {}
    
    '''
    @api.multi
    def button_awaiting_approval(self):
        sub = self.env['ninas.recommendation.form'].search([('application_id','=',self.application_id.id), ('partner_id', '=', self.partner_id.id), ('state','=','done'),], limit=3)
        print(sub)
        if self.recommendation_count == 0:
            raise Warning('Recommendation Forms has not been Filled!')
        elif self.recommendation_count < 3:
            raise Warning('Recommendation Forms has not been Completely Filled!')
        else:
            for line in sub:
                mylist = len(sub)
                print(mylist)
                if mylist >= 3:
                    if line.recommendation == '1' and self.ceo == '1':
                        self.application_id.button_approved_app()
                        self.approved_by_ceo = True
                        subject = "CEO has Approved for {} ".format(self.display_name)
                        partner_ids = []
                        for partner in self.message_partner_ids:
                            partner_ids.append(partner.id)
                        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
                    else:
                        self.overule = True
                        raise Warning('Recommendation has not been Approved for this Application')
                else:
                    raise Warning('Recommendation Form for this Application has being confirmed(Done)')
            return {}
    '''
    
    @api.multi
    def button_overule_approval(self):
        if self.overule == True:
            self.application_id.button_approved_app()
            
    @api.multi
    def button_submit_decision(self):
        self.submitted_to_ceo = True
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_ceo')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Decision Form for {} has been created and awaiting Approval".format(self.application_id.display_name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    
    @api.multi
    def button_update_record(self):
        self.update_record = True
        return {}
    
    @api.multi
    def _invoice_count(self):
        oe_invoice = self.env['account.invoice']
        for inv in self:
            invoice_ids = self.env['account.invoice'].search([('partner_id', '=', inv.partner_id.id)])
            invoices = oe_invoice.browse(invoice_ids)
            invoice_count = 0
            for inv_id in invoices:
                invoice_count+=1
            inv.invoice_count = invoice_count
        return True

    @api.multi
    def _checklist_count(self):
        oe_checklist = self.env['checklist.ticket']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_checklist.search(domain)
            pres = oe_checklist.browse(pres_ids)
            checklist_count = 0
            for pr in pres:
                checklist_count+=1
            pa.checklist_count = checklist_count
        return True
    
    @api.multi
    def _confidentiality_count(self):
        oe_confidentiality = self.env['ninas.confidentiality']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_confidentiality.search(domain)
            pres = oe_confidentiality.browse(pres_ids)
            confidentiality_count = 0
            for pr in pres:
                confidentiality_count+=1
            pa.confidentiality_count = confidentiality_count
        return True
    
    @api.multi
    def _conflict_count(self):
        oe_conflict = self.env['ninas.conflict.interest']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_conflict.search(domain)
            pres = oe_conflict.browse(pres_ids)
            conflict_count = 0
            for pr in pres:
                conflict_count+=1
            pa.conflict_count = conflict_count
        return True
    
    
    @api.multi
    def _car_count(self):
        car_rep = self.env['car.report']
        for car in self:
            domain = [('partner_id', '=', car.partner_id.id)]
            car_ids = car_rep.search(domain)
            cars = car_rep.browse(car_ids)
            car_count = 0
            for ca in cars:
                car_count+=1
            car.car_count = car_count
        return True
    
    @api.multi
    def _recommendation_count(self):
        car_rep = self.env['ninas.recommendation.form']
        for car in self:
            domain = [('partner_id', '=', car.partner_id.id)]
            car_ids = car_rep.search(domain)
            cars = car_rep.browse(car_ids)
            car_count = 0
            for ca in cars:
                car_count+=1
            car.recommendation_count = car_count
        return True
    
    @api.multi
    def button_aac(self):
        self.write({'state': 'aac_recommendation'})
        return {}
    
    @api.multi
    def button_da(self):
        self.write({'state': 'da_recommendation'})
        return {}
    
    @api.multi
    def open_customer_invoices(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_refund_out_tree').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_checklist_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_checklist_ticket_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_confidentiality_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_confidentiality_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_conflict_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_conflict_of_interest_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_car(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_car_report_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_recommendation_form(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_recommendation_form_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
class AppraisalForm(models.Model):
    _name='ninas.appraisal'
    _description='Appraisal Form'

   # employee_id=fields.Many2one(
    #    comodel_name='hr.employee',
    #    string='Employee')

    appraisee=fields.Many2one(
        comodel_name='hr.employee',
        string='Employee')

    appraisee_title=fields.Char(
        string='Job Title',
        related='appraisee.job_id.name',
        readonly=True)

    appraiser=fields.Many2one(
        comodel_name='hr.employee',
        string='Appraiser')
    
    appraiser_title=fields.Char(
        string='Job Title',
        related='appraiser.job_id.name',
        readonly=True)

    reviewer=fields.Many2one(
        comodel_name='hr.employee',
        string='Reviewer')

    reviewer_title=fields.Char(
        string='Job Title',
        related='reviewer.job_id.name',
        readonly=True)

    objectives=fields.Text(
        string='Review of Objectives Achieved, Partially Achieved and Why')

    performance=fields.Text(
        string='Review of Personal Performance')

    superior=fields.Boolean(
        string='Superior')

    acceptable=fields.Boolean(
        string='Fully Acceptable')

    incomplete=fields.Boolean(
        string='Incomplete')

    unsatisfactory=fields.Boolean(
        string='Unsaticfactory')

    reason=fields.Text(
        string='Reason for Rating')

    appraiser_comments=fields.Text(
        string='Appraiser Comments')

    appraisee_comments=fields.Text(
        string='Appraisee Comments')
    
    reviewer_comments=fields.Text(
        string='Reviwer Comments')
    
    date=fields.Date(
        string='Date')

class VehicleFuelRequestForm(models.Model):
    _name='ninas.vehicle.fuel.request'
    _description='Vehicle Fuel Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    name = fields.Many2one(comodel_name="hr.employee",string='Driver', default=_get_employee_id, required=True)
    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string='Vehicle')
    vehicle_no = fields.Char(string='Vehicle No')
    date_request=fields.Date(
        string='Date Requested')
    price_per_litre = fields.Float(string='Price per litre')
    no_of_litre = fields.Float(string='No. of litre')
    
    price_subtotal = fields.Float(string='Estimated Amount', compute='_total_unit', readonly=True)
    
    authorized_sign = fields.Many2one(
        comodel_name="res.users",
        string='Signature')
    
    sign_date = fields.Date(
        string='Date')
    
    @api.depends('price_per_litre','no_of_litre')
    def _total_unit(self):
        self.price_subtotal = self.price_per_litre * self.no_of_litre
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        if self.state in ['submit']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_logistics','ninasmain.group_admin_finance_officer')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Vehicle request from {} has been made".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_approve(self):
        self._check_line_manager()
        self.write({'state': 'approve'})
        self.authorized_sign = self._uid
        self.sign_date = date.today()
        self.send_vehicle_request_done_message()
        if self.state in ['approve']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_drivers')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Vehicle request from {} has been approved".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def send_vehicle_request_done_message(self):
        if self.state in ['approve']:
            config = self.env['mail.template'].sudo().search([('name','=','vehicle assigned')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        if self.state in ['reject']:
            config = self.env['mail.template'].sudo().search([('name','=','vehicle request rejected')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
        return {}
    
    @api.multi
    def _check_line_manager(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.name:
            raise UserError(_('Only your line manager can approve your leave request.'))
    
class VehicleRequestForm(models.Model):
    _name='ninas.vehicle.request'
    _description='Vehicle Request'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    state = fields.Selection(
        [('new','New'),('submit', 'Submitted'), ('approve','Approved'), ('reject','Rejected')],
        string='Status',
        default='new',
        track_visibility='onchange')
    
    name=fields.Many2one(
        comodel_name="hr.employee",
        string='Name', default=_get_employee_id)
    
    time_requires=fields.Datetime(
        string='Time Required')
    
    date_request=fields.Date(
        string='Date')
    
    purpose_requested=fields.Text(
        string='Purpose')
    
    purpose_official=fields.Boolean(
        string='Official')
    
    purpose_personal=fields.Boolean(
        string='Personal')
    
    address = fields.Text(
        string='Address')
    
    vehicle_id = fields.Many2one(comodel_name="fleet.vehicle", string='Vehicle')
    vehicle_no = fields.Char(
        string='Assigned Vehicle No')
    
    drivers_name = fields.Many2one(
        comodel_name="hr.employee",
        string='Drivers Name')
    
    authorized_sign = fields.Many2one(
        comodel_name="res.users",
        string='Signature')
    
    sign_date = fields.Date(
        string='Date') 
    
    @api.multi
    def button_reset(self):
        self.write({'state': 'new'})
        return {}
    
    @api.multi
    def button_submit(self):
        self.write({'state': 'submit'})
        if self.state in ['submit']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_logistics')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Vehicle request from {} has been made".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def button_approve(self):
        self._check_line_manager()
        self.write({'state': 'approve'})
        self.authorized_sign = self._uid
        self.sign_date = date.today()
        self.send_vehicle_request_done_message()
        if self.state in ['approve']:
            group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_drivers')
            user_ids = []
            partner_ids = []
            for user in group_id.users:
                user_ids.append(user.id)
                partner_ids.append(user.partner_id.id)
            self.message_subscribe_users(user_ids=user_ids)
            subject = "Vehicle request from {} has been approved".format(self.name.name)
            self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
            return False
        return {}
    
    @api.multi
    def send_vehicle_request_done_message(self):
        if self.state in ['approve']:
            config = self.env['mail.template'].sudo().search([('name','=','vehicle assigned')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
        return {}
    
    @api.multi
    def button_reject(self):
        self.write({'state': 'reject'})
        if self.state in ['reject']:
            config = self.env['mail.template'].sudo().search([('name','=','vehicle request rejected')], limit=1)
            mail_obj = self.env['mail.mail']
            if config:
                values = config.generate_email(self.id)
                mail = mail_obj.create(values)
                if mail:
                    mail.send()
        return {}
    
    @api.multi
    def _check_line_manager(self):
        current_employee = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if current_employee == self.name:
            raise UserError(_('Only your line manager can approve your leave request.'))
        
class AssessorFormAttachment(models.Model):
    _name = 'assessor.form.attachment'
    
    name = fields.Char(string='Form Name', required=True)
    description = fields.Char(string='Form Description', required=True)
    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        string='Attachment', required=True)
    
class RecommendationForm(models.Model):
    _name='ninas.recommendation.form'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'portal.mixin']
    
    application_id = fields.Many2one(
        comodel_name='helpdesk.ticket', 
        string='Accreditation ID',
        required=True,
        track_visibility='onchange',)
    
    partner_id = fields.Many2one(comodel_name='res.partner', related='application_id.partner_id', string='Applicant', readonly=True)
    
    name = fields.Char(
        related='application_id.laboratory_legal_name',
        string="Name of Institution or Lab",
        track_visibility='onchange')
    
    address_of_institution= fields.Char(
        string='Address of Institution or Lab',
        track_visibility='onchange')
    
    institution_number = fields.Char(
        related='application_id.lab_number',
        string='Number')
    institution_street = fields.Char(
        related='application_id.lab_street',
        string='Street')
    institution_city = fields.Char(
        related='application_id.lab_city',
        string='City')
    institution_state_id = fields.Many2one("res.country.state", string='State', related='application_id.lab_state_id', ondelete='restrict')
    institution_country_id = fields.Many2one('res.country', string='Country', related='application_id.lab_country_id', ondelete='restrict')
    
    reference_no = fields.Char(
        string="Reference Number",related='application_id.name',
        track_visibility='onchange')
    
    name_of_institution_rep = fields.Char(
        related='application_id.partner_id.name',
        string="Name of Institution Representative",
        track_visibility='onchange')
    
    accreditation_scope = fields.Selection(
        related='application_id.number_of_scopes',
        string="Accreditation Scope",
        track_visibility='onchange')
    
    name_assessor = fields.Many2many(
        related='application_id.assessment_team_ids',
        comodel_name='hr.employee',
        string="Name Assessor(s)",
        track_visibility='onchange')
    
    type_assessment = fields.Selection([('pre_assesment', 'Pre-assesment'), ('initial', 'Initial'), ('re_assesment', 'Re-assesment')],
        string='Type of Assessment', track_visibility='onchange')
    
    assessment_date = fields.Date(
        related='application_id.assessment_date',
        string="Accreditation Date",
        track_visibility='onchange')
    
    assessment_date_from = fields.Date(related='application_id.assessment_date_from',track_visibility='onchange')
    assessment_date_to = fields.Date(related='application_id.assessment_date_to',track_visibility='onchange')
    assessment_number_of_days = fields.Integer(related='application_id.assessment_number_of_days', string='Number of Days', store=True, track_visibility='onchange')
    
    satisfactory_yes = fields.Boolean(string='Yes')
    
    satisfactory_no = fields.Boolean(string='No')
    
    update_record = fields.Boolean(string='Update')
    
    recommendation = fields.Selection(
        [('1','Unconditional accreditation/renewal of accreditation to be granted'),
        ('2','Accreditation/renewal of accreditation to be deferred until all non-conformances have been cleared'),
        ('3','Accreditation/renewal of accreditation is not recommended'),
        ('4','For re-assessment only: Suspension of accreditation status or part thereof')],
        string = 'Recommendation')
    
    further_comment = fields.Text(string='Any other Comment:')
    
    name_sign = fields.Many2one(
        comodel_name='res.users',
        string="Name / Signature",
        track_visibility='onchange', readonly=True)
    
    date = fields.Date(
        string="Date",
        track_visibility='onchange', readonly=True)
    
    state = fields.Selection(
        [('incomplete', "Incomplete"), ('done','Done')],
        string='Status',
        default='incomplete',
        track_visibility='onchange')
    
    checklist_count = fields.Integer(compute="_checklist_count",string="Checklist", store=False)
    car_count = fields.Integer(compute="_car_count",string="C.A.R")
    confidentiality_count = fields.Integer(compute="_confidentiality_count",string="Confidentiality", store=False)
    conflict_count = fields.Integer(compute="_conflict_count",string="Checklist", store=False)
    
    @api.multi
    def button_update_record(self):
        self.update_record = True
        return {}
    
    @api.multi
    def _checklist_count(self):
        oe_checklist = self.env['checklist.ticket']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_checklist.search(domain)
            pres = oe_checklist.browse(pres_ids)
            checklist_count = 0
            for pr in pres:
                checklist_count+=1
            pa.checklist_count = checklist_count
        return True
    
    @api.multi
    def _confidentiality_count(self):
        oe_confidentiality = self.env['ninas.confidentiality']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_confidentiality.search(domain)
            pres = oe_confidentiality.browse(pres_ids)
            confidentiality_count = 0
            for pr in pres:
                confidentiality_count+=1
            pa.confidentiality_count = confidentiality_count
        return True
    
    @api.multi
    def _conflict_count(self):
        oe_conflict = self.env['ninas.conflict.interest']
        for pa in self:
            domain = [('partner_id', '=', pa.partner_id.id)]
            pres_ids = oe_conflict.search(domain)
            pres = oe_conflict.browse(pres_ids)
            conflict_count = 0
            for pr in pres:
                conflict_count+=1
            pa.conflict_count = conflict_count
        return True
    
    
    @api.multi
    def _car_count(self):
        car_rep = self.env['car.report']
        for car in self:
            domain = [('partner_id', '=', car.partner_id.id)]
            car_ids = car_rep.search(domain)
            cars = car_rep.browse(car_ids)
            car_count = 0
            for ca in cars:
                car_count+=1
            car.car_count = car_count
        return True
    
    @api.multi
    def open_checklist_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_checklist_ticket_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_confidentiality_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_confidentiality_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_conflict_ticket(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_conflict_of_interest_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def open_car(self):
        self.ensure_one()
        action = self.env.ref('ninasmain.ninas_car_report_action').read()[0]
        action['domain'] = literal_eval(action['domain'])
        action['domain'].append(('partner_id', 'child_of', self.partner_id.id))
        return action
    
    @api.multi
    def button_done(self):
        if self.recommendation == False:
            raise Warning('Recommendation Form for this Application has being confirmed(Done)')
        else:
            self.name_sign = self._uid
            self.date = date.today()
            self.write({'state': 'done'})
        return {}
    
class DocumentsArchive(models.Model):
    _name='ninas.documents.archive'
    _description='Ninas Documents'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    def _get_employee_id(self):
        employee_rec = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        return employee_rec.id
    
    name = fields.Char(string="Name of Document", track_visibility='onchange', required=True)
    datas_fname = fields.Char('File Name')
    employee_id = fields.Many2one(comodel_name="hr.employee", string='Employee', default=_get_employee_id)
    folder_id = fields.Many2one(comodel_name="ninas.documents.archive.category", string='Folder')
    department_id = fields.Many2one(comodel_name="hr.department", string='Department', related="employee_id.department_id", store=True)
    document_type_id = fields.Many2one(comodel_name="document.type", string='Document Type')
    file = fields.Binary(string='Document', required=True, store=True)
    description = fields.Text(string='Note(s)')
    
    general = fields.Boolean(string="general")
    finance = fields.Boolean(string="Finance")
    hr = fields.Boolean(string="HR")
    accreditation = fields.Boolean(string="Accreditation")
    logistics = fields.Boolean(string="Logistics")
    
    
class DocumentsArchiveCategory(models.Model):
    _name='ninas.documents.archive.category'
    _description='Ninas Folders'
    
    name = fields.Char(string="Folder Name", track_visibility='onchange', required=True)