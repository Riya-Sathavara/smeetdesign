from openerp import api, fields, models, _

class product_template(models.Model):
    _inherit = 'product.template'

    @api.multi
    def set_vendors(self):
        ref_dict = {3187: 'RH%', 3105: 'JO%'}
        vals = {}
        vendor_list = []
        for key, val in ref_dict.items():
            i = 1
            templates = self.search([('default_code', 'like', val)])
            for template in templates:
                vals.update({'product_tmpl_id': template.id,
                             'name': key,
                             'product_code': template.default_code,
                             'delay': 4
                             })
                existing_vendor = self.env['product.supplierinfo'].search([('product_tmpl_id', '=', template.id), ('name', '=', key)])
                if existing_vendor:
                    existing_vendor.write(vals)
                else:
                    self.env['product.supplierinfo'].create(vals)
                    i += 1
