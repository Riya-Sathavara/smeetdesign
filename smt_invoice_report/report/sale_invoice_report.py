from openerp.osv import osv
from openerp.report import report_sxw


class sale_invoice_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_invoice_report, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'set_company_name': self._set_company_name,
            'set_name': self._set_name,
            'set_first_name': self._set_first_name,
            'set_tax_line': self._set_tax_line,
            'set_quantity': self._set_quantity,
            'set_taxes': self._set_taxes,
            'set_description': self._set_description,
            'set_price_subtotal': self._set_price_subtotal,
            'set_price_unit': self._set_price_unit,
            'set_amount': self._set_amount,
            'set_amount_1': self._set_amount_1,
            'set_unit_price': self._set_unit_price,
            'set_total_lenge': self._set_total_lenge,
            'set_length': self._set_length,
            'set_cust_ref': self._set_cust_ref,
            'set_reference': self._set_reference,

        })

    def _set_reference(self, object):
        if object.name and len(object.name) >= 18:
            return False
        return object.name

    def _set_cust_ref(self, object):
        desc = ""
        for order_line in object.sale_line_ids:
            if order_line.order_id.client_order_ref:
                desc = desc + order_line.order_id.client_order_ref
        return desc
    # Need To Comment
    def _set_length(self, object):
        length = float(object.zpro_length)
        final = str(length).split('.')
        final_len = final[0] + ',' + final[1]
        return final_len

    # Need To Comment
    def _set_total_lenge(self, object):
        tottal_len = object.quantity * object.zpro_length
        tot_l = str(tottal_len).split('.')
        to_final = tot_l[0] + ',' + tot_l[1]
        return to_final

    def _set_unit_price(self, object):
        if object.price_unit:
            ab = object.product_id.zpro_length * object.price_unit
            num = str(ab).split('.')
            price_unit = num[0] + "," + num[1]

            return price_unit

    def _set_amount(self, amount):
        num = str(amount).split('.')
        amount = num[0] + "," + num[1]
        return amount

    def _set_amount_1(self, object):
        fin_reduction = 0.0
        # Dilip's Fin Reduction Condition
        # if object.partner_id.fin_reduction_id:
            # fin_reduction = object.partner_id.fin_reduction_id.fin_reduction
            # amount = (object.amount_untaxed * (fin_reduction / 100))
            # num = str(round(amount, 2)).split('.')
            # amount = num[0] + "," + num[1]
            # return amount
        if object.tot_fin_reduction:
            num = str(round(object.tot_fin_reduction, 2)).split('.')
            fin_reduction = num[0] + "," + num[1]
        return fin_reduction

    # Need To Comment
    def _set_price_subtotal(self, object):
        subtotal = object.price_unit * object.quantity * object.zpro_length
        num = str(subtotal).split('.')
        price_subtotal = num[0] + "," + num[1]

        return price_subtotal

    # Need To Comment
    def _set_price_unit(self, object):
        num = str(object.price_unit).split('.')
        price_unit = num[0] + "," + num[1]

        return price_unit

    # in production not commit so that method working on that case
    def _set_description(self, object):
        if object.product_id:
            if object.product_id.description_sale:
                desc = object.product_id.description_sale
                return desc[0:60]
            else:
                desc = object.product_id.name
                return desc[0:60]
        if object.name:
            desc = object.name
            return desc[0:60]
        return ''

    def _set_taxes(self, object):
        taxes = ''
        if object.invoice_line_tax_ids:
            for tax in object.invoice_line_tax_ids:
                if len(object.invoice_line_tax_ids) == 1:
                    if tax.amount_type == 'group' and tax.children_tax_ids:
                        taxes += str(int(tax.children_tax_ids[0].amount)) + "%"
                    else:
                        taxes += str(int(tax.amount)) + "%"

                else:
                    if tax.amount_type == 'group' and tax.children_tax_ids:
                        taxes += "," + str(int(tax.children_tax_ids[0].amount)) + "%"
                    else:
                        taxes += "," + str(int(tax.amount)) + "%"
        if taxes and taxes[0] == ',':
            taxes = taxes[1:]
        return taxes
#     def _set_taxes(self,object):
#         taxes = ''
#         if object.invoice_line_tax_ids:
#             for tax in  object.invoice_line_tax_ids:
#                 if len(object.invoice_line_tax_ids) == 1:
#                     if object.invoice_line_tax_ids.amount_type != 'group':
#                         taxes += (str(tax.amount))
#                     else:
#                         if tax.amount_type == 'group':
#                             for child_tax in tax.children_tax_ids:
#                                 ret = tax.children_tax_ids[0].amount
#                                 return ret
#                 else:
#                     if object.invoice_line_tax_ids.amount_type != 'group':
#                         taxes += ","+ (str(tax.amount))
#                     else:
#                         if tax.amount_type == 'group':
#                             for child_tax in tax.children_tax_ids:
#                                 ret = tax.children_tax_ids[0].amount
#                                 return ret
#         return taxes

    def _set_quantity(self, object):
        if object.product_id:
            num = str(object.quantity).split('.')
            qty = num[0] + "," + num[1]
            return qty
        return ''
    # def _set_tax_line(self,object):
    #     taxes = []
    #     data = []

    #     for l in object.invoice_line_ids:
    #         if l.invoice_line_tax_ids:
    #             t = [x.id for x in l.invoice_line_tax_ids[0]]
    #             if t[0] not in taxes:
    #                 taxes.append(t[0])

    #     tax_data = {}
    #     for tax in taxes:
    #         for line in object.invoice_line_ids:
    #             if line.invoice_line_tax_ids:
    #                 if line.invoice_line_tax_ids[0].id == tax:
    #                     fin_reduction = 0.0
    #                     if object.partner_id.fin_reduction_id:
    #                         fin_reduction = object.partner_id.fin_reduction_id.fin_reduction
    #                     if line.invoice_line_tax_ids[0].id in tax_data:
    #                         basis = tax_data.get(line.invoice_line_tax_ids[0].id)[1] + line.price_subtotal
    #                         btw = tax_data.get(line.invoice_line_tax_ids[0].id)[2] + round(((line.price_subtotal - (line.price_subtotal * (fin_reduction / 100))) * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 2)
    #                         tax_data[line.invoice_line_tax_ids[0].id] = [line.invoice_line_tax_ids[0].description, basis, btw, basis + btw]
    #                     else:
    #                         basis = line.price_subtotal
    #                         btw = round(((line.price_subtotal - (line.price_subtotal * (fin_reduction / 100))) * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 2)
    #                         tax_data.update({line.invoice_line_tax_ids[0].id: [line.invoice_line_tax_ids[0].description
    #                                                             , basis
    #                                                             , btw
    #                                                             , (basis + btw)]})

    #     for t in tax_data:
    #         tmp = str(tax_data[t][1]).split('.')
    #         qty = tmp[0] + "," + tmp[1]
    #         tax_data[t][1] = qty

    #         tmp = str(tax_data[t][2]).split('.')
    #         qty = tmp[0] + "," + tmp[1]
    #         tax_data[t][2] = qty

    #         tmp = str(tax_data[t][3]).split('.')
    #         qty = tmp[0] + "," + tmp[1]
    #         tax_data[t][3] = qty

    #         data.append(tax_data[t])

    #     return data
    def _set_tax_line(self,object):
        taxes = []
        data = []
        for line in object.tax_line_ids:
            tmp = []
            base = 0.0
            amount_tax = 0.0
            tmp.append(line.name)

            num = str((object.amount_untaxed - object.tot_fin_reduction)).split('.')
            base = num[0] + "," + num[1]
            tmp.append(base)

            tax = str((object.amount_tax)).split('.')
            amount_tax = tax[0] + "," + tax[1]
            tmp.append(amount_tax)

            data.append(tmp)
#         for l in object.invoice_line_ids:
#             if l.invoice_line_tax_ids:
#                 t = [x.id for x in l.invoice_line_tax_ids[0]]
#                 if t[0] not in taxes:
#                     taxes.append(t[0])
# 
#         tax_data = {}
#         for tax in taxes:
#             for line in object.invoice_line_ids:
#                 if line.invoice_line_tax_ids:
#                     if line.invoice_line_tax_ids[0].id == tax:
#                         fin_reduction = 0.0
#                         if object.partner_id.fin_reduction_id:
#                             fin_reduction = object.partner_id.fin_reduction_id.fin_reduction
#                         if line.invoice_line_tax_ids[0].id in tax_data:
#                             basis = tax_data.get(line.invoice_line_tax_ids[0].id)[1] + line.price_subtotal
#                             btw = tax_data.get(line.invoice_line_tax_ids[0].id)[2] + round(((line.price_subtotal - (line.price_subtotal * (fin_reduction / 100))) * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 3)
#                             tax_data[line.invoice_line_tax_ids[0].id] = [line.invoice_line_tax_ids[0].description, basis, btw, basis + btw]
#                         else:
#                             basis = line.price_subtotal
#                             btw = round(((line.price_subtotal - (line.price_subtotal * (fin_reduction / 100))) * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 3)
#                             tax_data.update({line.invoice_line_tax_ids[0].id: [line.invoice_line_tax_ids[0].description
#                                                                 , basis
#                                                                 , btw
#                                                                 , (basis + btw)]})
# 
#         for tax_line in object.tax_line_ids:
#             tax_line.amount
#             tax_line.base
# 
#         for t in tax_data:
#             finall = tax_data[t][1] - object.tot_fin_reduction
# #             tmp = str(tax_data[t][1]).split('.')
#             tmp = str(finall).split('.')
#             qty = tmp[0] + "," + tmp[1]
#             tax_data[t][1] = qty
# 
# #               here we have fix this issue for 21% and 0%  
# #             if str((tax_data[t][2] % 0.100)) == str(0.095):
# #                 tmp1 = round(tax_data[t][2], 1)
# #             else:
# #                 tmp1 = round(tax_data[t][2], 2)
#             tmp1 = object.amount_tax
#             tmp = str(tmp1).split('.')
#             qty = tmp[0] + "," + tmp[1]
#             tax_data[t][2] = qty
# 
# #             if str((tax_data[t][3] % 0.100)) == str(0.095):
# #                 tmp2 = round(tax_data[t][3], 1)
# #             else:
# #                 tmp2 = round(tax_data[t][3], 2)
#             tmp2 = object.amount_total
#             tmp = str(tmp2).split('.')
#             qty = tmp[0] + "," + tmp[1]
#             tax_data[t][3] = qty
# 
#             data.append(tax_data[t])

        return data

    def _set_company_name(self,object):
        if object.partner_id.is_company:
            return object.partner_id.name
        if not object.partner_id.is_company and object.partner_id.parent_id:
            return object.partner_id.parent_id.name
        return ""

    def _set_name(self,object):
        name = ""

        if object.partner_id.is_company and object.partner_id.child_ids and object.partner_id.child_ids[0].name:
            if object.partner_id.child_ids[0].name:
                name = object.partner_id.child_ids[0].name
            if not object.partner_id.child_ids[0].name:
                name = object.partner_id.name
#             if len(object.partner_id.child_ids[0].name.split(' ')) > 1:
#                 name = object.partner_id.child_ids[0].name.split(' ')[1]
#             if len(object.partner_id.child_ids[0].name.split(' ')) == 1:
#                 name = object.partner_id.child_ids[0].name.split(' ')[0]

        if object.partner_id.is_company and not object.partner_id.child_ids:
            name = object.partner_id.name
#             if len(object.partner_id.name.split(' ')) > 1:
#                 name = object.partner_id.name.split(' ')[1]
#             if len(object.partner_id.name.split(' ')) == 1:
#                 name = object.partner_id.name.split(' ')[0]

        if not object.partner_id.is_company:
            if object.partner_id.name:
                name = object.partner_id.name
#                 if len(object.partner_id.name.split(' ')) > 1:
#                     name = object.partner_id.name.split(' ')[1]
#                 if len(object.partner_id.name.split(' ')) == 1:
#                     name = object.partner_id.name.split(' ')[0]

        return name

    def _set_first_name(self,object):

        name = ""
        if object.partner_id.is_company and object.partner_id.child_ids:
            if len(object.partner_id.child_ids[0].name.split(' ')) > 1:
                name = object.partner_id.child_ids[0].name.split(' ')[0]

        if not object.partner_id.is_company and object.partner_id.parent_id:
            if len(object.partner_id.name.split(' ')) > 1:
                name = object.partner_id.name.split(' ')[0]

        return name



class report_sale_invoice_ext(osv.AbstractModel):
    _name = 'report.smt_invoice_report.account_invoice'
    _inherit = 'report.abstract_report'
    _template = 'smt_invoice_report.account_invoice'
    _wrapped_report_class = sale_invoice_report
