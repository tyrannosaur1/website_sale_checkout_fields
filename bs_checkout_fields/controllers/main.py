# -*- coding: utf-8 -*-
"""The server-side half of the rule.

A hidden field is a rendering decision, but a required field is a contract: the
customer must not be able to place an order that the shop said it would refuse.
So the check lives in the controller that validates the checkout address --
``/shop/address/submit`` and the portal's own address form, which is the same
controller and therefore the same rule. Nothing here touches ``res.partner``: a
contact written from the backend, an import, or the API is not the website's
checkout and is not concerned.
"""
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCheckoutFields(WebsiteSale):

    def _validate_address_values(self, address_values, partner_sudo, address_type,
                                 use_delivery_as_billing, required_fields, **kwargs):
        invalid_fields, missing_fields, error_messages = super()._validate_address_values(
            address_values, partner_sudo, address_type, use_delivery_as_billing,
            required_fields, **kwargs,
        )
        website = request.env["website"].get_current_website()
        for name in website._checkout_required_names():
            if address_values.get(name):
                continue
            missing_fields.add(name)
            error_messages.append(website._checkout_required_message(name))
        return invalid_fields, missing_fields, error_messages
