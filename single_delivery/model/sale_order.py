# -*- coding: utf-8 -*-
from openerp import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    #override method for stop creating delivery order.
    @api.multi
    def action_confirm(self):
        for order in self:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
            #order.order_line._action_procurement_create()
            if not order.project_id:
                for line in order.order_line:
                    if line.product_id.invoice_policy == 'cost':
                        order._create_analytic_account()
                        break
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.action_done()
        return True