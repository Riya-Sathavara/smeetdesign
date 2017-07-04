# -*- coding: utf-8 -*-
from openerp import models, fields


class pro_plat_nbr(models.Model):
    _name = "product.platnumber"

    name = fields.Char(string="Product Name", required=True)
#     product_id = fields.Many2one('product.product', string="Product id")

class product_template(models.Model):
    _inherit = 'product.template'

    zmat_no = fields.Char(string="Materiaalnummer")
    zpro_width = fields.Integer(string="Breedte")
    zpro_length = fields.Float(string="Lengte", default=1)
    zpro_measur = fields.Char(string="Eenheid")
    zpro_thik = fields.Char(string="Dikte")
    zcoating = fields.Char(string="Afwerking")
    zcolor = fields.Char(string="Kleur")
    zemb = fields.Char(string="Structuur")
    zpro_vol = fields.Integer(string="Verpakking")
    zean = fields.Char(string="EAN")
    zpro_palnt_ids = fields.Many2many('product.platnumber', string="Plaatnummer")
    type = fields.Selection([('product', 'Stockable Product'), ('consu', 'Consumable'), ('service', 'Service')], 'Type', default='product')
