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
        # 11.0 has no `cls.env` in setUpClass, so the fixture lives here.
        self.website = self.env["website"].search([], limit=1)
        self.product = self._product()
        self.country = self.env.ref("base.uk")
        # Every test starts from a shop that configured nothing.
        self.website.checkout_field_ids.write({
            "visibility": "visible", "required": False, "label": False,
        })
        # The requests of this series run in a transaction of their own: what
        # the page is supposed to see has to be committed, not just created.
        self.env.cr.commit()

    def _product(self):
        """The fixture is committed, so a later test reuses what it finds."""
        values = {
            "name": "Checkout Widget",
            "type": "consu",
            "sale_ok": True,
            "list_price": 10.0,
            "website_published": True,
        }
        product = self.env["product.template"].search(
            [("name", "=", values["name"])], limit=1)
        if product:
            product.write(values)
            return product
        return self.env["product.template"].create(values)

    def _pricelist(self):
        """11.0 wants a pricelist on the order and has no website to take it
        from, so the first one of the database is used (or one is made)."""
        pricelist = self.env["product.pricelist"].search([], limit=1)
        if pricelist:
            return pricelist
        return self.env["product.pricelist"].create({
            "name": "Checkout Fields",
            "currency_id": self.env.user.company_id.currency_id.id,
        })

    # -- configuration -------------------------------------------------
    def _rule(self, name):
        return self.website.checkout_field_ids.filtered(
            lambda rule: rule.field_name == name)

    def _set_rule(self, name, **values):
        self._rule(name).write(values)
        # the request reads the rule through another cursor
        self.env.cr.commit()

    # -- the visitor ---------------------------------------------------
    def _cart(self):
        """An anonymous cart with one physical product in it."""
        order = self.env["sale.order"].create({
            "partner_id": self.website.user_id.partner_id.id,
            "pricelist_id": self._pricelist().id,
            "order_line": [(0, 0, {
                "product_id": self.product.product_variant_id.id,
                "product_uom_qty": 1,
            })],
        })
        self.env.cr.commit()
        # The session this setUp builds is anonymous already; 11.0 has no
        # browser to sign out of, and nothing here signs a customer in.
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
