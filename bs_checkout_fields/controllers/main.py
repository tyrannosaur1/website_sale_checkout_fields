# -*- coding: utf-8 -*-
"""The server-side half of the rule.

A hidden field is a rendering decision, but a required field is a contract: the
customer must not be able to place an order that the shop said it would refuse.
So the check lives in the controller that validates the checkout address, and
nowhere else: a contact written from the backend, an import, or the API is not
the website's checkout and is not concerned.

18.0 has no portal address manager -- `/my/account` is the account-details form,
with its own field list -- so the checkout form is the whole surface here.
"""
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCheckoutFields(WebsiteSale):

    def _validate_address_values(self, address_values, partner_sudo, address_type,
                                 use_delivery_as_billing, required_fields,
                                 is_main_address, **kwargs):
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, partner_sudo, address_type, use_delivery_as_billing,
            required_fields, is_main_address, **kwargs,
        )
        website = request.env["website"].get_current_website()
        for name in website._checkout_required_names():
            if address_values.get(name):
                continue
            missing_fields.add(name)
            error_messages.append(website._checkout_required_message(name))
        return invalid_fields, missing_fields, error_messages
