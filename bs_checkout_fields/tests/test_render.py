# -*- coding: utf-8 -*-
"""The rendered form: what a visitor actually receives.

The assertions are made on the HTML the server sent, because a rule applied in
JavaScript would pass a "does the field exist" check on the source and still
show the field to the customer.
"""
from .common import CheckoutFieldsCase


class TestCheckoutFieldsRender(CheckoutFieldsCase):

    def _label(self, tree, selector):
        nodes = tree.xpath(selector)
        self.assertEqual(len(nodes), 1, "the label was rendered %d times" % len(nodes))
        return nodes[0]

    def test_a_hidden_field_is_absent_from_the_form(self):
        self._cart()
        self._set_rule("street2", visibility="hidden")
        tree = self._tree()
        self.assertEqual(tree.xpath("//input[@name='street2']"), [])
        self.assertEqual(tree.xpath("//*[contains(@class, 'div_street2')]"), [])
        # The rest of the form is untouched: a neighbour is still rendered.
        self.assertEqual(len(tree.xpath("//input[@name='street']")), 1)

    def test_a_hidden_b2b_field_is_absent_from_the_form(self):
        self._cart()
        self._set_rule("company", visibility="hidden")
        tree = self._tree()
        self.assertEqual(tree.xpath("//input[@name='company_name']"), [])
        self.assertEqual(len(tree.xpath("//input[@name='phone']")), 1)

    def test_a_required_field_carries_the_marker(self):
        self._cart()
        self._set_rule("street2", required=True)
        tree = self._tree()
        inputs = tree.xpath("//input[@name='street2']")
        self.assertEqual(len(inputs), 1)
        self.assertEqual(inputs[0].get("required"), "required")
        label = self._label(tree, "//label[@for='street2']")
        self.assertNotIn(
            "label-optional", (label.get("class") or "").split(),
            "a required field still says it is optional",
        )

    def test_a_required_phone_is_rendered_required(self):
        self._cart()
        self._set_rule("phone", required=True)
        tree = self._tree()
        self.assertEqual(
            tree.xpath("//input[@name='phone']")[0].get("required"), "required")

    def test_a_required_zip_is_rendered_required(self):
        self._cart()
        self._set_rule("zip", required=True)
        tree = self._tree()
        inputs = tree.xpath("//input[@name='zip']")
        self.assertEqual(len(inputs), 1, "the zip block was rendered %d times" % len(inputs))
        self.assertEqual(inputs[0].get("required"), "required")

    def test_a_website_with_no_rule_renders_the_shop_form(self):
        self._cart()
        tree = self._tree()
        inputs = tree.xpath("//input[@name='street2']")
        self.assertEqual(len(inputs), 1)
        self.assertIsNone(inputs[0].get("required"))
        label = self._label(tree, "//label[@for='street2']")
        self.assertIn("label-optional", (label.get("class") or "").split())
        self.assertEqual(label.text_content().strip(), "Street 2")

    def test_the_merchant_wording_replaces_the_shop_wording(self):
        self._cart()
        self._set_rule("phone", label="Mobile number")
        tree = self._tree()
        label = self._label(tree, "//label[@for='phone']")
        self.assertEqual(label.text_content().strip(), "Mobile number")

    def test_the_shop_wording_is_kept_when_no_wording_was_given(self):
        self._cart()
        tree = self._tree()
        self.assertEqual(
            self._label(tree, "//label[@for='phone']").text_content().strip(),
            "Phone")
