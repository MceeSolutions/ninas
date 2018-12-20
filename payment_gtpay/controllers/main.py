# -*- coding: utf-8 -*-

import json
import logging
import pprint

import requests
import werkzeug
from werkzeug import urls

from odoo import http
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.http import request

_logger = logging.getLogger(__name__)


class GTPayController(http.Controller):
    _return_url = '/payment/gtpay/return/'
    _cancel_url = '/payment/gtpay/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from gtpay. """
        return_url = post.pop('gtpay_tranx_noti_url', '')
        return return_url


    def gtpay_validate_data(self, **post):
        """ GTPay IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to Paypal (preceded
           by cmd=_notify-validate or _notify-synch for PDT), with same encoding
         - step 3: paypal send either VERIFIED or INVALID (single word) for IPN
                   or SUCCESS or FAIL (+ data) for PDT

        Once data is validated, process it. """
        res = False
        new_post = dict(post, cmd='_notify-validate', charset='UTF-8')
        reference = post.get('gtpay_tranx_id')
        tx = None
        if reference:
            tx = request.env['payment.transaction'].search([('reference', '=', reference)])
        gtpay_urls = request.env['payment.acquirer']._get_gtpay_urls(tx and tx.acquirer_id.environment or 'prod')
        validate_url = gtpay_urls['gtpay_form_url']
        urequest = requests.post(validate_url, new_post)
        urequest.raise_for_status()
        resp = urequest.json()
        if resp['gtpay_tranx_status_code'] in ['00']:
            _logger.info('GTPay: Validated Data')
            res = request.env['payment.transaction'].sudo().form_feedback(post, 'gtpay')
        elif resp in ['INVALID', 'FAIL']:
            _logger.warning('GTPay: answered INVALID/FAIL on data verification')
        return res

    @http.route('/payment/gtpay/return', type='http', auth="none", methods=['POST', 'GET'], csrf=False)
    def gtpay_return(self, **post):
        """ GTPay """
        _logger.info('Beginning GTPay form_feedback with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        self.gtpay_validate_data(**post)
        return werkzeug.utils.redirect(return_url)

    @http.route('/payment/gtpay/cancel', type='http', auth="none", csrf=False)
    def gtpay_cancel(self, **post):
        """ When the user cancels its GTPay payment: GET on this route """
        _logger.info('Beginning GTPay cancel with post data %s', pprint.pformat(post))  # debug
        return_url = self._get_return_url(**post)
        return werkzeug.utils.redirect(return_url)
