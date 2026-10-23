---
id: aas-risk-assessment
titulo: Risk assessment, informes y alertas de seguridad
area: seguridad-avanzada
tags: [risk-assessment, security-scores, security-profiles, security-reports, security-alerts, cloud-monitoring]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-security/security-scores
revisado: 2026-10-23
---

# Risk assessment, informes y alertas de seguridad

> **Fecha de corte: 23 de octubre de 2026.** Requiere el add-on [Advanced API Security](01-vision-general.md).

## Risk assessment

El *risk assessment* evalúa periódicamente la **configuración** de los proxies desplegados contra un **perfil de seguridad**. Calcula una puntuación y da recomendaciones. No mira el tráfico: mira qué políticas tiene cada proxy. Hay dos versiones; **Google recomienda la v2**.

| Aspecto | v1 | **v2** |
|---|---|---|
| Escala | Puntuación propia de la v1 | **0 % a 100 %** |
| ¿Hace falta adjuntar un perfil al entorno para puntuar? | Sí | No |
| Pesos por comprobación | No | Sí |
| Políticas de autenticación evaluadas | 5 | 8 |
| Categoría de *traffic management* y revisión de `continueOnError` | No | Sí |
| Shared flows encadenados y flow hooks | No evalúa el encadenamiento | Hasta **5 niveles** |
| Target servers | Puntuación separada | Integrados en la puntuación del proxy |
| *Source assessment* (por tráfico abusivo) | Sí | **No** |
| Integración con API hub y Cloud Monitoring | — | Sí |
| Perfil de sistema | Default | `google-default`, y perfiles propios |

### Cómo se calcula la puntuación (v2)

- Cada **comprobación** tiene un peso: **minor = 1**, **moderate = 5** y **major = 15** puntos.
- **Puntuación** = puntos de las comprobaciones superadas ÷ puntos posibles del perfil. Es una media ponderada: cuantas más comprobaciones tiene el perfil, menos pesa cada una.
- **Severidad** según la puntuación:

| Puntuación | Severidad |
|---|---|
| 0–50 % | High |
| 51–90 % | Medium |
| 91–99 % | Low |
| 100 % | Minimal (sin riesgos según el perfil) |

### Ejemplos de comprobaciones

| Comprobación | Pasa si el proxy tiene alguna de |
|---|---|
| `auth-policies-check` | AccessControl, BasicAuthentication, HMAC, OAuth, ValidateSAMLAssertion, VerifyAPIKey, VerifyIAM, VerifyJWS o VerifyJWT |
| `mediation-policies-check` | SOAPMessageValidation u OASValidation |
| `threat-policies-check` | JSONThreatProtection, RegularExpressionProtection o XMLThreatProtection |
| `traffic-management-policies-check` | LookupCache, Quota, ResponseCache o SpikeArrest |

### Qué cuenta y qué no

- **Solo cuentan las políticas adjuntas a un flujo** (PreFlow, flujo condicional, PostFlow o shared flow). Una política definida en el bundle pero sin `<Step>` no suma.
- **Cuentan los shared flows** llamados por flow hook o por un FlowCallout que esté adjunto a un flujo.
- **En los flujos condicionales** se comprueba que la política **está**, no si se ejecuta en runtime.

> [!WARNING]
> Por esta última regla, una VerifyAPIKey dentro de un flujo condicional que nunca se cumple da la misma puntuación que una que se aplica siempre. Una puntuación del 100 % no sustituye a la revisión de los flujos ni a las [pruebas de seguridad](../03-seguridad/01-apikeys.md).

### Monitoreo y alertas

En la v2, puntuaciones y métricas se pueden seguir en el tiempo con **condiciones de monitoreo** en Cloud Monitoring, y generar alertas a partir de ellas.

## Security reports

Son informes de tráfico de seguridad por métricas y dimensiones (por ejemplo, peticiones maliciosas por país de origen). Se crean en la UI o por API, y se ejecutan como trabajos asíncronos.

| Límite | Valor |
|---|---|
| Rango temporal máximo (informes de bots) | **1 año**, siempre en el pasado |
| Métricas por informe | 25 |
| Dimensiones por informe | 25 |
| Tamaño del informe | **31 MB**, como la API asíncrona de informes personalizados |
| Caducidad en la UI | **7 días** tras crearlo (expórtalo antes) |
| Eliminación de la lista | A los **30 días** |

## Security alerts

Las alertas se crean en **Cloud Monitoring**, con políticas de umbral sobre métricas, y se notifican por los canales que configures (email, SMS, etc.).

Métricas disponibles, entre otras:

- puntuación de seguridad del proxy;
- puntuación de *sources* y de *target servers* (v1);
- puntuación total del entorno;
- incidentes de abuso.

Las alertas funcionan tanto con la v1 como con la v2 del risk assessment.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Risk assessment overview and UI: <https://docs.cloud.google.com/apigee/docs/api-security/security-scores>, secciones v1/v2, metodología, comprobaciones y adjuntos.
- Security reports UI: <https://docs.cloud.google.com/apigee/docs/api-security/security-reports-ui>, límites.
- Security report jobs: <https://docs.cloud.google.com/apigee/docs/api-security/security-report-jobs>, caducidad.
- Security alerts: <https://docs.cloud.google.com/apigee/docs/api-security/security-alerts>.
