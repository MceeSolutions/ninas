# -*- coding: utf-8 -*-

from odoo import api, fields, models

class GatewayConfig(models.Model):
    _name = 'gateway.config'
    _description = 'Gateway Config'

    name = fields.Char(
        string='Name of Bank',
        required=True
    )

    url = fields.Char(
        string='URL',
        required=True
    )

    access_code = fields.Char(
        string='Access Code',
        required=True
    )

    username = fields.Char(
        string='Username',
        required=True
    )

    password = fields.Char(
        string='Password',
        required=True
    )

    
