# -*- coding: utf-8 -*-
"""What a merchant may configure, and what the shop refuses to let them do.

Every refusal here is about an address that would still have to be delivered:
hiding the country or the street is not a matter of taste, it is an order the
shop could not ship. Everything a merchant *can* do is tested next to the
refusal so the refusal cannot be satisfied by refusing everything.
"""
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestCheckoutFieldConfig(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].search([], limit=1)

    def _rule(self, name):
        return self.website.checkout_field_ids.filtered(
            lambda rule: rule.field_name == name)

    def test_a_website_has_the_whole_set_of_fields_once(self):
        """The block is a fixed set, not a list the merchant builds."""
        names = self.website.checkout_field_ids.mapped("field_name")
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(
            set(names),
            {"street", "street2", "city", "zip", "country", "phone", "company", "vat"})

    def test_a_new_website_gets_its_own_rows(self):
        other = self.env["website"].create({"name": "Second Shop"})
        self.assertEqual(len(other.checkout_field_ids), 8)
        self.assertFalse(any(other.checkout_field_ids.mapped("required")))

    def test_hiding_the_country_is_refused(self):
        with self.assertRaises(ValidationError):
            self._rule("country").write({"visibility": "hidden"})

    def test_hiding_the_street_is_refused(self):
        with self.assertRaises(ValidationError):
            self._rule("street").write({"visibility": "hidden"})

    def test_hiding_the_second_street_line_is_accepted(self):
        self._rule("street2").write({"visibility": "hidden"})
        self.assertTrue(self.website._checkout_field_hidden("street2"))
        self.assertFalse(self.website._checkout_field_required("street2"))

    def test_making_the_phone_required_is_accepted(self):
        self._rule("phone").write({"required": True})
        self.assertTrue(self.website._checkout_field_required("phone"))
        self.assertIn("phone", self.website._checkout_required_names())

    def test_a_hidden_field_cannot_be_required(self):
        with self.assertRaises(ValidationError):
            self._rule("street2").write({"visibility": "hidden", "required": True})

    def test_a_field_the_shop_only_shows_on_billing_cannot_be_required(self):
        """Company and VAT live in the optional B2B block of a billing address."""
        with self.assertRaises(ValidationError):
            self._rule("company").write({"required": True})
        with self.assertRaises(ValidationError):
            self._rule("vat").write({"required": True})

    def test_the_merchant_wording_is_kept(self):
        self._rule("phone").write({"label": "Mobile number"})
        self.assertEqual(self.website._checkout_field_label("phone"), "Mobile number")
