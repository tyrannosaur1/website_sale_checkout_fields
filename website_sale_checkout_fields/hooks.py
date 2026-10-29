# -*- coding: utf-8 -*-
import logging

from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def post_init_hook(env):
    """Websites that existed before this module did have no rows yet."""
    env["website"].search([])._checkout_ensure_fields()
