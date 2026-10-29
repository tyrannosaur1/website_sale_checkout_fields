# Checkout Address Fields

The checkout asks everyone the same six questions. Decide per website which ones your shop actually needs, and hold the checkout to your answer.

Odoo 10.0 – 20.0. One branch per series, the branch name is the series.

## What it does

- Eight address fields per website — street, street 2, city, zip, country, phone, company, VAT — each one shown or hidden, some of them optional or mandatory, any of them reworded.
- A hidden field is not rendered: it is out of the HTML, on the billing form and on the shipping form alike, not merely invisible.
- Hiding does not clear anything. An address that already carries a second line or a VAT number keeps it; the customer stops being asked and the value stops being validated.
- A field the shop cannot do without — street, country — cannot be hidden. The attempt is refused with a sentence that says why, at the moment the setting is saved, instead of at the first order that cannot be shipped.
- The requirement is kept by the server. An address posted without a field the website made mandatory is refused with a sentence that names the field, whether it came from the browser or from a hand-made request.
- The wording is the arch's own text unless you replace it, so the shop's
  translations keep working; Company and VAT keep the shop's own wording
  ("TIN / VAT") until you give them one.

## Install

1. Copy the module into your addons path.
2. Update the app list, install **Checkout Address Fields**.
3. Website › Configuration › Websites › open your site › **Checkout Fields**: hide, require or reword the fields of this website.

The eight rows are created for every website when the module is installed, and for every website created afterwards. There is nothing to add and nothing to delete.

## Notes

- The set of rows is fixed on purpose. "The field this merchant hid" has to be a fact a template can read by name, not a row that may or may not have been created.
- Street and Country are listed but locked: the address is unusable without them, and the shop's own checks read them for every country.
- City is not hideable either, and Zip is not hideable although it can be made mandatory: the shop's address-completeness checks read both for the countries that require them, so hiding one would send the customer back to the form after every submit.
- Company and VAT cannot be made mandatory: they are part of the optional B2B block, and a delivery address never shows them, so the requirement could not be honoured on the page that renders the form.
- Before 16.0 the website's settings are still edited on the website record itself, under Website › Configuration › Websites, which is where the block lives on this branch.
- Before 19.0 the customer portal has no address form of its own (its `/my/account` page is the account-details form, with a different field list), so the rule covers the shop's checkout only; the portal half applies from 19.0 on, where `/my/address` exists.
- Nothing is validated on `res.partner` itself: a contact written in the backend, imported, or created through the API is not the website's checkout.

## License

OPL-1. See `LICENSE`.

## Support

Open an issue on this repository.
