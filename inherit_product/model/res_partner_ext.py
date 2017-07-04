# -*- coding: utf-8 -*-
from openerp import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def _get_product_history(self):
        order_line_obj = self.env['sale.order.line']
        for partner in self:
            order_lines = order_line_obj.search([('order_partner_id', '=', partner.id)])
            partner.product_history = len(order_lines)

    product_history = fields.Integer(string="Product history", compute='_get_product_history')
