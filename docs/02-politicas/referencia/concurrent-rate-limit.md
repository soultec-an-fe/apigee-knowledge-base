---
id: politica-concurrent-rate-limit
titulo: ConcurrentRateLimit — retirada (solo Edge, histórico)
area: politicas
tags: [concurrentratelimit, retirada, edge, spike-arrest, quota, migracion]
aplica_a: [apigee-edge]
elemento_xml: ConcurrentRatelimit
tipo_politica: trafico
fuente: https://docs.apigee.com/release/deprecated-features
revisado: 2026-10-22
---

# ConcurrentRateLimit — retirada (solo Edge, histórico)

> [!CAUTION]
> **Política retirada.** Se anunció su deprecación el **15 de julio de 2020** para Edge Cloud y Private Cloud, y se retiró el **15 de julio de 2021**. En Private Cloud ya no está a partir de la versión **4.50.00**. Nunca existió en Apigee X ni en hybrid.
> La antigua URL de su referencia (`docs.apigee.com/api-platform/reference/policies/concurrent-rate-limit-policy`) hoy **redirige a la página de deprecaciones**: Google ya no publica su sintaxis.

## Qué hacía

Limitaba el número de **conexiones concurrentes** desde Apigee hacia un backend, pensando en backends lentos. Según Google, la arquitectura que usaba afectaba al rendimiento de las APIs, y por eso se retiró.

El elemento XML es `<ConcurrentRatelimit>`, con *l* minúscula en *limit*. El dato viene de la documentación histórica de Edge; no se puede verificar en la página actual, que ya no existe. **Pendiente de verificación** si necesitas migrar un bundle antiguo: confirma el nombre en el XML del propio bundle.

## Cómo migrar

Google recomienda pasar a [Quota](quota.md) y/o [SpikeArrest](spike-arrest.md), combinadas con encadenamiento de proxies o shared flows, para proteger backends lentos sin penalizar el rendimiento.

| Necesidad que cubría ConcurrentRateLimit | Alternativa |
|---|---|
| No saturar un backend lento | [SpikeArrest](spike-arrest.md) con una tasa acorde a la capacidad del backend |
| Tope de consumo por app o cliente | [Quota](quota.md) distribuida |
| Fallar rápido si el backend no responde | Timeouts del TargetEndpoint e `<HealthMonitor>` con `<LoadBalancer>` (ver [target endpoints](../../01-proxies/05-target-endpoints-y-servidores.md)) |

Ver también el antipatrón [permitir un backend lento](../../08-mejores-practicas/03-rendimiento.md#backends-lentos).

## Fuentes

- Apigee deprecations and retirements (Edge): <https://docs.apigee.com/release/deprecated-features> (consultada directamente, 2026-10-22; la URL de la política redirige aquí).
