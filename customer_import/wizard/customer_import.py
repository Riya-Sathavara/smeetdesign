from openerp import api, fields, models, _
import base64
import csv
import cStringIO
# ============= To get to know which mail 
# class MailMessage(models.Model):
#     _inherit = "mail.message"
#   
#     test = fields.Boolean()
#   
#     @api.model
#     def create(self, vals):
#         vals.update({'test': True})
#         res = super(MailMessage, self).create(vals)
#         return res

class CustomerImport(models.TransientModel):
    _name = "customer.import.wiz"

    file_name = fields.Binary('Customer CSV File')
    datas_fname = fields.Char('File Name')

    @api.multi
    def import_partners(self):
        # =================== Correction for VAT calculation on Invoice. =======================================
#         inv_list = [128,132,167,177,197,212,217,226,227,229,233,236,238,311,345,348,398,404,  13,45,106,153,327,
#                     254,290,
#                     319,89,239,273,203,369,79,11,235,99,290,257,
#                     534,538,556,562,581,583,590,594,595,607,612,628,630,634,643,645,
#                     721,707,706,696,688,687,685,677,676,674,656,752]
#         inv_list = [752,694,556,164,162,159,145,144,142,138,137,136,113,124,119,118,117,109,108,107,105,104,99,98,93,88,87,85,83,82,81,77,75,50,47,46,44,42,40,39,31,24,23,22,16,15,12,8,6,5]
        
        
        #update for vendo bill
        inv_list = [426,768,771,848]


#         for invoice in self.env['account.invoice'].search([('id', 'in', inv_list)]):
        # ================ Calculate delivery status:: ==================
            # orders = self.env['sale.order'].search([])
            # for order in orders:
            #     order.delivery_status = 'draft'
            #     delivered_picking = [pick for pick in order.picking_ids if pick.state == 'done']
            #     if len(order.picking_ids) == len(delivered_picking):
            #         order.delivery_status = 'delivered'
            #     elif (len(order.picking_ids) != len(delivered_picking)) and len(delivered_picking) > 0:
            #         order.delivery_status = 'partial'
        # ========== for invoice mismatch calculations (Total Amount -> Amount Due=================
        for invoice in self.env['account.invoice'].search([('id', 'in', inv_list)]):
            payment_move_line = invoice.payment_move_line_ids
            if payment_move_line:
                payment_move_line.remove_move_reconcile()

            #cancel invoice
            invoice.action_cancel()

            #reset to draft invoice
            invoice.action_cancel_draft()

            invoice._onchange_invoice_line_ids()
            #validate invoice
            invoice.signal_workflow('invoice_open')
            if payment_move_line:
                self.pool.get('account.invoice').assign_outstanding_credit(self._cr, self._uid, invoice.id, payment_move_line.id, context=self._context)

        messages = self.env['mail.message'].search([('test', '=', True)])
        if messages:
            messages.unlink()
        return

        # ================== Call Invoice Line Onchange to calculate Tax. ======================
            # for line in self.env['account.invoice.line'].search([]):
            #     line.price_unit = line.price_unit
            #     line.invoice_id._onchange_invoice_line_ids()

        # ==============================================
            # for line in self.env['sale.order.line'].search([]):
            #     line.price_unit = line.price_unit

        # ==============================================
            # for line in self.env['purchase.order.line'].search([]):
            #     line.price_unit = line.price_unit

        # ===================Actual Customer Import Script==========================
#         partner_obj = self.env['res.partner']
#         country_obj = self.env['res.country']
#         data = base64.b64decode(self.file_name)
#         file_input = cStringIO.StringIO(data)
#          file_input.seek(0)
#         reader = csv.reader(file_input, delimiter=',',
#                             lineterminator='\r\n')
#         line = 0
#         for row in reader:
#             line += 1
#             if line == 1:
#                 continue
#             vals = {}
#             contact_vals = {}
#             print "row:",line
#             if row[1]:
#                 parent_id = False
#                 existing_parent_id = partner_obj.sudo().search([('name', '=', row[1])])
#                 country_id = country_obj.search([('code','=',row[5].upper())])
#                 vals.update({'customer': True,
#                         'ref': row[0],
#                         'name': row[1],
#                         'street': row[2],
#                         'street2': row[3],
#                         'zip': row[4],
#                         'country_id': country_id and country_id.id or False,
#                         'city': row[6],
#                         'phone': row[7],
#                         'fax': row[8],
#                         'mobile': row[9],
#                         'email': row[10],
#                         'vat': row[11],
#                         })
#                 if not existing_parent_id:
#                     parent_id = partner_obj.sudo().create(vals)
#                 else:
#                     partner_obj.sudo().write(vals)
#                     parent_id = existing_parent_id
# #                 parent_id
#                 if row[14]:
#                     country_id = country_obj.search([('code', '=', row[22].upper())])
#                     contact_vals.update({
#                         'name': row[14],
#                         'function': row[13],
#                         'type': row[12].lower(),
#                         'mobile': row[15],
#                         'email': row[17],
#                         'street': row[18],
#                         'street2': row[19],
#                         'zip': row[20],
#                         'city': row[21],
#                         'country_id': country_id and country_id.id or False,
#                         })

#                     existing_child_id = partner_obj.sudo().search([('name', '=', row[14])])
#                     if existing_child_id != existing_parent_id:
#                         contact_vals.update({'parent_id': parent_id and parent_id.id or False})
#                     if not existing_child_id:
#                         partner_obj.sudo().create(contact_vals)
#                     else:
#                         partner_obj.sudo().write(contact_vals)
