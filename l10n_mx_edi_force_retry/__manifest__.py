# Copyright 2026 Globalbtek
# License OPL-1 (Odoo Proprietary License v1.0)

{
    "name": "MX EDI - Forzar reintento de decimales",
    "summary": "Detección automática y reintento para CRP20268 y CRPER654 en complementos de pago",
    "version": "19.0.1.0.1",
    "author": "Globalbtek",
    "license": "OPL-1",
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