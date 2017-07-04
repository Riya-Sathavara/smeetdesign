from openerp import api, fields, models, _
from openerp.exceptions import UserError


class ProductHistory(models.TransientModel):
    _name = "product.history"

    product_id = fields.Many2one('product.product','Product')
    ordered_qty = fields.Float('Ordered Quantity')
    line_id = fields.Many2one('sale.order.line','Order line')
    sale_wiz_id = fields.Many2one('sale.advance.product.history','Sale Wizard id')


class SaleAdvanceProductHistory(models.TransientModel):
    _name = "sale.advance.product.history"

    product_his_ids = fields.One2many('product.history','sale_wiz_id')

    @api.model
    def default_get(self, fields):
        rec = super(SaleAdvanceProductHistory, self).default_get(fields)
        context = dict(self._context or {})
        active_model = context.get('active_model')
        active_ids = context.get('active_ids')
        product_his_list = []

        # Checks on received invoice records
        order_lines = self.env[active_model].browse(active_ids)
        for line in order_lines:
            product_his_list.append((0,0,{'product_id': line.product_id.id,
                                    'ordered_qty' : line.product_uom_qty,
                                    'line_id' : line.id}))
        rec.update({'product_his_ids' : product_his_list})
        return rec

    @api.multi
    def action_view_sale(self, order_id):
        imd = self.env['ir.model.data']
        action = imd.xmlid_to_object('sale.action_orders')
        list_view_id = imd.xmlid_to_res_id('sale.view_order_tree')
        form_view_id = imd.xmlid_to_res_id('sale.view_order_form')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'views': [[form_view_id, 'form'], [False, 'graph'], [False, 'kanban'], [False, 'calendar'], [False, 'pivot']],
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
            'res_id' : order_id.id,
        }
        return result

    @api.multi
    def create_sale_order(self):
        if self.product_his_ids:
            partner_id = self.product_his_ids[0].line_id.order_partner_id
            addr = partner_id.address_get(['delivery', 'invoice'])
            values = {
                    'partner_id' : partner_id.id,
                    'pricelist_id': partner_id.property_product_pricelist and partner_id.property_product_pricelist.id or False,
                    'payment_term_id': partner_id.property_payment_term_id and partner_id.property_payment_term_id.id or False,
                    'partner_invoice_id': addr['invoice'],
                    'partner_shipping_id': addr['delivery'],
                    }
            if self.env.user.company_id.sale_note:
                values['note'] = self.with_context(lang=partner_id.lang).env.user.company_id.sale_note
            if partner_id.user_id:
                values['user_id'] = partner_id.user_id.id
            if partner_id.team_id:
                values['team_id'] = partner_id.team_id.id                
            order_id = self.env['sale.order'].create(values)
            for product_his_id in self.product_his_ids:
                product_his_id.line_id.copy(default={'order_id' : order_id.id ,'product_uom_qty' :product_his_id.ordered_qty })
        if self._context.get('open_sale', False):
            return self.action_view_sale(order_id)
        return {'type': 'ir.actions.act_window_close'}
    