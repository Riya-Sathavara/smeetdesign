# -*- coding: utf-8 -*-

from openerp import http
from openerp.http import request

class CustomerController(http.Controller):

    @http.route(['/customer/client_action'], type='json', auth="public")
    def mail_client_action_test(self):
        values = {
            'needaction_inbox_counter': request.env['res.partner'].search_count([('customer', '=', True)]),
        }
        return values
