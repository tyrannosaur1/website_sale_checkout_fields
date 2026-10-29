# -*- coding: utf-8 -*-
"""A required field is a promise the server keeps, not an asterisk.

Each refusal is paired with the same submission carrying the field: the pair is
what proves the refusal came from this website's rule and not from the shop
having decided the same thing on its own.

Up to 17.0 the form is a plain POST to `/shop/address`: a refusal re-renders
the page with the errors in it, and a success is a redirect into the rest of
the checkout.
"""
from .common import CheckoutFieldsCase


class TestCheckoutFieldsValidation(CheckoutFieldsCase):

    def _refused(self, response):
        self.assertEqual(response.status_code, 200, "the shop did not re-render the form")
        return response.text

    def _accepted(self, response):
        self.assertEqual(
            response.status_code, 303,
            "the form was not accepted (status %s)" % response.status_code)
        self.assertIn("/shop/", response.headers.get("Location", ""))

    def test_a_checkout_address_without_the_required_phone_is_refused(self):
        self._cart()
        self._set_rule("phone", required=True)
        page = self._refused(self._submit(self._address_form(phone="")))
        self.assertIn(
            "Phone is required by this website", page)

    def test_the_same_address_with_the_phone_is_accepted(self):
        """The positive control for the refusal above."""
        self._cart()
        self._set_rule("phone", required=True)
        self._accepted(self._submit(self._address_form(phone="+44 20 7000 0000")))

    def test_a_checkout_address_without_the_required_second_line_is_refused(self):
        """Street 2 is the field the shop would otherwise never ask for, so a
        refusal here cannot be the shop's own rule in disguise."""
        self._cart()
        self._set_rule("street2", required=True)
        page = self._refused(self._submit(self._address_form(street2="")))
        self.assertIn(
            "Street 2 is required by this website", page)

    def test_the_same_address_with_the_second_line_is_accepted(self):
        self._cart()
        self._set_rule("street2", required=True)
        self._accepted(self._submit(self._address_form(street2="Suite 3")))

    def test_a_hidden_field_is_not_required_by_the_shop(self):
        """Hiding Street 2 must not leave the form refusing its own emptiness."""
        self._cart()
        self._set_rule("street2", visibility="hidden")
        self._accepted(self._submit(self._address_form(street2="")))
