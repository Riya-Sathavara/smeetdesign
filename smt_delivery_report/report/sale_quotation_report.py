from openerp.osv import osv
from openerp.report import report_sxw


class sale_quotation_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_quotation_report, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'set_company_name': self._set_company_name,
            'set_delivery_name': self._set_delivery_name,
            'set_name': self._set_name,
            'set_tax_line': self._set_tax_line,
            'set_quantity': self._set_quantity,
            'set_taxes': self._set_taxes,
            'set_description': self._set_description,
            'set_price_subtotal': self._set_price_subtotal,
            'set_price_unit': self._set_price_unit,
            'set_amount': self._set_amount,
            'set_length': self._set_length,
            'set_total_lenge': self._set_total_lenge,
        })
    def _set_length(self, object):
        length = float(object.zpro_length)
        final = str(length).split('.')
        final_len = final[0] + ',' + final[1]
        return final_len

    def _set_company_name(self,object):
        if object.partner_id.is_company:
            return object.partner_id.name
        if not object.partner_id.is_company and object.partner_id.parent_id:
            return object.partner_id.parent_id.name
        return ""

    def _set_total_lenge(self, object):
        tottal_len = object.product_uom_qty * object.zpro_length
        tot_l = str(tottal_len).split('.')
        to_final = tot_l[0] + ',' + tot_l[1]
        return to_final

    def _set_amount(self, amount):
        num = str(amount).split('.')
        amount = num[0] + "," + num[1]
        return amount

    def _set_price_subtotal(self, object):
        discount = 0.0
#         if object.discount > 0.0:
#             discount = object.price_unit * (object.discount / 100)
        subtotal = (object.price_unit - discount) * object.product_uom_qty * object.zpro_length
        num = str(subtotal).split('.')
        price_subtotal = num[0] + "," + num[1]

        return price_subtotal

    def _set_price_unit(self, object):
        num = str(object.price_unit).split('.')
        price_unit = num[0] + "," + num[1]

        return price_unit

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
        if object.tax_id:
            for tax in object.tax_id:
                if len(object.tax_id) == 1:
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

    def _set_quantity(self, object):
        num = str(object.product_uom_qty).split('.')
        qty = num[0] + "," + num[1]
        return qty

    def _set_tax_line(self,object):
        taxes = []
        data = []

        for l in object.order_line:
            if l.tax_id:
                t = [x.id for x in l.tax_id[0]]
                if t[0] not in taxes:
                    taxes.append(t[0])

        tax_data = {}
        for tax in taxes:
            for line in object.order_line:
                if line.tax_id:
                    if line.tax_id[0].id == tax:
                        if line.tax_id[0].id in tax_data:
                            basis = tax_data.get(line.tax_id[0].id)[1] + line.price_subtotal
                            btw = tax_data.get(line.tax_id[0].id)[2] + + round((line.price_subtotal * (round(line.tax_id[0].amount,2) / 100)),2)
                            tax_data[line.tax_id[0].id] = [line.tax_id[0].description,basis ,btw ,basis + btw]
                        else:
                            basis = line.price_subtotal
                            btw = round((line.price_subtotal * (round(line.tax_id[0].amount,2) / 100)),2)
                            tax_data.update({line.tax_id[0].id:[line.tax_id[0].name
                                                                ,basis
                                                                ,btw
                                                                ,(basis + btw) ]})                    

        for t in tax_data:
            tmp = str(tax_data[t][1]).split('.')
            qty = tmp[0]+","+tmp[1]
            tax_data[t][1] = qty

            tmp = str(tax_data[t][2]).split('.')
            qty = tmp[0]+","+tmp[1]
            tax_data[t][2] = qty

            tmp = str(tax_data[t][3]).split('.')
            qty = tmp[0] + "," + tmp[1]
            tax_data[t][3] = qty
            data.append(tax_data[t])
        return data

    def _set_name(self, object):
        name = ""
        if object.partner_id.is_company and object.partner_id.child_ids:
            if object.partner_id.child_ids[0].name:
                name = object.partner_id.child_ids[0].name
            if not object.partner_id.child_ids[0].name:
                name = object.partner_id.name
#             if len(object.partner_id.child_ids[0].name.split(' ')) > 1:
#                 name = object.partner_id.child_ids[0].name.split(' ')[1]
#             if len(object.partner_id.child_ids[0].name.split(' ')) == 1:
#                 name = object.partner_id.child_ids[0].name.split(' ')[0]

        if object.partner_id.is_company and not object.partner_id.child_ids:
            name = False
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

    def _set_delivery_name(self, object):

        name = ""
        if object.partner_shipping_id.is_company and object.partner_shipping_id.child_ids:
            if object.partner_shipping_id.child_ids[0].name:
                name = object.partner_shipping_id.child_ids[0].name
            if not object.partner_shipping_id.child_ids[0].name:
                name = object.partner_shipping_id.name

        if object.partner_shipping_id.is_company and not object.partner_shipping_id.child_ids:
            name = ''

        if not object.partner_shipping_id.is_company:
            if object.partner_shipping_id.name:
                name = object.partner_shipping_id.name

        return name

class report_sale_quo_invoice_ext(osv.AbstractModel):
    _name = 'report.smt_delivery_report.sale_quotation_report'
    _inherit = 'report.abstract_report'
    _template = 'smt_delivery_report.sale_quotation_report'
    _wrapped_report_class = sale_quotation_report
