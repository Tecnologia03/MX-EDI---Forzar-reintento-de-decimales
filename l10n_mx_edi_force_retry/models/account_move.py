# -*- coding: utf-8 -*-
from odoo import _, models
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = "account.move"

    def action_force_retry_edi_payment_decimals(self):
        """Fallback for a generic account_edi retry button.

        The visible MX CFDI row normally uses l10n_mx_edi.document.  If this
        fallback is reached, direct the user to the CFDI row so the wizard can
        preserve the exact native retry action used by the localization.
        """
        self.ensure_one()
        raise UserError(_(
            "Usa 'Forzar volver a intentar' desde la fila del documento en la pestaña CFDI."
        ))
