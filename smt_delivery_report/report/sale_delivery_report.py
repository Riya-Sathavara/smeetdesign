from openerp.osv import osv
from openerp.report import report_sxw


class sale_delivery_report(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(sale_delivery_report, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'set_company_name': self._set_company_name,
            'set_name': self._set_name,
            'set_first_name': self._set_first_name,
            'set_tax_line': self._set_tax_line,
            'set_product_uom_qty': self._set_product_uom_qty,
            'set_taxes': self._set_taxes,
            'set_description': self._set_description,
            'set_price_unit': self._set_price_unit,
            'set_amount': self._set_amount,
            'set_total_leng': self._set_total_leng,
            'set_lengt': self._set_lengt,
        })

    def _set_lengt(self, object):
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

    def _set_total_leng(self, object):
        total_len = object.product_uom_qty * object.zpro_length
        lenge = str(total_len).split('.')
        total_final = lenge[0] + ',' + lenge[1]
        return total_final

    def _set_amount(self, amount):
        num = str(amount).split('.')
        amount = num[0] + "," + num[1]
        return amount
    def _set_price_subtotal(self, object):
        num = str(object.price_subtotal).split('.')
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
        if object.invoice_line_tax_ids:
            for tax in object.invoice_line_tax_ids:
                if len(object.invoice_line_tax_ids) == 1:
                    taxes += tax.name
                else:
                    taxes += "," + tax.name

        return taxes
    def _set_product_uom_qty(self, object):
        num = str(object.product_uom_qty).split('.')
        qty = num[0] + "," + num[1]
        return qty

    def _set_tax_line(self, object):
        taxes = []
        data = []
        for l in object.invoice_line_ids:
            if l.invoice_line_tax_ids:
                t = [x.id for x in l.invoice_line_tax_ids[0]]
                if t[0] not in taxes:
                    taxes.append(t[0])

        tax_data = {}
        for tax in taxes:
            for line in object.invoice_line_ids:
                if line.invoice_line_tax_ids:
                    if line.invoice_line_tax_ids[0].id == tax:
                        if line.invoice_line_tax_ids[0].id in tax_data:
                            basis = tax_data.get(line.invoice_line_tax_ids[0].id)[1] + line.price_subtotal
                            btw = tax_data.get(line.invoice_line_tax_ids[0].id)[2] + + round((line.price_subtotal * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 2)
                            tax_data[line.invoice_line_tax_ids[0].id] = [line.invoice_line_tax_ids[0].description, basis, btw, basis + btw]
                        else:
                            basis = line.price_subtotal
                            btw = round((line.price_subtotal * (round(line.invoice_line_tax_ids[0].amount, 2) / 100)), 2)
                            tax_data.update({line.invoice_line_tax_ids[0].id: [line.invoice_line_tax_ids[0].name
                                                                , basis
                                                                , btw
                                                                , (basis + btw)]})
        for t in tax_data:
            tmp = str(tax_data[t][1]).split('.')
            qty = tmp[0] + "," + tmp[1]
            tax_data[t][1] = qty

            tmp = str(tax_data[t][2]).split('.')
            qty = tmp[0] + "," + tmp[1]
            tax_data[t][2] = qty

            tmp = str(tax_data[t][3]).split('.')
            qty = tmp[0] + "," + tmp[1]
            tax_data[t][3] = qty
            data.append(tax_data[t])
        return data

    def _set_name(self, object):
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

    def _set_first_name(self, object):
        name = ""
        if object.partner_id.is_company and object.partner_id.child_ids:
            if len(object.partner_id.child_ids[0].name.split(' ')) > 1:
                name = object.partner_id.child_ids[0].name.split(' ')[0]
        if not object.partner_id.is_company and object.partner_id.parent_id:
            if len(object.partner_id.name.split(' ')) > 1:
                name = object.partner_id.name.split(' ')[0]

        return name
class report_sale_delivery_ext(osv.AbstractModel):
    _name = 'report.smt_delivery_report.delivery_report_ext'
    _inherit = 'report.abstract_report'
    _template = 'smt_delivery_report.delivery_report_ext'
    _wrapped_report_class = sale_delivery_report
