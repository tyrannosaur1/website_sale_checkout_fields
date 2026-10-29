# -*- coding: utf-8 -*-
"""The fixture every HTTP test here shares: a visitor with a real cart.

The address form is only rendered for a cart that needs an address, so the
tests build one and put its id in the session the way the shop does, instead
of posting to the cart route and hoping the redirect landed.
"""
import re

from lxml import html as lxml_html

from odoo.http import root
from odoo.tests.common import HttpCase

CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


class CheckoutFieldsCase(HttpCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.website = cls.env["website"].search([], limit=1)
        cls.product = cls.env["product.template"].create({
            "name": "Checkout Widget",
            "type": "consu",
            "sale_ok": True,
            "list_price": 10.0,
            "website_published": True,
        })
        cls.country = cls.env.ref("base.uk")

    def setUp(self):
        super().setUp()
        # Every test starts from a shop that configured nothing.
        self.website.checkout_field_ids.write({
            "visibility": "visible", "required": False, "label": False,
        })

    # -- configuration -------------------------------------------------
    def _rule(self, name):
        return self.website.checkout_field_ids.filtered(
            lambda rule: rule.field_name == name)

    def _set_rule(self, name, **values):
        self._rule(name).write(values)

    # -- the visitor ---------------------------------------------------
    def _cart(self):
        """An anonymous cart with one physical product in it."""
        order = self.env["sale.order"].create({
            "partner_id": self.website.user_id.partner_id.id,
            "website_id": self.website.id,
            "order_line": [(0, 0, {
                "product_id": self.product.product_variant_id.id,
                "product_uom_qty": 1,
            })],
        })
        self.authenticate(None, None)
        self.session['sale_order_id'] = order.id
        root.session_store.save(self.session)
        return order

    def _portal_user(self, login="checkout.fields@example.com", password="cf_pw_2024"):
        user = self.env["res.users"].create({
            "name": "Portal Shopper",
            "login": login,
            "password": password,
            "email": login,
            "group_ids": [(6, 0, [self.env.ref("base.group_portal").id])],
        })
        self.authenticate(login, password)
        return user

    # -- pages and posts ----------------------------------------------
    def _page(self, url="/shop/address"):
        response = self.url_open(url)
        self.assertEqual(response.status_code, 200, "the page did not render")
        return response

    def _tree(self, url="/shop/address"):
        return lxml_html.fromstring(self._page(url).text)

    def _csrf(self, url="/shop/address"):
        match = CSRF_RE.search(self._page(url).text)
        self.assertTrue(match, "the address form carries no csrf token")
        return match.group(1)

    def _address_form(self, url="/shop/address", **overrides):
        data = {
            "csrf_token": self._csrf(url),
            "address_type": "billing",
            "use_delivery_as_billing": "false",
            "name": "Ada Lovelace",
            "email": "ada@example.com",
            "street": "1 Analytical Way",
            "street2": "Suite 3",
            "city": "London",
            "zip": "N1 1AA",
            "country_id": str(self.country.id),
            "phone": "+44 20 7000 0000",
        }
        data.update(overrides)
        return data

    def _submit(self, data, url="/shop/address/submit"):
        return self.url_open(url, data=data)
