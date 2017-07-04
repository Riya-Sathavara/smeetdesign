# -*- coding: utf-8 -*-
from openerp import models, fields, api
from openerp.tools.float_utils import float_compare


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity', 'invoice_id.fin_reduction_id',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id', 'zpro_length')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        taxes = False

        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity * self.zpro_length, product=self.product_id, partner=self.invoice_id.partner_id)
        price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
#         if self.zpro_length:
#             price_subtotal_signed = price_subtotal_signed * self.zpro_length
        self.price_subtotal = price_subtotal_signed

        if self.invoice_id.currency_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign

    @api.multi
    @api.depends('quantity', 'zpro_length')
    def _get_total_length(self):
        for line in self:
            line.total_length = line.quantity * line.zpro_length

    @api.multi
    def _get_sale_reference(self):
        for invoice_line in self:
            sale_ref = False
            if invoice_line.sale_line_ids and invoice_line.sale_line_ids[0] and invoice_line.sale_line_ids[0].order_id:
                sale_ref = invoice_line.sale_line_ids[0].order_id.id
            invoice_line.order_id = sale_ref

    zpro_length = fields.Float(string="Lengte", default=1)
    price_subtotal = fields.Monetary(string='Amount',
        store=True, readonly=True, compute='_compute_price')
    price_subtotal_signed = fields.Monetary(string='Amount Signed', currency_field='company_currency_id',
        store=True, readonly=True, compute='_compute_price',
        help="Total amount in the currency of the company, negative for credit notes.")
    total_length = fields.Float(string="Total Lengte", compute='_get_total_length',readonly=True)
    order_id = fields.Many2one('sale.order','Order',compute='_get_sale_reference')

    @api.onchange('product_id')
    def _onchange_product_id(self):
        res = super(AccountInvoiceLine, self)._onchange_product_id()
        if self.product_id:
            self.zpro_length = self.product_id.zpro_length
        return res

class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.one
    @api.depends('fin_reduction_id', 'invoice_line_ids.price_subtotal')
    def _tot_fin_reduction(self):
        fin_reduction = 0.0
        if self.fin_reduction_id:
            for line in self.invoice_line_ids:
                fin_reduction += line.price_subtotal * (self.fin_reduction_id.fin_reduction / 100)
        self.tot_fin_reduction = fin_reduction

    fin_reduction_id = fields.Many2one('financial.reduction', string='Financial Reduction', track_visibility='onchange')
    tot_fin_reduction = fields.Monetary(string='Total Financial Reduction', readonly=True, compute='_tot_fin_reduction')
    is_print = fields.Boolean(string='Invoice Print')
    origin = fields.Char(string='Source Document',
        help="Reference of the document that produced this invoice.",readonly=True, states={'draft': [('readonly', False)]},copy=False)

    @api.onchange('partner_id', 'company_id')
    def _onchange_partner_id(self):
        res = super(AccountInvoice, self)._onchange_partner_id()
#         if self.partner_id.fin_reduction_id:
        if self.type in ['out_invoice', 'out_refund']:
            self.fin_reduction_id = self.partner_id.fin_reduction_id

        return res

    @api.onchange('purchase_id')
    def purchase_order_change(self):
        if not self.purchase_id:
            return {}
        if not self.partner_id:
            self.partner_id = self.purchase_id.partner_id.id

        new_lines = self.env['account.invoice.line']
        for line in self.purchase_id.order_line:
            # Load a PO line only once
            if line in self.invoice_line_ids.mapped('purchase_line_id'):
                continue
            if line.product_id.purchase_method == 'purchase':
                qty = line.product_qty - line.qty_invoiced
            else:
                qty = line.qty_received - line.qty_invoiced
            if float_compare(qty, 0.0, precision_rounding=line.product_uom.rounding) <= 0:
                qty = 0.0
            taxes = line.taxes_id
            invoice_line_tax_ids = self.purchase_id.fiscal_position_id.map_tax(taxes)
            data = {
                'purchase_line_id': line.id,
                'name': line.name,
                'origin': self.purchase_id.origin,
                'uom_id': line.product_uom.id,
                'product_id': line.product_id.id,
                'account_id': self.env['account.invoice.line'].with_context({'journal_id': self.journal_id.id, 'type': 'in_invoice'})._default_account(),
                'price_unit': line.order_id.currency_id.compute(line.price_unit, self.currency_id, round=False),
                'quantity': qty,
                'discount': 0.0,
                'account_analytic_id': line.account_analytic_id.id,
                'invoice_line_tax_ids': invoice_line_tax_ids.ids,
                'zpro_length': line.zpro_length,
                'total_length': line.total_length,
            }
            account = new_lines.get_invoice_line_account('in_invoice', line.product_id, self.purchase_id.fiscal_position_id, self.env.user.company_id)
            if account:
                data['account_id'] = account.id
            new_line = new_lines.new(data)
            new_line._set_additional_fields(self)
            new_lines += new_line

        self.invoice_line_ids += new_lines
        self.purchase_id = False
        return {}

    @api.onchange('invoice_line_ids', 'fin_reduction_id')
    def _onchange_invoice_line_ids(self):
        taxes_grouped = self.get_taxes_values()
        tax_lines = self.tax_line_ids.browse([])
        for tax in taxes_grouped.values():
            tax_lines += tax_lines.new(tax)
        self.tax_line_ids = tax_lines
        return

    @api.multi
    def copy(self, default=None):
        res = super(AccountInvoice, self).copy(default=default)
        res._onchange_invoice_line_ids()
        return res

    @api.multi
    @api.depends('fin_reduction_id')
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
#             taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            quantity = 0.0
            if line.zpro_length:
                fin_reduction = 0.0
                if self.fin_reduction_id:
                    fin_reduction = self.fin_reduction_id.fin_reduction
                quantity = (line.quantity * line.zpro_length) - ((line.quantity * line.zpro_length) * (fin_reduction / 100))
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = {
                    'invoice_id': self.id,
                    'name': tax['name'],
                    'tax_id': tax['id'],
                    'amount': tax['amount'],
                    'manual': False,
                    'sequence': tax['sequence'],
                    'account_analytic_id': tax['analytic'] and line.account_analytic_id.id or False,
                    'account_id': self.type in ('out_invoice', 'in_invoice') and (tax['account_id'] or line.account_id.id) or (tax['refund_account_id'] or line.account_id.id),
                }

                # If the taxes generate moves on the same financial account as the invoice line,
                # propagate the analytic account from the invoice line to the tax line.
                # This is necessary in situations were (part of) the taxes cannot be reclaimed,
                # to ensure the tax move is allocated to the proper analytic account.
                if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                    val['account_analytic_id'] = line.account_analytic_id.id

                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
        return tax_grouped

    @api.model
    def create(self, vals):
        if vals.get('partner_id'):
            partner_obj = self.env['res.partner'].browse(vals.get('partner_id'))
            vals.update({'fin_reduction_id': partner_obj.fin_reduction_id.id})
        res = super(AccountInvoice, self).create(vals)
        return res

    @api.multi
    def action_date_assign(self):
        if self.type in ['out_invoice', 'out_refund']:
            self.compute_taxes()
        res = super(AccountInvoice, self).action_date_assign()
        return res

class AccountTax(models.Model):
    _inherit = 'account.tax'


    #overrid for rounding issue for amount in invoice  (0.442 * 100   =  44.20)
#     @api.v8
#     def compute_all(self, price_unit, currency=None, quantity=1.0, product=None, partner=None):
#         """ Returns all information required to apply taxes (in self + their children in case of a tax goup).
#             We consider the sequence of the parent for group of taxes.
#                 Eg. considering letters as taxes and alphabetic order as sequence :
#                 [G, B([A, D, F]), E, C] will be computed as [A, D, F, C, E, G]
# 
#         RETURN: {
#             'total_excluded': 0.0,    # Total without taxes
#             'total_included': 0.0,    # Total with taxes
#             'taxes': [{               # One dict for each tax in self and their children
#                 'id': int,
#                 'name': str,
#                 'amount': float,
#                 'sequence': int,
#                 'account_id': int,
#                 'refund_account_id': int,
#                 'analytic': boolean,
#             }]
#         } """
#         if len(self) == 0:
#             company_id = self.env.user.company_id
#         else:
#             company_id = self[0].company_id
#         if not currency:
#             currency = company_id.currency_id
#         taxes = []
#         # By default, for each tax, tax amount will first be computed
#         # and rounded at the 'Account' decimal precision for each
#         # PO/SO/invoice line and then these rounded amounts will be
#         # summed, leading to the total amount for that tax. But, if the
#         # company has tax_calculation_rounding_method = round_globally,
#         # we still follow the same method, but we use a much larger
#         # precision when we round the tax amount for each line (we use
#         # the 'Account' decimal precision + 5), and that way it's like
#         # rounding after the sum of the tax amounts of each line
#         prec = currency.decimal_places
#         if company_id.tax_calculation_rounding_method == 'round_globally' or not bool(self.env.context.get("round", True)):
#             prec += 5
#         total_excluded = total_included = base = round(price_unit * quantity, 3)
# 
#         # Sorting key is mandatory in this case. When no key is provided, sorted() will perform a
#         # search. However, the search method is overridden in account.tax in order to add a domain
#         # depending on the context. This domain might filter out some taxes from self, e.g. in the
#         # case of group taxes.
#         for tax in self.sorted(key=lambda r: r.sequence):
#             if tax.amount_type == 'group':
#                 ret = tax.children_tax_ids.compute_all(price_unit, currency, quantity, product, partner)
#                 total_excluded = ret['total_excluded']
#                 base = ret['base']
#                 total_included = ret['total_included']
#                 tax_amount = total_included - total_excluded
#                 taxes += ret['taxes']
#                 continue
# 
#             tax_amount = tax._compute_amount(base, price_unit, quantity, product, partner)
#             if company_id.tax_calculation_rounding_method == 'round_globally' or not bool(self.env.context.get("round", True)):
#                 tax_amount = round(tax_amount, 3)
#             else:
#                 tax_amount = round(tax_amount, 3)
# 
#             if tax.price_include:
#                 total_excluded -= tax_amount
#                 base -= tax_amount
#             else:
#                 total_included += tax_amount
# 
#             if tax.include_base_amount:
#                 base += tax_amount
# 
#             taxes.append({
#                 'id': tax.id,
#                 'name': tax.with_context(**{'lang': partner.lang} if partner else {}).name,
#                 'amount': tax_amount,
#                 'sequence': tax.sequence,
#                 'account_id': tax.account_id.id,
#                 'refund_account_id': tax.refund_account_id.id,
#                 'analytic': tax.analytic,
#             })
# 
#         return {
#             'taxes': sorted(taxes, key=lambda k: k['sequence']),
#             'total_excluded': round(total_excluded, 3) if bool(self.env.context.get("round", True)) else total_excluded,
#             'total_included': round(total_included, 3) if bool(self.env.context.get("round", True)) else total_included,
#             'base': base,
#         }
