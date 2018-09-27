# -*- coding: utf-8 -*-

#@author steve
#Date: 6/06/18

from odoo import models, api

import logging


logger = logging.getLogger(__name__)


class CodeofConduct(models.Model):
    _name = 'report.ninasmain.ninas_code_conduct_report'
    _description = 'Ninas Code of Conduct Report'
    
    @api.model
    def get_report_values(self, docids, data=None):
        model = self.env['ninas.code.conduct'].browse(docids)
        return {
            'doc_ids': docids,
            'doc_model': 'ninas.code.conduct',
            'docs': model,
            'data': data,
            }