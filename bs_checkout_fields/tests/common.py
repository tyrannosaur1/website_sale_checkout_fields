# -*- coding: utf-8 -*-
"""The fixture every HTTP test here shares: a visitor with a real cart.

The address form is only rendered for a cart that needs an address, so the
tests build one and put its id in the session the way the shop does, instead
of posting to the cart route and hoping the redirect landed.

The form is a plain POST in this series: a refused address re-renders the page
with the errors in it, and an accepted one answers with a redirect.
"""
import re

from lxml import html as lxml_html

from odoo.http import root
from odoo.tests.common import HttpCase

CSRF_RE = re.compile(r'name="csrf_token"[^>]*value="([^"]+)"')


class CheckoutFieldsCase(HttpCase):

    def setUp(self):
        super(CheckoutFieldsCase, self).setUp()
        # 12.0 has no `cls.env` in setUpClass, so the fixture lives here.
        self.website = self.env["website"].search([], limit=1)
        self.product = self.env["product.template"].create({
            "name": "Checkout Widget",
            "type": "consu",
            "sale_ok": True,
            "list_price": 10.0,
            "website_published": True,
        })
        self.country = self.env.ref("base.uk")
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
        # 12.0's `authenticate(None, None)` reaches for a browser that the
        # test has not started; the session this setUp builds is anonymous
        # already, so there is nothing to sign out of.
        self.session['sale_order_id'] = order.id
        root.session_store.save(self.session)
        return order

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
        """The fields the plain-post form of this series sends."""
        data = {
            "csrf_token": self._csrf(url),
            "submitted": "1",
            "partner_id": "0",
            "callback": "",
            "field_required": "phone,name",
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

    def _submit(self, data, url="/shop/address"):
        """Post the form. Up to 15.0 the answer is the page, not JSON.

        ``url_open`` has no ``allow_redirects`` before 14.0, and the opener it
        wraps keeps the session cookie, so the post goes through the opener.
        """
        base = self.xmlrpc_url.split("/xmlrpc/2/")[0]
        return self.opener.post(base + url, data=data, allow_redirects=False)
