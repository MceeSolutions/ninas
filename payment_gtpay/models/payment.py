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
                'gtpay_form_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
                'gtpay_rest_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
            }
        else:
            return {
                'gtpay_form_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
                'gtpay_rest_url': 'https://ibank.gtbank.com/GTPay/Tranx.aspx',
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
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')

        gtpay_tx_values = dict(values)
        gtpay_tx_values.update({
            'cmd': '_xclick',
            'item_name': '%s: %s' % (self.company_id.name, values['reference']),
            'item_number': values['reference'],
            'amount': values['amount'],
            'currency_code': values['currency'] and values['currency'].name or '',
            'address1': values.get('partner_address'),
            'city': values.get('partner_city'),
            'country': values.get('partner_country') and values.get('partner_country').code or '',
            'state': values.get('partner_state') and (values.get('partner_state').code or values.get('partner_state').name) or '',
            'email': values.get('partner_email'),
            'zip_code': values.get('partner_zip'),
            'first_name': values.get('partner_first_name'),
            'last_name': values.get('partner_last_name'),
            'gtpay_return': urls.url_join(base_url, GTPayController._return_url),
            'cancel_return': urls.url_join(base_url, GTPayController._cancel_url),
            'handling': '%.2f' % gtpay_tx_values.pop('fees', 0.0) if self.fees_active else False,
        })
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
        reference, txn_id = data.get('item_number'), data.get('txn_id')
        if not reference or not txn_id:
            error_msg = _('Paypal: received data with missing reference (%s) or txn_id (%s)') % (reference, txn_id)
            _logger.info(error_msg)
            raise ValidationError(error_msg)

        # find tx -> @TDENOTE use txn_id ?
        txs = self.env['payment.transaction'].search([('reference', '=', reference)])
        if not txs or len(txs) > 1:
            error_msg = 'Paypal: received data for reference %s' % (reference)
            if not txs:
                error_msg += '; no order found'
            else:
                error_msg += '; multiple order found'
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        return txs[0]

    @api.multi
    def _gtpay_form_get_invalid_parameters(self, data):
        invalid_parameters = []
        _logger.info('Received a notification from GTPay with IPN version %s', data.get('notify_version'))
        if data.get('test_ipn'):
            _logger.warning(
                'Received a notification from Paypal using sandbox'
            ),

        # TODO: txn_id: shoudl be false at draft, set afterwards, and verified with txn details
        if self.acquirer_reference and data.get('txn_id') != self.acquirer_reference:
            invalid_parameters.append(('txn_id', data.get('txn_id'), self.acquirer_reference))
        # check what is buyed
        if float_compare(float(data.get('mc_gross', '0.0')), (self.amount + self.fees), 2) != 0:
            invalid_parameters.append(('mc_gross', data.get('mc_gross'), '%.2f' % self.amount))  # mc_gross is amount + fees
        if data.get('mc_currency') != self.currency_id.name:
            invalid_parameters.append(('mc_currency', data.get('mc_currency'), self.currency_id.name))
        if 'handling_amount' in data and float_compare(float(data.get('handling_amount')), self.fees, 2) != 0:
            invalid_parameters.append(('handling_amount', data.get('handling_amount'), self.fees))
        # check buyer
        if self.payment_token_id and data.get('payer_id') != self.payment_token_id.acquirer_ref:
            invalid_parameters.append(('payer_id', data.get('payer_id'), self.payment_token_id.acquirer_ref))
        # check seller
        if data.get('receiver_id') and self.acquirer_id.paypal_seller_account and data['receiver_id'] != self.acquirer_id.paypal_seller_account:
            invalid_parameters.append(('receiver_id', data.get('receiver_id'), self.acquirer_id.paypal_seller_account))
        if not data.get('receiver_id') or not self.acquirer_id.paypal_seller_account:
            # Check receiver_email only if receiver_id was not checked.
            # In Paypal, this is possible to configure as receiver_email a different email than the business email (the login email)
            # In Odoo, there is only one field for the Paypal email: the business email. This isn't possible to set a receiver_email
            # different than the business email. Therefore, if you want such a configuration in your Paypal, you are then obliged to fill
            # the Merchant ID in the Paypal payment acquirer in Odoo, so the check is performed on this variable instead of the receiver_email.
            # At least one of the two checks must be done, to avoid fraudsters.
            if data.get('receiver_email') != self.acquirer_id.paypal_email_account:
                invalid_parameters.append(('receiver_email', data.get('receiver_email'), self.acquirer_id.paypal_email_account))

        return invalid_parameters

    @api.multi
    def _gtpay_form_validate(self, data):
        status = data.get('payment_status')
        res = {
            'acquirer_reference': data.get('txn_id'),
            'paypal_txn_type': data.get('payment_type'),
        }
        if status in ['Completed', 'Processed']:
            _logger.info('Validated Paypal payment for tx %s: set as done' % (self.reference))
            try:
                # dateutil and pytz don't recognize abbreviations PDT/PST
                tzinfos = {
                    'PST': -8 * 3600,
                    'PDT': -7 * 3600,
                }
                date_validate = dateutil.parser.parse(data.get('payment_date'), tzinfos=tzinfos).astimezone(pytz.utc)
            except:
                date_validate = fields.Datetime.now()
            res.update(state='done', date_validate=date_validate)
            return self.write(res)
        elif status in ['Pending', 'Expired']:
            _logger.info('Received notification for Paypal payment %s: set as pending' % (self.reference))
            res.update(state='pending', state_message=data.get('pending_reason', ''))
            return self.write(res)
        else:
            error = 'Received unrecognized status for Paypal payment %s: %s, set as error' % (self.reference, status)
            _logger.info(error)
            res.update(state='error', state_message=error)
            return self.write(res)
