# -*- coding: utf-8 -*-
from openerp import models, fields, api

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_printed(self):
        self.is_print = True
        return ""

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, 'smt_invoice_report.account_invoice')

    @api.multi
    def get_multiple_so(self):
        so_list = []
        for line in self.invoice_line_ids:
            for order_line in line.sale_line_ids:
                if order_line.order_id.id not in so_list:
                    so_list.append(order_line.order_id.id)
                    if len(so_list) > 1:
                        return True
        return False

    @api.multi
    def get_multiple_so_1(self):
        so_list = []
        for line in self.invoice_line_ids:
            for order_line in line.sale_line_ids:
                if order_line.order_id.client_order_ref:
                    return True
        return False

    def get_notation_amt(self, amt):
        amount = str(amt).split('.')
        if len(amount) == 2:
            amount = amount[0] + "," + amount[1]
            return amount
        return amt

    @api.multi
    def get_product_invoice_lines(self,client_ref=False):
        product_invoices = []
        client_order_ref = []
        # client_order_ref = [(order_line.order_id,line) for line in self.invoice_line_ids for order_line in line.sale_line_ids]
        for line in self.invoice_line_ids :
            sale_line = (False,line)
            if line.sale_line_ids:
                sale_line = (line.sale_line_ids[0].order_id,line)
            client_order_ref.append(sale_line)
        if client_order_ref:
            for ref in client_order_ref:
                if (client_ref == ref[0]):
                    product_invoices.append({'price_subtotal' : ref[1].price_unit * ref[1].quantity * ref[1].zpro_length,
                        'default_code': ref[1].product_id.default_code,
                        'client_ref': False,
                        'description': ref[1].set_description(),
                        'qty': self.get_notation_amt(ref[1].quantity),
                        'length': self.get_notation_amt(ref[1].zpro_length),
                        'total_lenge': self.get_notation_amt(ref[1].quantity * ref[1].zpro_length),
#                         'price_unit': self.get_notation_amt(ref[1].price_unit)
                        'price_unit': self.get_notation_amt("{0:.3f}".format(ref[1].price_unit))
                        })
        else:
            for line in self.invoice_line_ids:
                product_invoices.append({'price_subtotal' : line.price_unit * line.quantity * line.zpro_length,
                        'default_code': line.product_id.default_code,
                        'client_ref': False,
                        'description': line.set_description(),
                        'qty': self.get_notation_amt(line.quantity),
                        'length': self.get_notation_amt(line.zpro_length),
                        'total_lenge': self.get_notation_amt(line.quantity * line.zpro_length),
#                         'price_unit': self.get_notation_amt(line.price_unit)
                        'price_unit': self.get_notation_amt("{0:.3f}".format(line.price_unit))
                        })
        return product_invoices

    @api.multi
    def get_invoice_lines(self):
        vals = []
        sale_order_lines = []
        false_sale_order_lines = []
        # sale_order_lines = list(set([order_line.order_id for line in self.invoice_line_ids for order_line in line.sale_line_ids]))
        for line in self.invoice_line_ids :
            sale_line = False
            if line.sale_line_ids:
                sale_line = line.sale_line_ids[0].order_id
            if sale_line:
                sale_order_lines.append(sale_line)
            else:
                false_sale_order_lines.append(sale_line)
        sale_order_lines = list(set(sale_order_lines))
        false_sale_order_lines = list(set(false_sale_order_lines))

        for sale_order in sale_order_lines:
            if sale_order and self.origin:
                client_ref = sale_order.name
                if sale_order.client_order_ref:
                    client_ref += ' ' + '/' + ' ' + sale_order.client_order_ref
                vals.append({'price_subtotal': False, 'default_code': False, 'client_ref': client_ref,
                    'description': False, 'qty': False, 'length': False, 'total_lenge': False,
                        'price_unit': False})
            vals.extend(self.get_product_invoice_lines(client_ref=sale_order))

        #for sort false sale order, display manually invoice line at last
        for so in false_sale_order_lines:
            vals.extend(self.get_product_invoice_lines(client_ref=so))

        # else:
        #     vals.extend(self.get_product_invoice_lines())
        return [vals, len(vals)]

    # @api.multi
    # def get_invoice_lines(self):
    #     vals = []
    #     client_reference = list(set([order_line.order_id.client_order_ref for line in self.invoice_line_ids for order_line in line.sale_line_ids]))
    #     if self.origin and len(self.origin.split(',')) >= 2 and client_reference:
    #         for client_ref in client_reference:
    #             if client_ref : 
    #                 vals.append({'price_subtotal' : False,'default_code':False,'client_ref':client_ref,
    #                     'description': False, 'qty':False, 'length':False,'total_lenge':False,
    #                     'price_unit':False})
    #             vals.extend(self.get_product_invoice_lines(client_ref=client_ref))
    #     else:
    #         vals.extend(self.get_product_invoice_lines())
    #     return vals


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    def set_cust_ref(self):
        desc = ""
        for order_line in self.sale_line_ids:
            if order_line.order_id.client_order_ref:
                desc = desc + order_line.order_id.client_order_ref
        return desc

    # to set product description that method working on group by invoice method working
    def set_description(self):
        if self.product_id:
            if self.product_id.description_sale:
                desc = self.product_id.description_sale
                return desc[0:60]
            else:
                desc = self.product_id.name
                return desc[0:60]
        if self.name:
            desc = self.name
            return desc[0:60]
        return ''

    # def set_quantity(self):
    #     if self.product_id:
    #         num = str(self.quantity).split('.')
    #         qty = num[0] + "," + num[1]
    #         return qty
    #     return ''

    # def set_length(self):
    #     length = float(self.zpro_length)
    #     final = str(length).split('.')
    #     final_len = final[0] + ',' + final[1]
    #     return final_len

    # def set_total_lenge(self):
    #     tottal_len = self.quantity * self.zpro_length
    #     tot_l = str(tottal_len).split('.')
    #     to_final = tot_l[0] + ',' + tot_l[1]
    #     return to_final

    # def set_price_unit(self):
    #     num = str(self.price_unit).split('.')
    #     price_unit = num[0] + "," + num[1]

    #     return price_unit

    # def set_price_subtotal(self):
    #     subtotal = self.price_unit * self.quantity * self.zpro_length
    #     num = str(subtotal).split('.')
    #     price_subtotal = num[0] + "," + num[1]

    #     return price_subtotal

class res_partner(models.Model):
    _inherit = 'res.partner'

    fin_reduction_id = fields.Many2one('financial.reduction', string='Financial Reduction')
