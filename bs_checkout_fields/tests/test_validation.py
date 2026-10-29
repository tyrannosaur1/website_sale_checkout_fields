# -*- coding: utf-8 -*-
"""A required field is a promise the server keeps, not an asterisk.

Each refusal is paired with the same submission carrying the field: the pair is
what proves the refusal came from this website's rule and not from the shop
having decided the same thing on its own.
"""
from lxml import html as lxml_html

from odoo.tests.common import at_install, post_install

from .common import CheckoutFieldsCase


@at_install(False)
@post_install(True)
class TestCheckoutFieldsValidation(CheckoutFieldsCase):

    def _messages(self, response):
        tree = lxml_html.fromstring(response.body)
        return " ".join(
            node.text_content() for node in tree.xpath("//*[@class='text-danger']"))

    def _wrapper(self, response, name):
        tree = lxml_html.fromstring(response.body)
        nodes = tree.xpath("//input[@name='%s']/.." % name)
        self.assertEqual(len(nodes), 1, "the field was rendered %d times" % len(nodes))
        return nodes[0]

    def test_a_checkout_address_without_the_required_phone_is_refused(self):
        self._cart()
        self._set_rule("phone", required=True)
        response = self._submit(self._address_form(phone=""))
        self.assertEqual(response.status_code, 200, "the refusal must be a page")
        self.assertIn(
            "Phone is required by this website's checkout settings.",
            self._messages(response))
        wrapper = self._wrapper(response, "phone")
        self.assertIn("has-error", (wrapper.get("class") or "").split())

    def test_the_same_address_with_the_phone_is_accepted(self):
        """The positive control for the refusal above."""
        self._cart()
        self._set_rule("phone", required=True)
        response = self._submit(self._address_form(phone="+44 20 7000 0000"))
        self.assertIn(response.status_code, (302, 303), "the address was not saved")
        self.assertIn("/shop/", response.headers.get("Location", ""))

    def test_a_checkout_address_without_the_required_zip_is_refused(self):
        """Zip is optional for the country of the fixture, so a refusal here
        cannot be the shop's own rule in disguise."""
        self._cart()
        self._set_rule("zip", required=True)
        response = self._submit(self._address_form(zip=""))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Zip is required by this website's checkout settings.",
            self._messages(response))
        wrapper = self._wrapper(response, "zip")
        self.assertIn("has-error", (wrapper.get("class") or "").split())

    def test_the_same_address_with_the_zip_is_accepted(self):
        self._cart()
        self._set_rule("zip", required=True)
        response = self._submit(self._address_form(zip="N1 1AA"))
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/shop/", response.headers.get("Location", ""))

    def test_a_hidden_field_is_not_required_by_the_shop(self):
        """Hiding a field must not leave the form refusing its own emptiness."""
        self._cart()
        self._set_rule("company", visibility="hidden")
        response = self._submit(self._address_form(company_name=""))
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/shop/", response.headers.get("Location", ""))
