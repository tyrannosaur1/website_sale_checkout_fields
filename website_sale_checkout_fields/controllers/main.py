# -*- coding: utf-8 -*-
"""The server-side half of the rule.

A hidden field is a rendering decision, but a required field is a contract: the
customer must not be able to place an order that the shop said it would refuse.
In 17.0 the address form is a plain POST that re-renders the page with the
errors, and every one of those errors is decided in `checkout_form_validate`,
so the website's own requirements are added there -- next to the shop's, not
instead of them.

Nothing here touches `res.partner`: a contact written from the backend, an
import, or the API is not the website's checkout and is not concerned.
"""
from odoo.http import request

from odoo.addons.website_sale.controllers.main import WebsiteSale


class WebsiteSaleCheckoutFields(WebsiteSale):

    def checkout_form_validate(self, mode, all_form_values, data):
        error, error_message = super().checkout_form_validate(
            mode, all_form_values, data)
        website = request.env["website"].get_current_website()
        for name in website._checkout_required_names():
            value = data.get(name)
            if isinstance(value, str):
                value = value.strip()
            if value:
                continue
            error[name] = "missing"
            error_message.append(website._checkout_required_message(name))
        return error, error_message
