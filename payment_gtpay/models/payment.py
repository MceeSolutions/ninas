# coding: utf-8

import json
import logging

import dateutil.parser
import pytz
from werkzeug import urls

from odoo import api, fields, models, _
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment_gtpay.controllers.main import GTPayController
from odoo.tools.float_utils import float_compare
import hashlib

_logger = logging.getLogger(__name__)


class AcquirerGTPay(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(selection_add=[('gtpay', 'GTPay')])
    gtpay_seller_account = fields.Char(
        'GTPay Merchant ID', groups='base.group_user',
        help='The Merchant ID is used to ensure communications coming from GTPay are valid and secured.')
    gtpay_webpay_seller_account = fields.Char(
        'GTPay WebPay Merchant ID', groups='base.group_user',
        help='The WebPay Merchant ID is used to ensure communications coming from GTPay WebPay are valid and secured.')
    gtpay_hash_key = fields.Char(string='GTPay Hash Key', required_if_provider='gtpay', help='Payment Data Transfer allows you to receive notification of successful payments as they are made.', groups='base.group_user')
    # Default gtbank fees
    fees_dom_fixed = fields.Float(default=0.0)
    fees_dom_var = fields.Float(default=1.5)
    fees_int_fixed = fields.Float(default=0.0)
    fees_int_var = fields.Float(default=1.5)

    def _get_feature_support(self):
        """Get advanced feature support by provider.

        Each provider should add its technical in the corresponding
        key for the following features:
            * fees: support payment fees computations
            * authorize: support authorizing payment (separates
                         authorization and capture)
            * tokenize: support saving payment data in a payment.tokenize
                        object
        """
        res = super(AcquirerGTPay, self)._get_feature_support()
        res['fees'].append('gtpay')
        return res

    @api.model
    def _get_gtpay_urls(self, environment):
        """ GTPay URLS """
        if environment == 'prod':
            return {
                'gtpay_rest_url': 'https://ibank.gtbank.com/GTPayService/gettransactionstatus.json',
                'gtpay_form_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
            }
        else:
            return {
                'gtpay_rest_url': 'https://ibank.gtbank.com/GTPayService/gettransactionstatus.json',
                'gtpay_form_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
            }

    @api.multi
    def gtpay_compute_fees(self, amount, currency_id, country_id):
        """ Compute gtpay fees.

            :param float amount: the amount to pay
            :param integer country_id: an ID of a res.country, or None. This is
                                       the customer's country, to be compared to
                                       the acquirer company country.
            :return float fees: computed fees
        """
        if not self.fees_active:
            return 0.0
        country = self.env['res.country'].browse(country_id)
        if country and self.company_id.country_id.id == country.id:
            percentage = self.fees_dom_var
            fixed = self.fees_dom_fixed
        else:
            percentage = self.fees_int_var
            fixed = self.fees_int_fixed
        fees = (percentage / 100.0 * amount + fixed) / (1 - percentage / 100.0)
        if fees > 2000.0:
            fees = 2000.0
        return fees

    @api.multi
    def gtpay_form_generate_values(self, values):
        _logger.info('gtpay_form_generate_values')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        gtpay_tx_values = dict(values)
        currency = 0
        if values['currency'] and values['currency'].name == 'NGN':
            currency = 566
        elif values['currency'] and values['currency'].name == 'USD':
            currency = 826
        amount = 0 
        if values['amount']:
            amount = values['amount'] * 100
            amount = '{0:.0f}'.format(amount)

        gtpay_hash = '%s%s%s%s%s%s%s'%(self.gtpay_seller_account,
                                    '%s: %s' % (self.company_id.name, values['reference']),
                                    amount, currency, values.get('partner').code,
                                    urls.url_join(base_url, GTPayController._return_url),
                                    self.gtpay_hash_key)
        
        hash = hashlib.sha512()
        hash.update(gtpay_hash.encode('utf-8'))
        gtpay_hash = hash.hexdigest().upper()

        gtpay_tx_values.update({
            'cmd': '_xclick',
            'gtpay_mert_id': self.gtpay_seller_account,
            'gtpay_tranx_id': values['reference'],
            'gtpay_tranx_amt': str(amount),
            'gtpay_tranx_curr': str(currency),
            'gtpay_cust_id':values.get('partner').code,
            'gtpay_cust_name': values.get('partner_name'),
            'gtpay_tranx_memo': self.env['account.invoice'].search([('number','=',values['reference'])],limit=1).name, 
            'gtpay_no_show_gtbank': 'yes',
            'gtpay_echo_data': 'TEST',
            'gtpay_gway_name': "",
            'gtpay_hash': gtpay_hash,
            'gtpay_tranx_noti_url': urls.url_join(base_url, GTPayController._return_url),
        })
        #_logger.info(gtpay_tx_values)
        return gtpay_tx_values

    @api.multi
    def gtpay_get_form_action_url(self):
        return self._get_gtpay_urls(self.environment)['gtpay_form_url']


class TxGTPay(models.Model):
    _inherit = 'payment.transaction'

    gtpay_txn_type = fields.Char('Transaction type')

    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------

    @api.model
    def _gtpay_form_get_tx_from_data(self, data):
        _logger.info('_gtpay_form_get_tx_from_data')
        _logger.info(data)
        reference = data.get('gtpay_tranx_id')
        if not reference:
            error_msg = _('GTPay: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'GTPay: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _gtpay_form_get_invalid_parameters(self, data):
        _logger.info('_gtpay_form_get_invalid_parameters')
        invalid_parameters = []
        _logger.info('Received a notification from GTPay with status code %s', data.get('gtpay_tranx_status_code'))

        if self.acquirer_reference and data.get('gtpay_tranx_id') != self.reference:
            invalid_parameters.append(('gtpay_tranx_id', data.get('gtpay_tranx_id'), self.reference))
        if float_compare(float(data.get('gtpay_tranx_amt', '0.0')), (self.amount + self.fees), 2) != 0:
            invalid_parameters.append(('gtpay_tranx_amt', data.get('gtpay_tranx_amt'), '%.2f' % self.amount))
        return invalid_parameters

    @api.multi
    def _gtpay_form_validate(self, data):
        _logger.info('_gtpay_form_validate')
        status = data.get('gtpay_tranx_status_code')
        message = data.get('gtpay_tranx_status_msg')
        res = {
            'acquirer_reference': data.get('gtpay_tranx_id'),
            'gtpay_txn_type': data.get('gtpay_gway_name'),
        }
        if status in ['00']:
            _logger.info('Validated GTPay payment for tx %s: set as done' % (self.reference))
            date_validate = fields.Datetime.now()
            res.update(state='done', date_validate=date_validate)
            return self.write(res)
        elif status in ['G300']:
            cancel = 'Received status for GTPay payment %s: %s %s set as cancel' % (self.reference, status, message)
            _logger.info(cancel)
            res.update(state='cancel', state_message=cancel)
            return self.write(res)
        else:
            error = 'Received status for GTPay payment %s: %s %s set as error' % (self.reference, status, message)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)
