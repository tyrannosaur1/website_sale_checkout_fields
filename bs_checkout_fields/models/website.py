# -*- coding: utf-8 -*-
"""What the address forms read from the website.

The helpers below are called from QWeb, once per field, and they answer from
the one2many the settings block edits. The one2many is prefetched, so asking
eight times costs one query, not eight.
"""
from odoo import api, fields, models

from .checkout_field import FIELD_LABELS, FIELD_NAMES, translate


class Website(models.Model):
    _inherit = "website"

    checkout_field_ids = fields.One2many(
        "website.checkout.field", "website_id", string="Checkout Address Fields")

    @api.model_create_multi
    def create(self, vals_list):
        websites = super().create(vals_list)
        websites._checkout_ensure_fields()
        return websites

    def _checkout_ensure_fields(self):
        """Give every website the full set of rows, once."""
        Rule = self.env["website.checkout.field"]
        for website in self:
            present = set(website.checkout_field_ids.mapped("field_name"))
            for sequence, name in enumerate(FIELD_NAMES, start=1):
                if name in present:
                    continue
                Rule.create({
                    "website_id": website.id,
                    "field_name": name,
                    "sequence": sequence * 10,
                })

    def _checkout_field_rule(self, name):
        """The row for one field; an empty recordset when the site has none."""
        self.ensure_one()
        return self.checkout_field_ids.filtered(
            lambda rule: rule.field_name == name)[:1]

    def _checkout_field_hidden(self, name):
        rule = self._checkout_field_rule(name)
        return bool(rule) and rule.visibility == "hidden"

    def _checkout_field_required(self, name):
        rule = self._checkout_field_rule(name)
        return bool(rule) and rule.required and rule.visibility != "hidden"

    def _checkout_field_label(self, name):
        """The merchant's wording for the field, or an empty string."""
        rule = self._checkout_field_rule(name)
        return (rule.label or "") if rule else ""

    def _checkout_required_names(self):
        """The fields this website asks for, as ``res.partner`` field names."""
        self.ensure_one()
        return [
            rule.field_name
            for rule in self.checkout_field_ids
            if rule.required and rule.visibility != "hidden"
        ]

    def _checkout_required_message(self, name):
        """The sentence a customer reads when a required field is missing."""
        self.ensure_one()
        rule = self._checkout_field_rule(name)
        label = (rule.label or FIELD_LABELS.get(name, name)) if rule else name
        return translate(
            self.env,
            "%(field)s is required by this website's checkout settings.",
        ) % {"field": label}
