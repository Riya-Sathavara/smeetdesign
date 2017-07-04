# -*- coding: utf-8 -*-
from openerp import models, fields, api
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.multi
    @api.onchange('date_order')
    def onchange_date_order(self):
        if self.date_order:
            date_order = datetime.strptime(self.date_order,"%Y-%m-%d %H:%M:%S").date()
            self.validity_date = (date_order + relativedelta(months=1))

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.date_order = datetime.today()
        return True


    @api.multi
    def print_quotation(self):
        self.filtered(lambda s: s.state == 'draft').write({'state': 'sent'})
        return self.env['report'].get_action(self, 'smt_delivery_report.sale_quotation_report')

class StockPicking(models.Model):
    _inherit = "stock.picking"

    @api.model
    def is_print(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id:
                move.procurement_id.sale_line_id.order_id.is_print = True
                return

    @api.model
    def so_total_amount(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)

        amount = []
        if move and not move.order_id:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id:
                amount.append(move.procurement_id.sale_line_id.order_id.amount_untaxed)
                amount.append(move.procurement_id.sale_line_id.order_id.amount_tax)
                amount.append(move.procurement_id.sale_line_id.order_id.amount_total)
        else:
            sale_ids = [move.order_id for move in self.move_lines if move.order_id]
            sale_ids = list(set(sale_ids))
            for sale in sale_ids:
                if not amount:
                    amount.append(sale.amount_untaxed)
                    amount.append(sale.amount_tax)
                    amount.append(sale.amount_total)
                else:
                    amount[0] = amount[0] + sale.amount_untaxed
                    amount[1] = amount[1] + sale.amount_tax
                    amount[2] = amount[2] + sale.amount_total

        return amount

    @api.model
    def so_name(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id:
                return move.procurement_id.sale_line_id.order_id.name

    @api.model
    def sale_company_name(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id:
                if move.procurement_id.sale_line_id.order_id.partner_id.company_type == 'company':
                    return False
                else:
                    if move.procurement_id.sale_line_id.order_id.partner_id.parent_id:
                        return move.procurement_id.sale_line_id.order_id.partner_id.parent_id.name
                    else:
                        return False

    @api.model
    def sale_customer_name(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id:
                return move.procurement_id.sale_line_id.order_id.partner_id.name

    @api.model
    def customer_ref(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.client_order_ref:
                return move.procurement_id.sale_line_id.order_id.client_order_ref

    @api.model
    def cust_street(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id.street:
                return move.procurement_id.sale_line_id.order_id.partner_id.street


    @api.model
    def cust_street2(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id.street2:
                return move.procurement_id.sale_line_id.order_id.partner_id.street2

    @api.model
    def cust_zip(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id.zip:
                return move.procurement_id.sale_line_id.order_id.partner_id.zip


    @api.model
    def cust_city(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id.city:
                return move.procurement_id.sale_line_id.order_id.partner_id.city


    @api.model
    def cust_count_name(self):
        move = self.env['stock.move'].search([('picking_id', '=', self.id)], limit=1)
        if move:
            if move.procurement_id and move.procurement_id.sale_line_id and move.procurement_id.sale_line_id.order_id.partner_id.country_id.name:
                return move.procurement_id.sale_line_id.order_id.partner_id.country_id.name

    @api.multi
    def get_move_lines(self):
        vals = []
        sale_ids = [move.order_id for move in self.move_lines if move.order_id]
        sale_ids = list(set(sale_ids))
        for order in sale_ids:
            if order:
                client_ref = order.name
                if order.client_order_ref:
                    client_ref += ' ' + '/' + ' ' + order.client_order_ref
                vals.append({'prod_code': False, 'prod_description': False, 'aantal': False, 'client_ref': client_ref,
                    'lengte': False, 'tot_lengte': False, 'product_uom_qty': False})

                for m in self.move_lines:
                    if m.order_id and order == m.order_id:
                        desc = self.set_description(m)
                        aantal = self.set_product_uom_qty(m)
                        lengte = self.set_lengt(m)
                        tot_lengte = self.set_total_leng(m)
                        vals.append({'prod_code': m.product_id.default_code, 'prod_description': desc, 'aantal': aantal, 'client_ref': False,
                            'lengte': lengte, 'tot_lengte': tot_lengte, 'product_uom_qty': m.product_uom_qty})

        #for sort false sale order, display manually invoice line at last
        for move in self.move_lines:
            if not move.order_id:
                desc = self.set_description(move)
                aantal = self.set_product_uom_qty(move)
                lengte = self.set_lengt(move)
                tot_lengte = self.set_total_leng(move)
                vals.append({'prod_code': move.product_id.default_code, 'prod_description': desc, 'aantal': aantal, 'client_ref': False,
                    'lengte': lengte, 'tot_lengte': tot_lengte, 'product_uom_qty': move.product_uom_qty})

        return [vals, len(vals)]

    def set_description(self, move):
        if move.product_id:
            if move.product_id.description_sale:
                desc = move.product_id.description_sale
                return desc[0:60]
            else:
                desc = move.product_id.name
                return desc[0:60]
        if move.name:
            desc = move.name
            return desc[0:60]
        return ''

    def set_product_uom_qty(self, move):
        num = str(move.product_uom_qty).split('.')
        qty = num[0] + "," + num[1]
        return qty

    def set_lengt(self, move):
        length = float(move.zpro_length)
        final = str(length).split('.')
        final_len = final[0] + ',' + final[1]
        return final_len

    def set_total_leng(self, move):
        total_len = move.product_uom_qty * move.zpro_length
        lenge = str(total_len).split('.')
        total_final = lenge[0] + ',' + lenge[1]
        return total_final
