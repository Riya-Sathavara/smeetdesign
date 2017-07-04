# -*- coding: utf-8 -*-
from openerp import models, fields, api


class financial_reduction(models.Model):
    _name = "financial.reduction"
    _rec_name = "fin_reduction"

    fin_reduction = fields.Float(string="Financial Reduction", default=2.0)

    _order = 'fin_reduction'

    _sql_constraints = [
            ('fin_reduction_uniq', 'unique(fin_reduction)', 'Financial Reduction must be unique!'),
            ]

    @api.multi
    def name_get(self):

        result = []
        for financial_reduction in self:
            lang = self.env['res.lang'].search([('code', '=', self._context.get('lang'))])
            fin = str(financial_reduction.fin_reduction)
            if self._context.get('lang') == 'nl_BE':
                fin = fin.replace(".", lang.decimal_point)
            result.append((financial_reduction.id, fin))
        return result