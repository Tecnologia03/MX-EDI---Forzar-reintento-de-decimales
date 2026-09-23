# -*- coding: utf-8 -*-
import logging

from odoo import _, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class L10nMxEdiDocument(models.Model):
    _inherit = "l10n_mx_edi.document"

    def _l10n_mx_force_retry_error_text(self):
        """Collect the current EDI/PAC error without depending on one field name.

        The Enterprise localization has changed the technical error field between
        revisions.  Read likely text fields on the MX document and, when
        available, the generic EDI error message from the related move.
        """
        self.ensure_one()
        parts = []

        preferred = {
            "error", "error_message", "message", "blocking_error",
            "response", "response_message",
        }
        for field_name, field in self._fields.items():
            if field.type not in ("char", "text", "html"):
                continue
            low = field_name.lower()
            if field_name not in preferred and not any(token in low for token in ("error", "message")):
                continue
            try:
                value = self[field_name]
            except Exception:
                continue
            if isinstance(value, str) and value.strip():
                parts.append(value)

        # Most l10n_mx_edi.document revisions are related to an account.move.
        for relation_name in ("move_id", "account_move_id"):
            if relation_name not in self._fields:
                continue
            move = self[relation_name]
            if not move:
                continue
            for field_name in ("edi_error_message", "l10n_mx_edi_error", "l10n_mx_edi_error_message"):
                if field_name in move._fields:
                    value = move[field_name]
                    if isinstance(value, str) and value.strip():
                        parts.append(value)

        return "\n".join(parts)

    @staticmethod
    def _l10n_mx_force_retry_correction_from_text(error_text):
        text = (error_text or "").upper()
        if "CRP20268" in text:
            return "crp20268"
        if "CRPER654" in text:
            return "crper654"
        return False

    def _l10n_mx_force_retry_call_native(self, source_method, correction=False):
        self.ensure_one()
        ctx = dict(self.env.context)
        # Remove helper keys so they never leak into the native action.
        for key in (
            "l10n_mx_force_retry_source_method",
            "l10n_mx_force_fix_crp20268",
            "l10n_mx_force_fix_crper654",
        ):
            ctx.pop(key, None)
        if correction:
            ctx.update({
                "l10n_mx_force_fix_crp20268": correction == "crp20268",
                "l10n_mx_force_fix_crper654": correction == "crper654",
            })
        return getattr(self.with_context(ctx), source_method)()

    def action_force_retry_edi_payment_decimals(self):
        """Retry once normally, detect the PAC error, and fix only when needed.

        - If the current error is already CRP20268/CRPER654, skip the redundant
          failed request and directly apply the corresponding workaround.
        - Otherwise run the native retry first.  If its response becomes
          CRP20268/CRPER654, immediately run one corrected retry in the same
          button click.
        - Any unrelated error (for example PAC 702) is left untouched.
        """
        self.ensure_one()

        source_method = self.env.context.get("l10n_mx_force_retry_source_method")
        if not source_method or source_method == "action_force_retry_edi_payment_decimals":
            raise UserError(_(
                "No se pudo identificar la acción nativa 'Volver a intentar' "
                "de este CFDI. Actualiza el módulo y vuelve a cargar la factura."
            ))
        if not hasattr(self, source_method):
            raise UserError(_(
                "La acción nativa de reintento '%s' ya no existe en esta versión de Odoo."
            ) % source_method)

        # 1) If Odoo still has the original relevant error, correct immediately.
        correction = self._l10n_mx_force_retry_correction_from_text(
            self._l10n_mx_force_retry_error_text()
        )
        if correction:
            _logger.info("MX force retry: applying %s directly on document %s", correction, self.id)
            return self._l10n_mx_force_retry_call_native(source_method, correction)

        # 2) Current error can be something unrelated (e.g. PAC 702). Retry
        # normally first so the PAC can expose the real CFDI validation error.
        normal_result = self._l10n_mx_force_retry_call_native(source_method)

        # Re-read values written by the native retry/PAC response.
        self.invalidate_recordset()
        correction = self._l10n_mx_force_retry_correction_from_text(
            self._l10n_mx_force_retry_error_text()
        )

        # 3) Only if the *actual* response is one of our two known decimal
        # errors, retry one more time with its specific workaround.
        if correction:
            _logger.info(
                "MX force retry: native retry returned %s; applying correction on document %s",
                correction, self.id,
            )
            return self._l10n_mx_force_retry_call_native(source_method, correction)

        _logger.info(
            "MX force retry: no CRP20268/CRPER654 detected after native retry for document %s",
            self.id,
        )
        return normal_result
