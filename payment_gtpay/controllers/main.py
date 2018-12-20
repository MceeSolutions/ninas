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
import hashlib

_logger = logging.getLogger(__name__)


class GTPayController(http.Controller):
    _return_url = '/payment/gtpay/return/'
    _cancel_url = '/payment/gtpay/cancel/'

    def _get_return_url(self, **post):
        """ Extract the return URL from the data coming from gtpay. """
        return_url = post.pop('gtpay_tranx_noti_url', '/')
        return return_url


    def gtpay_validate_data(self, **post):
        """ GTPay IPN: three steps validation to ensure data correctness

         - step 1: return an empty HTTP 200 response -> will be done at the end
           by returning ''
         - step 2: POST the complete, unaltered message back to GTPay, with same encoding
         - step 3: paypal send either 00 or G
        Once data is validated, process it. """

        res = False
        _logger.info('gtpay_validate_data')
        new_post = dict(post, charset='UTF-8')
        gtpay_tranx_id = new_post.get('gtpay_tranx_id')
        gtpay_tranx_amt_small_denom = new_post.get('gtpay_tranx_amt_small_denom')
        reference = gtpay_tranx_id
        tx = None
        if reference:
            tx = request.env['payment.transaction'].search([('reference', '=', reference)])

        gtpay_mert_id = tx and tx.acquirer_id.gtpay_seller_account or False
        gtpay_hashkey = tx and tx.acquirer_id.gtpay_hash_key or False

        hash_req = hashlib.sha512()
        hash_req.update((gtpay_mert_id+gtpay_tranx_id+gtpay_hashkey).encode('utf-8'))
        hash_req = hash_req.hexdigest().upper()
        params = {
            'mertid':gtpay_mert_id, 
            'amount':gtpay_tranx_amt_small_denom,
            'tranxid':gtpay_tranx_id,
            'hash':hash_req
        }

        gtpay_urls = request.env['payment.acquirer']._get_gtpay_urls(tx and tx.acquirer_id.environment or 'prod')
        validate_url = gtpay_urls['gtpay_rest_url']
        urequest = requests.get(validate_url, params)
        urequest.raise_for_status()
        resp = urequest.json()
        _logger.info('Response %s'%resp)
        if resp['ResponseCode'] in ['00']:
            _logger.info('GTPay: Validated Data')
            res = request.env['payment.transaction'].sudo().form_feedback(post, 'gtpay')
        else:
            _logger.warning('GTPay: %s - %s'%(resp['ResponseCode'], resp['ResponseDescription']))
            res = request.env['payment.transaction'].sudo().form_feedback(post, 'gtpay')
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
