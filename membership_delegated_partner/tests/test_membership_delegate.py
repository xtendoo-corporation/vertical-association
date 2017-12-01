# -*- coding: utf-8 -*-
# Copyright 2017 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestMembershipDelegate(common.SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestMembershipDelegate, cls).setUpClass()
        cls.partner1 = cls.env['res.partner'].create({
            'name': 'Mr. Odoo',
        })
        cls.partner2 = cls.env['res.partner'].create({
            'name': 'Mrs. Odoo',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Test membership product',
            'membership': True,
        })
        cls.account_type = cls.env['account.account.type'].create({
            'name': 'Test',
            'type': 'receivable',
        })
        cls.account = cls.env['account.account'].create({
            'name': 'Test account',
            'code': 'TEST',
            'user_type_id': cls.account_type.id,
            'reconcile': True,
        })

    def test_01_delegate(self):
        """ Delegates membership to partner 2 """
        invoice = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'account_id': self.account.id,
            'partner_id': self.partner1.id,  # Invoicing partner
            'delegated_member_id': self.partner2.id,  # Delegate membership to
            'invoice_line_ids': [(0, 0, {
                'name': 'Membership for delegate member',
                'account_id': self.account.id,
                'product_id': self.product.id,
                'price_unit': 1.0,
            })],
        })
        self.assertTrue(self.partner2.member_lines,
                        'Delegated partner gets the line')
        self.assertFalse(self.partner1.member_lines,
                         'Invoicing partner gets no line')
        # We try to force reassign member line to another partner
        self.partner2.member_lines.partner = ({'partner': self.partner1.id})
        self.assertFalse(self.partner1.member_lines,
                         "It's going to stand on partner2")
        # Same test, with account_invoice_line in the write
        self.partner2.member_lines.write({
            'partner': self.partner1.id,
            'account_invoice_line': invoice.invoice_line_ids[0].id,
        })
        self.assertFalse(self.partner1.member_lines,
                         "It's going to stand on partner2")

    def test_02_change_delegated_member(self):
        """ Delegated member can be changed later """
        invoice = self.env['account.invoice'].create({
            'name': "Test Customer Invoice",
            'journal_id': self.env['account.journal'].search(
                [('type', '=', 'sale')])[0].id,
            'account_id': self.account.id,
            'partner_id': self.partner1.id,  # Invoicing partner
            'invoice_line_ids': [(0, 0, {
                'name': 'Membership classic',
                'account_id': self.account.id,
                'product_id': self.product.id,
                'price_unit': 1.0,
            })],
        })
        self.assertTrue(self.partner1.member_lines, 'Partner gets the line')
        invoice.delegated_member_id = self.partner2
        self.assertTrue(self.partner2.member_lines, 'Delegate gets the line')
        self.assertFalse(self.partner1.member_lines, 'Partner drops the line')
