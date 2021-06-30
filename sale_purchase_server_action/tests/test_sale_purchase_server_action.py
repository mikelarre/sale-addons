# Copyright 2021 Mikel Arregi - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests import common
from odoo.exceptions import UserError


@common.at_install(False)
@common.post_install(True)
class TestNoDefaultPriceUnit(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestNoDefaultPriceUnit, cls).setUpClass()
        cls.product_model = cls.env['product.product']
        cls.partner_model = cls.env['res.partner']
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')
        SaleOrder = cls.env['sale.order'].with_context(tracking_disable=True)
        cls.partner = cls.partner_model.create({
            'name': 'Partner1',
        })
        cls.supplier = cls.partner_model.create({
            'name': 'Supplier1',
        })
        cls.product = cls.product_model.create({
            'name': 'Product',
            'type': 'product',
            'default_code': 'P1',
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
            'seller_ids': [(0, 0, {
                'name': cls.supplier.id,
            })]
        })
        cls.sale_order = SaleOrder.create({
            'partner_id': cls.partner.id,
            'partner_invoice_id': cls.partner.id,
            'partner_shipping_id': cls.partner.id})

    def test_default_price_unit(self):
        line_vals = {
            'product_id': self.product.id,
            'name': self.product.name,
            'product_uom_qty': 1,
            'product_uom': self.product.uom_id.id,
            'order_id': self.sale_order.id
            }
        lines = self.env['sale.order.line']
        lines_obj = self.env['sale.order.line']
        for i in range(2):
            lines |= lines_obj.create(line_vals)
        lines.create_purchase_lines()
        purchase = self.env['purchase.order'].search([])[-1]
        self.assertEqual(len(purchase.order_line), len(lines))
        self.assertEqual(purchase.order_line[0].product_id,
                         lines[0].product_id)
