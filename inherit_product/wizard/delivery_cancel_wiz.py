from openerp import api, fields, models, _
from openerp.exceptions import UserError


class DeliveryCancelWiz(models.TransientModel):
    _name = "delivery.cancel.wiz"

    @api.multi
    def cancel_confirmation(self):
        if self._context.get('active_ids',False):
            picking_ids = self.env['stock.picking'].browse(self._context.get('active_ids',False))
            for picking in picking_ids:
                picking.move_lines.action_cancel()