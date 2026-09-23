# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation, ROUND_DOWN

from odoo import api, models


class AccountPayment(models.Model):
    _inherit = "account.payment"

    @api.model
    def _l10n_mx_force_truncate_decimal(self, value, precision):
        """Return value truncated (never rounded) to ``precision`` decimals."""
        try:
            precision = int(precision or 0)
            decimal_value = Decimal(str(value or 0))
        except (TypeError, ValueError, InvalidOperation):
            return value

        quantum = Decimal("1").scaleb(-precision)
        truncated = decimal_value.quantize(quantum, rounding=ROUND_DOWN)
        return f"{truncated:.{precision}f}"
