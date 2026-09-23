# Copyright 2026 Globalbtek
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.html).

{
    "name": "MX EDI - Forzar reintento de decimales",
    "summary": "Detección automática y reintento para CRP20268 y CRPER654 en complementos de pago",
    "version": "19.0.1.0.0",
    "author": "Globalbtek",
    "license": "LGPL-3",
    "depends": [
        "account_edi",
        "l10n_mx_edi",
    ],
    "data": [
        "data/payment20_force_retry.xml",
        "data/install_force_retry_view.xml",
    ],
    "installable": True,
    "application": False,
}