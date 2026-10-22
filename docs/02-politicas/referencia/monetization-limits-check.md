---
id: politica-monetization-limits-check
titulo: MonetizationLimitsCheck — referencia completa
area: politicas
tags: [monetizationlimitscheck, monetizacion, mint, suscripcion, wallet, prepago, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: MonetizationLimitsCheck
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/monetization-limits-check-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/monetization-limits-check-policy
revisado: 2026-10-22
---

# MonetizationLimitsCheck — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<MonetizationLimitsCheck>`.
> **Aplica a:** Apigee X, hybrid y Edge. **Solo funciona si la monetización de Apigee está habilitada en la organización.**

MonetizationLimitsCheck **bloquea** la llamada a una API monetizada cuando el desarrollador dueño de la app no cumple las condiciones de su plan: no tiene suscripción al producto, o es de prepago y no le alcanza el saldo. En el resto de los casos deja pasar la llamada y rellena variables `mint.*` con el resultado de la comprobación.

Requiere que antes en el flujo esté identificada la app, normalmente con [VerifyAPIKey](verify-api-key.md) u [OAuthV2](oauthv2.md) `VerifyAccessToken`. De ahí salen el producto (`apiproduct.name`) y el desarrollador (`developer.id`).

> [!WARNING]
> Incluso con esta política, **un desarrollador prepago puede consumir de más y quedar con saldo negativo**. La comprobación no es una reserva atómica de saldo. La documentación oficial describe en *Negative developer balance* las condiciones en que pasa esto.

## Sintaxis completa (X/hybrid)

```xml
<MonetizationLimitsCheck name="MLC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
  <FaultResponse>
    <AssignVariable>
      <Name>mlc.motivo</Name>
      <Value>limites</Value>
    </AssignVariable>
    <Set>
      <Headers>
        <Header name="Content-Type">application/json</Header>
      </Headers>
      <Payload contentType="application/json">{"error":"plan_insuficiente","detalle":"{mint.limitscheck.status_message}"}</Payload>
      <StatusCode>403</StatusCode>
    </Set>
  </FaultResponse>
</MonetizationLimitsCheck>
```

## Elementos hijos

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<FaultResponse>` | No | — | Respuesta al cliente cuando la política bloquea. Usa la misma estructura que el `<FaultResponse>` de [RaiseFault](raise-fault.md): `<AssignVariable>`, `<Add>`, `<Copy>`, `<Remove>` y `<Set>`, con cabeceras, payload y código de estado. |
| `<IgnoreUnresolvedVariables>` | No | `true` | Con `true`, sigue aunque una variable no resuelva. Es distinto de `continueOnError`. |

> [!NOTE]
> El ejemplo oficial de X interpola `{mint.limitscheck.isRequestBlocked}`, pero la tabla de variables documenta `mint.limitscheck.is_request_blocked`, con guiones bajos. Usa la forma de la tabla.

## Variables de flujo (X/hybrid)

| Variable | Valor |
|---|---|
| `mint.limitscheck.is_request_blocked` | `true` si la llamada se bloquea. |
| `mint.limitscheck.is_subscription_found` | `true` si hay suscripción al producto. |
| `mint.limitscheck.purchased_product_name` | Producto comprado. |
| `mint.limitscheck.status_message` | Resultado de la comprobación (ver tabla siguiente). |
| `mint.subscription_start_time_ms` / `mint.subscription_end_time_ms` | Inicio y fin de la suscripción, en epoch ms. |

| `status_message` | Significado |
|---|---|
| `limits_check_success` | Comprobación correcta. |
| `apiproduct_name_and_developer_email_not_available` | No se pudo determinar ni el producto ni el desarrollador. |
| `apiproduct_name_not_available` / `developer_email_not_available` | Falta uno de los dos. |
| `developer_usage_exceeds_balance` | Saldo prepago insuficiente. |
| `rateplan_not_available` | El producto no tiene plan de tarifas: **no se bloquea**. |
| `subscription_not_available` | El desarrollador no tiene suscripción. |
| `wallet_disabled_due_to_inactivity` | Wallet inactivo. Se reactiva con una recarga mínima (en dólares, 0,01). |
| `wallet_not_found` | El desarrollador no tiene wallet (por ejemplo, nunca recargó). |

> [!CAUTION]
> Con `apiproduct_name_not_available` y variantes, la política no puede comprobar nada. Ponla **después** de la verificación de credenciales: si va antes, la monetización no se aplica.

## Errores (X/hybrid)

Todos devuelven `500`, salvo que `<FaultResponse>` fije otro código.

| Código | Causa |
|---|---|
| `mint.service.subscription_not_found_for_developer` | El desarrollador no tiene suscripción al producto. |
| `mint.service.wallet_not_found_for_developer` | Desarrollador prepago sin wallet en la moneda del plan. |
| `mint.service.developer_usage_exceeds_balance` | El consumo supera el saldo. |
| `mint.service.wallet_blocked_due_to_inactivity` | Wallet sin recargas durante el periodo de inactividad. |

> [!NOTE]
> **Plazo de inactividad contradictorio en la página oficial:** la tabla de errores habla de más de **1,5 años** sin recargas; la descripción de `wallet_disabled_due_to_inactivity` dice más de **un año**. Verifícalo con la documentación de monetización antes de comunicárselo a tus clientes.

### Variables de fallo

`fault.name` y `MonetizationLimitsCheck.{policy_name}.failed`, con mayúscula inicial.

## Ejemplo: bloqueo con mensaje útil

```xml
<MonetizationLimitsCheck name="MLC-Plan">
  <FaultResponse>
    <Set>
      <Payload contentType="application/json">{"error":"acceso_no_permitido_por_plan","motivo":"{mint.limitscheck.status_message}"}</Payload>
      <StatusCode>402</StatusCode>
    </Set>
  </FaultResponse>
</MonetizationLimitsCheck>
```

Va en el PreFlow de petición del ProxyEndpoint, **después** de VerifyAPIKey. El `402 Payment Required` es una elección de diseño; el ejemplo oficial usa `403`.

## Diferencias en Apigee Edge

- **`<Variables>/<Product>`:** solo en Edge. Indica de qué variable leer el nombre del producto (default: `apiproduct.name`). El desarrollador siempre se toma de `developer.id`.
- **Caso adicional de bloqueo:** Edge también bloquea cuando se supera el **volumen de transacciones** del plan.
- **Variables con `continueOnError="true"`:** en Edge, en vez de lanzar el fallo, se fijan `mint.limitsViolated`, `mint.isDeveloperSuspended` y `mint.limitsPolicyError` para manejarlo a mano. En X la familia de variables es `mint.limitscheck.*`.
- **`<ReasonPhrase>`** aparece en el `<FaultResponse>` de los ejemplos de Edge; X no lo documenta.
- **Tabla de errores:** la página de Edge no publica una.

## Antipatrones

- **Ponerla antes de identificar la app.** Sin producto ni desarrollador no hay comprobación posible.
- **`continueOnError="true"` sin revisar luego las variables.** La API se sirve gratis.
- **Confiar en ella como límite de saldo exacto.** Puede haber saldo negativo; concilia en facturación.

## Fuentes

- MonetizationLimitsCheck policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/monetization-limits-check-policy> (consultada directamente, contenido completo, 2026-10-22).
- MonetizationLimitsCheck policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/monetization-limits-check-policy> (consultada directamente, contenido completo, 2026-10-22).
