#-*- coding: utf-8 -*-
#@Author: Chuka
#Date 3/08/2018

from odoo import fields, models, api 
import datetime

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
