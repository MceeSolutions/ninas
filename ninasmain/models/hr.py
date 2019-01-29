# -*-coding:utf-8-*-
from odoo import models, fields, api
from email.policy import default
import datetime
from datetime import date, timedelta
from odoo.exceptions import UserError

class EmployeeCategory(models.Model):
    _inherit = 'hr.employee.category'
    
    is_assessor = fields.Boolean(
        string='Assessor?'
        )
    
class JobRec(models.Model):
    _inherit = "hr.job"
    
    state = fields.Selection([
        ('approve', 'Awaiting Approval'),
        ('recruit', 'Recruitment in Progress'),
        ('open', 'Not Recruiting')
    ], string='Status', readonly=True, required=True, track_visibility='always', copy=False, default='approve', help="Set whether the recruitment process is open or closed for this job position.")
    
    survey_id = fields.Many2one(
        'survey.survey', "Additional Form",
        help="Choose an interview form for this job position and you will be able to print/answer this interview from all applicants who apply for this job")
    

    @api.multi
    def button_approve(self):
        self.write({'state': 'recruit'})
        group_id = self.env['ir.model.data'].xmlid_to_object('ninasmain.group_admin_finance_officer')
        user_ids = []
        partner_ids = []
        for user in group_id.users:
            user_ids.append(user.id)
            partner_ids.append(user.partner_id.id)
        self.message_subscribe_users(user_ids=user_ids)
        subject = "Job Position {} has been approved and can hence be published".format(self.name)
        self.message_post(subject=subject,body=subject,partner_ids=partner_ids)
        return False
    

    appliaction_deadline = fields.Date(string="Application Deadline")
    todays_date = fields.Date(string="Todays Date", default = date.today())
    
    @api.multi
    def check_deadline(self):
        if self.appliaction_deadline == self.todays_date:
            self.set_open()
    
    '''
    @api.depends('website_published')
    def _check_ceo_approval(self):
        if self.state == 'approve':
            self.write({'website_published':False})
            raise UserError(_('Job Position must be approved first'))
    '''
    
class JobApp(models.Model):
    _inherit = "hr.applicant"
    
    approved = fields.Boolean(
        string='Approved')
    
    @api.multi
    def button_approve(self):
        self.write({'approved':True})
        return {}   
    