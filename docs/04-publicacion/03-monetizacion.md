---
id: publicacion-monetizacion
titulo: Monetización de APIs
area: publicacion
tags: [monetizacion, rate-plan, prepago, pospago, wallet, revenue-share, appgroups, mint, datacapture]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/monetization/overview
revisado: 2026-10-23
---

# Monetización de APIs

> **Fecha de corte: 23 de octubre de 2026.**

Con **Apigee monetization**, un API product lleva asociado un **rate plan** (plan de tarifas). Ese plan cobra a los desarrolladores (o a los AppGroups) por usar las APIs del producto, con cuotas de alta, cuotas recurrentes y cobro por consumo. También permite **repartir ingresos** con socios desarrolladores.

## Disponibilidad

| Tipo de organización | Monetización |
|---|---|
| **Subscription** | Add-on que se compra a ventas y luego **se habilita por API** |
| **Pay-as-you-go** | **No disponible** |
| **Evaluación** | Incluye una prueba de monetización durante el periodo de evaluación |
| **hybrid** | Soportada. Hay un *known issue* (355714868) con los datos de cuotas recurrentes, de alta y de recarga en hybrid. |

> [!CAUTION]
> Como con los demás add-ons, la llamada que habilita o deshabilita la monetización **sobrescribe toda la configuración de add-ons** de la organización. Lee primero el perfil de la organización y envía la configuración completa.

## Piezas

| Pieza | Papel |
|---|---|
| **API proxy** | Las políticas que activan la monetización (ver la tabla siguiente) |
| **API product** | El paquete monetizado, con su cuota, su tipo de aprobación y su rate plan. Ver [API products](01-api-products.md). |
| **Rate plan** | Moneda, frecuencia de facturación, cuotas y reparto de ingresos |
| **Suscripción** | Obligatoria para que un desarrollador use un producto monetizado: directa, o heredada de un AppGroup |

### Políticas en los proxies

| Política | Para qué |
|---|---|
| [VerifyAPIKey](../02-politicas/referencia/verify-api-key.md) u [OAuthV2](../02-politicas/referencia/oauthv2.md) `VerifyAccessToken` | Identifican la app y el producto. Con ellas Apigee sabe si la petición es monetizable, porque hay un rate plan activo y publicado. |
| [MonetizationLimitsCheck](../02-politicas/referencia/monetization-limits-check.md) | **Bloquea** si el desarrollador no tiene suscripción o no tiene saldo prepago suficiente |
| [Quota](../02-politicas/referencia/quota.md) con `<UseQuotaConfigInAPIProduct>` | Aplica la **cuota de monetización** definida en el producto |
| [DataCapture](../02-politicas/referencia/data-capture.md) con `scope="monetization"` | Sobrescribe las variables de monetización (ver abajo) |

> [!NOTE]
> Si añades una cuota a un producto que ya está en uso, el cómputo empieza en el siguiente periodo.

## Rate plans

| Configuración | Detalle |
|---|---|
| Moneda | Default `USD` |
| Periodo de facturación | **Solo mensual** (`MONTHLY`) |
| Cuota de alta (*initialization fee*) | Se cobra una vez, cuando el desarrollador compra el producto |
| Cuota fija recurrente | Por unidad y con su frecuencia; se **prorratea** el primer periodo |
| Cobro por consumo | **Fijo por unidad** (`FIXED_PER_UNIT`) o **por tramos** (*banded*: precio variable según rangos de consumo) |
| Reparto de ingresos | Porcentaje para el socio desarrollador (`revenueShareType: FIXED` en los ejemplos) |
| Vigencia | Hora de activación y, opcional, de expiración (default: nunca) |
| Estado | `DRAFT` o `PUBLISHED` |

**Reglas de vigencia:**

- Un producto puede tener **varios rate plans**, pero **solo uno activo a la vez**. Se pueden publicar varios con periodos que **no se solapen**.
- Para publicar, hace falta una **hora de activación**.
- La activación debe ser anterior a la expiración.
- En la UI solo se elige la **fecha**: la hora se fija a `00:00:00.000` para la activación y a `23:59:59.999` para la expiración. Por API se fija en milisegundos epoch.
- Se gestionan en *Distribution > Monetization* o con la API `organizations/{org}/apiproducts/{producto}/rateplans`. Con residencia de datos, se pueden usar tanto la UI como la API.

## Facturación: prepago y pospago

| Modelo | Funcionamiento |
|---|---|
| **Pospago** | El desarrollador paga después de usar. **Apigee no genera facturas**: la liquidación es cosa tuya, a partir de los informes. |
| **Prepago** | El desarrollador recarga antes un **wallet**, del que se descuentan la cuota de alta, las recurrentes y el coste por transacción. Si el saldo no cubre la cuota de alta, **la compra del producto falla**. |

Gestión por API (`.../developers/{email}/monetizationConfig` y `.../appgroups/{nombre}/monetizationConfig`):

- consultar y cambiar el tipo de facturación (`billingType`: `PREPAID` o `POSTPAID`);
- ver el saldo;
- acreditarlo;
- ajustarlo.

**Cambio de tipo de facturación:** es inmediato. Al pasar de prepago a pospago, el saldo prepago restante aparece en los informes como una transacción de **crédito**.

> [!WARNING]
> Incluso con MonetizationLimitsCheck, **un desarrollador prepago puede quedar con saldo negativo**: la comprobación no es una reserva atómica del saldo. Ver la [referencia de la política](../02-politicas/referencia/monetization-limits-check.md).

## AppGroups

Si un **AppGroup** tiene suscripción a un producto, sus miembros heredan esa suscripción. Los AppGroups admiten:

- facturación `PREPAID` o `POSTPAID`;
- wallet con recargas y ajustes manuales;
- informes de consumo y de reparto de ingresos, igual que los desarrolladores.

Ver [AppGroups](02-developers-apps.md#appgroups--modelo-b2b).

## Cómo compran los desarrolladores

- **Portal Drupal** con el módulo *Apigee Monetization*.
- **Portal propio**, que compra y gestiona suscripciones con la API (`purchase API products`).
- **Gestión manual** por el proveedor.

## Variables de monetización

Variables predefinidas, que no se pueden crear ni renombrar. Distinguen mayúsculas y minúsculas, y no aparecen en *Admin > Data Collectors* ni en `datacollectors.list`. Se sobrescriben con **DataCapture** (`<DataCollector scope="monetization">`):

| Variable | Tipo | Efecto |
|---|---|---|
| `currency` | String | Moneda para calcular el ingreso de la transacción |
| `perUnitPriceMultiplier` | Float | Multiplicador del coste por transacción del plan |
| `revShareGrossPrice` | Float | Ingreso de la transacción sobre el que se calcula la parte del desarrollador, si hay reparto de ingresos |
| `transactionSuccess` | Boolean | `true` monetiza y `false` no. **Sin valor**, se monetiza según `message.status.code`: no se cobra si es nulo o ≥ 300. |

> [!TIP]
> Por defecto, una respuesta **4xx o 5xx no se cobra**. Si tu modelo de negocio necesita otra cosa (por ejemplo, no cobrar un 200 con error de negocio en el cuerpo), fija `transactionSuccess` con DataCapture.

## Informes y depuración

Los informes personalizados (UI, *stats API* o *queries API* asíncrona) tienen métricas y dimensiones propias:

- **Para transacciones de proxies:** las `x_apigee_mintng_*`, como `x_apigee_mintng_price`, `_rate`, `_dev_share`, `_price_multiplier`, `_rate_plan_id`, `_currency` y `_tx_success`.
- **Para transacciones de cuotas:** métricas propias, como `fees`.

En la herramienta **Debug**, las variables `mint.*` muestran el resultado de la monetización en cada transacción. Por ejemplo:

- `mint.mintng_is_apiproduct_monetized`;
- `mint.mintng_consumption_pricing_type`;
- `mint.mintng_currency`;
- `mint.mintng_dev_share`;
- las `mint.limitscheck.*` de MonetizationLimitsCheck.

> [!NOTE]
> La página de Debug escribe algunas variables con dos formas distintas, por ejemplo `mint.limitscheck.is_subscription_found` y `mint.limitscheck_is_subscription_found`. La [referencia de la política](../02-politicas/referencia/monetization-limits-check.md) usa la forma con punto.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Monetization overview: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/overview>, contenido completo.
- Steps to use monetization: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/steps>, contenido completo.
- Enable monetization: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/enable>, contenido completo.
- Manage rate plans: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/manage-rate-plans>, campos, vigencia y estados.
- Enforce monetization quotas: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/enforce-monetization-quotas-api-products>, contenido completo.
- Capture monetization data: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/capture-monetization-data>, contenido completo.
- Manage prepaid balances: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/manage-prepaid-balances>, configuración y cambio de facturación.
- Generate monetization reports: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/generate-reports>, métricas y dimensiones.
- Debug monetization: <https://docs.cloud.google.com/apigee/docs/api-platform/monetization/debug-trace>, variables `mint.*`.
