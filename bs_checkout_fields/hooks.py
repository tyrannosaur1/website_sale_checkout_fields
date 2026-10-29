# -*- coding: utf-8 -*-
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """Websites that existed before this module did have no rows yet."""
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["website"].search([])._checkout_ensure_fields()
