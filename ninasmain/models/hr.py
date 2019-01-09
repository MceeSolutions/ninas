# -*-coding:utf-8-*-
from odoo import models, fields, api

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
        return {}
    
class JobApp(models.Model):
    _inherit = "hr.applicant"
    
    approved = fields.Boolean(
        string='Approved')
    
    @api.multi
    def button_approve(self):
        self.write({'approved':True})
        return {}   
    