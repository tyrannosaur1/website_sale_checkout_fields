# -*- coding: utf-8 -*-
"""A required field is a promise the server keeps, not an asterisk.

Each refusal is paired with the same submission carrying the field: the pair is
what proves the refusal came from this website's rule and not from the shop
having decided the same thing on its own.
"""
from lxml import html as lxml_html

from .common import CheckoutFieldsCase


class TestCheckoutFieldsValidation(CheckoutFieldsCase):

    def _messages(self, response):
        tree = lxml_html.fromstring(response.text)
        return " ".join(
            node.text_content() for node in tree.xpath("//*[@class='text-danger']"))

    def _wrapper(self, response, name):
        tree = lxml_html.fromstring(response.text)
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

    def test_a_checkout_address_without_the_required_second_line_is_refused(self):
        """Street 2 is the field the shop would otherwise never ask for, so a
        refusal here cannot be the shop's own rule in disguise."""
        self._cart()
        self._set_rule("street2", required=True)
        response = self._submit(self._address_form(street2=""))
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            "Street 2 is required by this website's checkout settings.",
            self._messages(response))
        wrapper = self._wrapper(response, "street2")
        self.assertIn("has-error", (wrapper.get("class") or "").split())

    def test_the_same_address_with_the_second_line_is_accepted(self):
        self._cart()
        self._set_rule("street2", required=True)
        response = self._submit(self._address_form(street2="Suite 3"))
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/shop/", response.headers.get("Location", ""))

    def test_a_hidden_field_is_not_required_by_the_shop(self):
        """Hiding Street 2 must not leave the form refusing its own emptiness."""
        self._cart()
        self._set_rule("street2", visibility="hidden")
        response = self._submit(self._address_form(street2=""))
        self.assertIn(response.status_code, (302, 303))
        self.assertIn("/shop/", response.headers.get("Location", ""))
