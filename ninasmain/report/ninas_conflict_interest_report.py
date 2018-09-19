# -*- coding: utf-8 -*-

#@author steve
#Date: 6/06/18

from odoo import models, api

import logging


logger = logging.getLogger(__name__)


class ConflictofInterestReport(models.Model):
    _name = 'report.ninasmain.ninas_conflict_interest_report'
    _description = 'Ninas Conflict of Interest Report'
    
    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env['ninas.conflict.interest'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'ninas.conflict.interest',
            'docs': model,
            'data': data,
            }