# MX EDI - Forzar reintento de decimales

Módulo independiente para Odoo 19. Agrega **Forzar volver a intentar** junto al reintento nativo del documento CFDI mexicano.

## Detección automática

Al pulsar **Forzar volver a intentar**:

1. Si el error actual ya es `CRP20268` o `CRPER654`, aplica directamente la corrección correspondiente.
2. Si el error actual es otro (por ejemplo `702` del PAC), primero ejecuta un reintento normal.
3. Lee la nueva respuesta real del PAC.
4. Si el PAC devuelve `CRP20268` o `CRPER654`, aplica automáticamente la corrección y reintenta una segunda vez en el mismo clic.
5. Si devuelve cualquier otro error, no altera decimales.

## Correcciones

### CRP20268
Solo durante el reintento corregido:
- `BaseDR` se trunca a la precisión de `MonedaDR`.
- `ImporteDR` se trunca a la precisión de `MonedaDR`.
- `BaseP` e `ImporteP` conservan el comportamiento normal.

Ejemplo MXN:
- `BaseDR: 135775.862069 -> 135775.86`
- `ImporteDR: 21724.137931 -> 21724.13`

### CRPER654
Solo durante el reintento corregido:
- `BaseP` se limita a la precisión de `MonedaP` (MXN = 2 decimales).
- No se alteran `BaseDR`, `ImporteDR` ni `ImporteP`.

El botón normal **Volver a intentar** permanece intacto.
