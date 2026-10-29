# -*- coding: utf-8 -*-
"""One row per address field, per website.

The row set is fixed. ``Website._checkout_ensure_fields`` gives every website
its eight rows when the website is created, and the settings block edits those
rows instead of adding new ones. A fixed set is what makes "the field this
merchant hid" a stable fact: a template can ask the website about one field by
name without having to cope with the row being absent.

What a row may do is a property of the *field*, not of the merchant's taste,
and it is spelled out here rather than left to the interface:

* a field the shop cannot build a deliverable address without (street, country)
  cannot be hidden -- the shop would take the order and then have nowhere to
  send it;
* a field the shop already always asks for (city) or cannot show on every page
  (company, vat: they are part of the optional B2B block, and a delivery
  address never shows them) cannot be made required, because the requirement
  could not be honoured on the page that renders the form.
"""
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

#: The configurable fields, in the order the checkout shows them.
FIELDS = [
    ("street", "Street"),
    ("street2", "Street 2"),
    ("city", "City"),
    ("zip", "Zip"),
    ("country", "Country"),
    ("phone", "Phone"),
    ("company", "Company"),
    ("vat", "VAT"),
]
FIELD_NAMES = [name for name, _label in FIELDS]
FIELD_LABELS = dict(FIELDS)

#: Fields a merchant may hide. Street and country are missing on purpose: the
#: address is unusable without them. City and zip are missing because the shop's
#: own address checks read them for the countries that require them, and hiding
#: one would send the customer back to the form after every submit. Phone is
#: missing too: the shop requires it on a shipping address from 17.0 on, and the
#: list is kept the same on every series so a site that moves between them keeps
#: the rules it had.
HIDEABLE = {"street2", "company", "vat"}

#: Fields a merchant may make required. City, country and street are always
#: required by the shop already; company and vat are only rendered inside the
#: optional B2B block, so a requirement on them could not be honoured.
#:
#: Street 2 is missing here on purpose: the 10.0 address form has no second
#: address line at all (neither a label nor an input), so a requirement on it
#: could not be satisfied from the page. Hiding it is still accepted -- it is
#: already absent -- so the configuration of a site stays valid when it moves
#: to a newer series.
REQUIRABLE = {"phone", "zip"}


def translate(env, text):
    """Translate *text* with the module-level translator of this series."""
    return _(text)


class WebsiteCheckoutField(models.Model):
    _name = "website.checkout.field"
    _description = "Checkout Address Field"
    _order = "sequence, id"

    website_id = fields.Many2one(
        "website", string="Website", required=True, ondelete="cascade", index=True)
    field_name = fields.Selection(FIELDS, string="Field", required=True)
    sequence = fields.Integer(default=10)
    visibility = fields.Selection(
        [("visible", "Shown"), ("hidden", "Hidden")],
        string="On the form", required=True, default="visible",
        help="A hidden field is not rendered and its value is left untouched on "
             "addresses that already carry one.",
    )
    required = fields.Boolean(
        help="Ask for this field on every checkout address, even on the shipping "
             "form where the shop would otherwise leave it empty.",
    )
    label = fields.Char(
        translate=True,
        help="Leave empty to keep the shop's own wording for this field.",
    )

    can_be_hidden = fields.Boolean(compute="_compute_capabilities")
    can_be_required = fields.Boolean(compute="_compute_capabilities")
    stock_label = fields.Char(compute="_compute_capabilities")

    @api.depends("field_name")
    def _compute_capabilities(self):
        for rule in self:
            name = rule.field_name
            rule.stock_label = FIELD_LABELS.get(name, name or "")
            rule.can_be_hidden = name in HIDEABLE
            rule.can_be_required = name in REQUIRABLE

    @api.constrains("field_name", "visibility")
    def _check_can_be_hidden(self):
        for rule in self:
            if rule.visibility != "hidden" or rule.can_be_hidden:
                continue
            raise ValidationError(translate(
                rule.env,
                "The %(field)s field cannot be hidden: the shop needs it to "
                "build an address it can deliver to or invoice.",
            ) % {"field": rule.stock_label or rule.field_name})

    @api.constrains("field_name", "required")
    def _check_can_be_required(self):
        for rule in self:
            if not rule.required or rule.can_be_required:
                continue
            raise ValidationError(translate(
                rule.env,
                "The %(field)s field cannot be made required here: the shop "
                "either always asks for it already, or does not show it on "
                "every address form.",
            ) % {"field": rule.stock_label or rule.field_name})

    @api.constrains("visibility", "required")
    def _check_hidden_is_not_required(self):
        for rule in self:
            if rule.visibility == "hidden" and rule.required:
                raise ValidationError(translate(
                    rule.env,
                    "The %(field)s field cannot be both hidden and required.",
                ) % {"field": rule.stock_label or rule.field_name})
