from openerp.osv import osv
from openerp.report import report_sxw


class picking_operation(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking_operation, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'set_name': self._set_name,
            'set_company_name': self._set_company_name,

        })
    def _set_company_name(self,object):
        if object.partner_id.is_company:
            return object.partner_id.name
        if not object.partner_id.is_company and object.partner_id.parent_id:
            return object.partner_id.parent_id.name
        return ""

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

class report_picking_operation_ext(osv.AbstractModel):
    _name = 'report.stock.report_picking'
    _inherit = 'report.abstract_report'
    _template = 'stock.report_picking'
    _wrapped_report_class = picking_operation
