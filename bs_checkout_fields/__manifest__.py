# -*- coding: utf-8 -*-
{
    "name": "Checkout Address Fields",
    "version": "20.0.1.0.0",
    "summary": "Show, hide, require and rename the address fields of the shop's "
               "checkout: a shorter form for the fields you do not need, and a "
               "server-side check for the ones you do.",
    "author": "ModForge",
    "images": ["static/description/cover.png"],
    "license": "OPL-1",
    "category": "Website/Website",
    "depends": ["website_sale"],
    "data": [
        "security/ir.access.csv",
        "views/website_views.xml",
        "views/templates.xml",
    ],
    "post_init_hook": "post_init_hook",
    "installable": True,
    "application": False,
    "price": 29.0,
    "currency": "USD",
}
