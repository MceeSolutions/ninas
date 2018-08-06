#-*- coding: utf-8 -*-
#@Author: Chuka
#Date 3/08/2018

from odoo import fields, models, api 
import datetime

class AppraisalForm(models.Model):
    _name='ninas.appraisal'
    _description='Appraisal Form'

    employee_id=fields.Char(
        string='Name')

    employee_title=fields.Char(
        string='Job Title')

    appraiser=fields.Char(
        string='Appraiser')
    
    appraisee=fields.Char(
        string='Appraisee')

    appraiser_title=fields.Char(
        string='Job Title')

    reviewer=fields.Char(
        string='Reviewer')

    reviewer_title=fields.Char(
        string='Job Title')

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
