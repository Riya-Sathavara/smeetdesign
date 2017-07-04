# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.exceptions import UserError
from openerp.tools.translate import _

class DeliveryCarrier(models.Model):
    _inherit = 'delivery.carrier'

    delivery_type = fields.Selection([('fixed', 'Fixed Price'), ('base_on_rule', 'Based on Rules'), ('custom', 'Custom Price')], string='Price Computation', default='fixed', required=True)

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    delivery_type = fields.Selection("Delivery Type", related="carrier_id.delivery_type", store=True)
    custom_delivery_cost = fields.Float()

    @api.depends('carrier_id', 'partner_id', 'order_line')
    def _compute_delivery_price(self):
        for order in self:
            if order.state != 'draft':
                # We do not want to recompute the shipping price of an already validated/done SO
                continue
            elif order.carrier_id.delivery_type != 'grid' and not order.order_line:
                # Prevent SOAP call to external shipping provider when SO has no lines yet
                continue
            elif order.carrier_id.delivery_type == 'custom' and not order.order_line:
                continue
            elif order.carrier_id.delivery_type == 'custom':
                order.delivery_price = order.custom_delivery_cost
            else:
                order.delivery_price = order.carrier_id.with_context(order_id=order.id).price

    @api.multi
    def delivery_set(self):

        for order in self:
            carrier = order.carrier_id
            if carrier.delivery_type != 'custom':
                # Remove delivery products from the sale order
                self._delivery_unset()

            if carrier:
                if order.invoice_status not in ['to invoice', 'no']:
                    raise UserError(_('The Invoice has beed validated.'))

                if order.state not in ('draft', 'sent') and carrier.delivery_type != 'custom':
                    raise UserError(_('The order state have to be draft to add delivery lines.'))

                if carrier.delivery_type not in ['fixed', 'base_on_rule', 'custom']:
                    # Shipping providers are used when delivery_type is other than 'fixed' or 'base_on_rule'
                    price_unit = order.carrier_id.get_shipping_price_from_so(order)[0]
                else:
                    # Classic grid-based carriers
                    carrier = order.carrier_id.verify_carrier(order.partner_shipping_id)
                    if not carrier:
                        raise UserError(_('No carrier matching.'))
                    price_unit = carrier.get_price_available(order)
                    if carrier.delivery_type == 'custom':
                        price_unit = order.custom_delivery_cost
                    if order.company_id.currency_id.id != order.pricelist_id.currency_id.id:
                        price_unit = order.company_id.currency_id.with_context(date=order.date_order).compute(price_unit, order.pricelist_id.currency_id)

                line_ids = self.env['sale.order.line'].search([('order_id', 'in', self.ids), ('is_delivery', '=', True)])
                if carrier.delivery_type != 'custom' or (carrier.delivery_type == 'custom' and not line_ids):
                    order._create_delivery_line(carrier, price_unit)
                else:
                    line_ids.write({'price_unit': price_unit, 'name': carrier.name, 'product_id': carrier.product_id.id})
            else:
                raise UserError(_('No carrier set for this order.'))

        return True
