from openerp import models, fields, api, _
from openerp.exceptions import UserError
from openerp.tools import float_compare

class MultiSODeliveryLine(models.TransientModel):
    _name = "sale.order.delivery.line"

    @api.multi
    def _get_availability(self):
        for a in self:
            a.availability = a.product_id.qty_available

    @api.multi
    def _get_status(self):
        for a in self:
            if a.product_id.qty_available > 0.0:
                a.state = 'assigned'
            else:
                a.state = 'confirmed'

    multiso_id = fields.Many2one('sale.order.confirm')
    order_id = fields.Many2one('sale.order', 'Order')
    sale_line_id = fields.Many2one('sale.order.line', 'Order Line')
    product_id = fields.Many2one('product.product', 'Product')
    deliver_qty = fields.Float('Deliver Quantity')
    product_qty = fields.Float('Quantity')
    product_uom = fields.Many2one('product.uom', 'Unit of Measure')
    state = fields.Selection([('confirmed', 'Waiting Availability'),
                                   ('assigned', 'Available')], 'Status', readonly=True, compute='_get_status')
    availability = fields.Float(compute='_get_availability', string='Available Quantity', readonly=True, help='Quantity in stock that can still be reserved for this move')
    transfer = fields.Boolean()

class MultiSO(models.TransientModel):
    _name = "sale.order.confirm"

    @api.model
    def default_get(self, fields):
        res = super(MultiSO, self).default_get(fields)
        if self._context.get('active_ids'):
            line_ids = []
            self.env['sale.order.delivery.line'].search([]).unlink()
            for so in self.env['sale.order'].browse(self._context.get('active_ids')):
                for so_line in so.order_line:
                    if so_line.is_multi_delivered is False or (so_line.is_multi_delivered is True and (so_line.product_uom_qty - so_line.qty_in_delivery) > 0.0):
                        if so_line.product_id.type != 'service':
                            sod_line = self.env['sale.order.delivery.line'].create({
                                'order_id': so.id,
                                'sale_line_id': so_line.id,
                                'product_id': so_line.product_id.id,
                                'product_qty': so_line.product_uom_qty,
                                'deliver_qty': (so_line.product_uom_qty - so_line.qty_in_delivery),
                                'product_uom': so_line.product_uom.id,
                                })
                            line_ids.append(sod_line.id)
        res['multi_so_line_ids'] = line_ids
        return res

    multi_so_line_ids = fields.One2many('sale.order.delivery.line', 'multiso_id')

    @api.multi
    def so_confirm(self):
        context = dict(self._context or {})
        active_ids = context.get('active_ids', []) or []
        sale_orders = self.env['sale.order'].browse(active_ids)
#         if any(so.state not in ['draft', 'sent'] for so in sale_orders):
#             raise UserError(_("Selected SaleOrder(s) cannot be confirmed as they are not in 'Draft' state."))
        so = [so.partner_id for so in sale_orders]
        if any(so[0].id != s.id for s in so):
            raise UserError(_("In order to make single delivery order of multiple SO at once, they must belong to the same customer."))
        for order in sale_orders:
            order.state = 'sale'
            if self.env.context.get('send_email'):
                self.force_quotation_send()
#         order_lines = self.env['sale.order.line'].search([('order_id', 'in', active_ids)])
#         order_lines = [x.sale_line_id for x in self.multi_so_line_ids]
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']
        so_line_ids = self.env['sale.order.delivery.line'].search([('transfer', '=', True)])
        if not so_line_ids:
            raise UserError(_("Please select Product to Delivery or There is not any product to Delivery."))
        for x in so_line_ids:
            if x.sale_line_id.state != 'sale' or not x.sale_line_id.product_id._need_procurement():
                continue
#             qty = 0.0
#             for proc in x.sale_line_id.procurement_ids:
#                 qty += proc.product_qty
# #             if float_compare(qty, x.sale_line_id.product_uom_qty, precision_digits=precision) >= 0:
#             if float_compare(qty, x.deliver_qty, precision_digits=precision) >= 0:
#                 continue
            vals = {}
            name = ''
            for so in sale_orders:
                name += so.name + ', '
            if not x.sale_line_id.order_id.procurement_group_id:
                #vals = line.order_id._prepare_procurement_group()
                #line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)
                vals = {'name': name[:-1], 'move_type': sale_orders[0].picking_policy, 'partner_id': sale_orders[0].partner_shipping_id.id}
                proc_group = self.env["procurement.group"].create(vals)
                for so in sale_orders:
                    so.procurement_group_id = proc_group

            vals = x.sale_line_id._prepare_order_line_procurement(group_id=x.sale_line_id.order_id.procurement_group_id.id)
            vals.update({'origin': name[:-1]})
#             vals['product_qty'] = x.sale_line_id.product_uom_qty - qty
            vals['product_qty'] = x.deliver_qty #- qty
            new_proc = self.env["procurement.order"].create(vals)
            new_procs += new_proc

            #assign sale order ids to related picking.
            picking_ids = self.env['stock.picking'].search([('group_id', '=', so.procurement_group_id.id)])
            for picking in picking_ids:
                if not picking.sale_order_ids:
                    picking.sale_order_ids = sale_orders
            if x.deliver_qty > x.sale_line_id.product_uom_qty:
                x.sale_line_id.write({'qty_in_delivery': (x.sale_line_id.qty_in_delivery + x.deliver_qty), 'is_multi_delivered': True, 'product_uom_qty': (x.sale_line_id.qty_in_delivery + x.deliver_qty)})
            else:
                x.sale_line_id.write({'qty_in_delivery': (x.sale_line_id.qty_in_delivery + x.deliver_qty), 'is_multi_delivered': True})

        new_procs.run()
        for order in sale_orders:
            if not order.project_id:
                    for line in order.order_line:
                        if line.product_id.invoice_policy == 'cost':
                            order._create_analytic_account()
                            break
        if self.env['ir.values'].get_default('sale.config.settings', 'auto_done_setting'):
            self.env['sale.order'].action_done()

        for picking_id in sale_orders[0].picking_ids:
            if picking_id.state in ['waiting', 'confirmed']:
                picking_id.action_assign()

        if sale_orders and sale_orders[0].picking_ids:
            pic_id = False
            for picking in sale_orders[0].picking_ids:
                if pic_id < picking.id:
                    pic_id = picking.id
            return {
                'name': _('Stock Operations'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.picking',
                'view_id': self.env.ref('stock.view_picking_form').id,
                'type': 'ir.actions.act_window',
                'res_id': pic_id,
                'context': context,
                'target': 'current'
                    }
        else:
            return {'type': 'ir.actions.act_window_close'}


class stock_move(models.Model):
    _inherit = 'stock.move'

#     @api.multi
#     def _get_sale_order(self):
#         for stock_move in self:
#             sale_ref = False
#             if stock_move.procurement_id and stock_move.procurement_id.sale_line_id:
#                 sale_ref = stock_move.procurement_id.sale_line_id.order_id.id
#             stock_move.order_id = sale_ref
# 
#     order_id = fields.Many2one('sale.order', 'Order', compute='_get_sale_order')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_multi_delivered = fields.Boolean(copy=False)
    qty_in_delivery = fields.Float(copy=False)

    @api.multi
    def _get_delivered_qty(self):
        """Computes the delivered quantity on sale order lines, based on done stock moves related to its procurements
        """
        self.ensure_one()
        super(SaleOrderLine, self)._get_delivered_qty()
        qty = 0.0
        for move in self.procurement_ids.mapped('move_ids').filtered(lambda r: r.state == 'done' and not r.scrapped):
            #Note that we don't decrease quantity for customer returns on purpose: these are exeptions that must be treated manually. Indeed,
            #modifying automatically the delivered quantity may trigger an automatic reinvoicing (refund) of the SO, which is definitively not wanted
            if move.location_dest_id.usage == "customer":
                qty += self.env['product.uom']._compute_qty_obj(move.product_uom, move.product_uom_qty, self.product_uom)

            #added code for deduct return qty of delivery order from sol.
            if move.picking_type_id.code == 'incoming':
                qty -= move.product_uom_qty
            if qty < 0.0:
                qty = 0.0
        return qty

    #stop creating delivery order when increase qty or add sale order line.
    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order'] #Empty recordset
#         for line in self:
#             if line.state != 'sale' or not line.product_id._need_procurement():
#                 continue
#             qty = 0.0
#             for proc in line.procurement_ids:
#                 qty += proc.product_qty
#             if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
#                 continue
# 
#             if not line.order_id.procurement_group_id:
#                 vals = line.order_id._prepare_procurement_group()
#                 line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)
# 
#             vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
#             vals['product_qty'] = line.product_uom_qty - qty
#             new_proc = self.env["procurement.order"].create(vals)
#             new_procs += new_proc
        new_procs.run()
        return new_procs

class stock_backorder_confirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    #override method for cancel backorder when click on create backorder button.
    @api.multi
    def _process(self, cancel_backorder=False):
        self.ensure_one()
        for pack in self.pick_id.pack_operation_ids:
            if pack.qty_done > 0:
                pack.product_qty = pack.qty_done
            else:
                pack.unlink()
        self.pick_id.do_transfer()
        if cancel_backorder:
            backorder_pick = self.env['stock.picking'].search([('backorder_id', '=', self.pick_id.id)])

            for picking in backorder_pick:
                picking.move_lines.action_cancel()

            backorder_pick.action_cancel()
            self.pick_id.message_post(body=_("Back order <em>%s</em> <b>cancelled</b>.") % (backorder_pick.name))
            backorder_pick.state

