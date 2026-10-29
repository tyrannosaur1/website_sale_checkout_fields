# -*- coding: utf-8 -*-
"""A required field is a promise the server keeps, not an asterisk.

Each refusal is paired with the same submission carrying the field: the pair is
what proves the refusal came from this website's rule and not from the shop
having decided the same thing on its own.
"""
from .common import CheckoutFieldsCase


class TestCheckoutFieldsValidation(CheckoutFieldsCase):

    def test_a_checkout_address_without_the_required_phone_is_refused(self):
        self._cart()
        self._set_rule("phone", required=True)
        response = self._submit(self._address_form(phone=""))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("phone", payload.get("invalid_fields", []))
        self.assertIn(
            "Phone is required by this website's checkout settings.",
            " ".join(payload.get("messages", [])),
        )

    def test_the_same_address_with_the_phone_is_accepted(self):
        """The positive control for the refusal above."""
        self._cart()
        self._set_rule("phone", required=True)
        payload = self._submit(self._address_form(phone="+44 20 7000 0000")).json()
        self.assertNotIn("invalid_fields", payload)
        self.assertTrue(payload.get("redirectUrl"), "the address was not saved")

    def test_a_checkout_address_without_the_required_second_line_is_refused(self):
        """Street 2 is the field the shop would otherwise never ask for, so a
        refusal here cannot be the shop's own rule in disguise."""
        self._cart()
        self._set_rule("street2", required=True)
        payload = self._submit(self._address_form(street2="")).json()
        self.assertIn("street2", payload.get("invalid_fields", []))
        self.assertIn(
            "Street 2 is required by this website's checkout settings.",
            " ".join(payload.get("messages", [])),
        )

    def test_the_same_address_with_the_second_line_is_accepted(self):
        self._cart()
        self._set_rule("street2", required=True)
        payload = self._submit(self._address_form(street2="Suite 3")).json()
        self.assertNotIn("invalid_fields", payload)
        self.assertTrue(payload.get("redirectUrl"))

    def test_a_hidden_field_is_not_required_by_the_shop(self):
        """Hiding Street 2 must not leave the form refusing its own emptiness."""
        self._cart()
        self._set_rule("street2", visibility="hidden")
        payload = self._submit(self._address_form(street2="")).json()
        self.assertNotIn("invalid_fields", payload)
        self.assertTrue(payload.get("redirectUrl"))
