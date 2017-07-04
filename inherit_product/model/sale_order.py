# -*- coding: utf-8 -*-
from openerp import models, fields, api

class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.model
    def create(self, vals):
        res = super(SaleOrder, self).create(vals)
        if self._context.get('show_sale', False):
            res.action_confirm()
        return res

    @api.multi
    @api.depends('write_date')
    def get_delivery_status(self):
        for order in self:
            qty = 0.0
            deliver_qty = 0.0
            for line_id in order.order_line:
                if line_id.product_id.type != 'service':
                    qty += line_id.product_uom_qty
                    deliver_qty += line_id.qty_delivered
            if deliver_qty == 0.0:
                order.delivery_status = 'draft'
            if deliver_qty < qty and deliver_qty > 0.0:
                order.delivery_status = 'partial'
            if deliver_qty == qty:
                order.delivery_status = 'delivered'

#             order.delivery_status = 'draft'
#             delivered_picking = [pick for pick in order.picking_ids if pick.state == 'done']
#             if len(order.picking_ids) == len(delivered_picking) and len(delivered_picking) > 0:
#                 order.delivery_status = 'delivered'
#             elif (len(order.picking_ids) != len(delivered_picking)) and len(delivered_picking) > 0:
#                 order.delivery_status = 'partial'

    delivery_status = fields.Selection([('draft', 'Not Delivered'),
                                    ('delivered', 'Delivered'),
                                    ('partial', 'Partially Delivered')],
                                    'Delivery Status', compute='get_delivery_status', store=True)
    is_print = fields.Boolean(string='Delivery Print')

    @api.multi
    @api.depends('procurement_group_id')
    def _compute_picking_ids(self):
        for order in self:
            picking_ids = self.env['stock.picking'].search(['|', ('group_id', '=', order.procurement_group_id.id), ('sale_order_ids', 'in', order.id)]) if order.procurement_group_id else []

            pic_ids = [x.id for x in picking_ids]
            for picking in picking_ids:
                if picking.sale_order_ids:
                    if order not in picking.sale_order_ids:
                        pic_ids.remove(picking.id)
            order.picking_ids = pic_ids
            order.delivery_count = len(order.picking_ids)

    @api.multi
    def action_quotation_send(self):
        res = super(SaleOrder, self).action_quotation_send()
        users = self.env['res.users'].search([])
        partners = [p.id for p in self.env['res.partner'].search([])]
        smeet_partner = [x.partner_id.id for x in users]
        related_partners = [self.partner_id.id, self.partner_invoice_id.id, self.partner_shipping_id.id]
        related_partners.extend(self.partner_id.child_ids.ids + self.partner_invoice_id.child_ids.ids + self.partner_shipping_id.child_ids.ids + smeet_partner)
        if related_partners:
            for r in related_partners:
                if r in partners:
                    partners.remove(r)
        res['context'].update({'related_partners': partners})
        return res

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

    @api.multi
    def action_draft(self):
        res = super(SaleOrder, self).action_draft()
        for line in self.order_line:
            line.write({'is_multi_delivered': False, 'qty_in_delivery': 0.0})
        return res
    
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'zpro_length')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#             taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, (line.product_uom_qty * line.zpro_length), product=line.product_id, partner=line.order_id.partner_id)
            price_subtotal = taxes['total_excluded']
#             if line.zpro_length:
#                 price_subtotal = price_subtotal * line.zpro_length
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': price_subtotal,

            })

    @api.multi
    @api.depends('product_uom_qty', 'zpro_length')
    def _get_total_length(self):
        for line in self:
            line.total_length = line.product_uom_qty * line.zpro_length

    zpro_length = fields.Float(string="Lengte", default=1)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    total_length = fields.Float(string="Total Lengte", compute='_get_total_length', readonly=True)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if self.product_id:
            self.zpro_length = self.product_id.zpro_length
        return res

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(SaleOrderLine, self)._prepare_invoice_line(qty)
        res.update({'zpro_length': self.zpro_length})
        return res


