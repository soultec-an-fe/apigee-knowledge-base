---
id: aas-vision-general
titulo: Advanced API Security — visión general, habilitación y roles
area: seguridad-avanzada
tags: [advanced-api-security, add-on, abuse-detection, risk-assessment, security-actions, aapi-ops, roles, xff]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-security/aas-apigee-overview
revisado: 2026-10-23
---

# Advanced API Security — visión general, habilitación y roles

> **Fecha de corte: 23 de octubre de 2026.**

**Advanced API Security** es un **add-on de pago** que vigila la postura de seguridad de las APIs. Detecta abuso con reglas y modelos de *machine learning*, puntúa la configuración de los proxies y permite bloquear o marcar tráfico. Según Google, su uso **no afecta al tráfico de runtime**; la excepción son las *security actions*, que sí intervienen en él (ver [02](02-deteccion-y-acciones.md)).

## Dos formas de habilitarlo

| Dónde se habilita | Qué ofrece | Alcance |
|---|---|---|
| **En la organización de Apigee** | La suite completa: detección de abuso, informes, *risk assessment*, *security actions* y alertas | Una organización de Apigee X o hybrid |
| **En API hub** | Solo **evaluación de riesgos multi-gateway** | Varias organizaciones y gateways, **incluido Apigee Edge** |

## Funcionalidades

| Función | Qué hace | Documento |
|---|---|---|
| **Abuse detection** | Agrupa eventos sospechosos en **incidentes**, a partir de reglas de detección | [02](02-deteccion-y-acciones.md) |
| **Security actions** | **Allow**, **Deny** o **Flag** de tráfico según condiciones, antes de que llegue al proxy | [02](02-deteccion-y-acciones.md) |
| **Risk assessment** | Puntúa cada proxy contra un perfil de seguridad y recomienda correcciones | [03](03-risk-assessment-e-informes.md) |
| **Security reports** | Informes de tráfico malicioso por dimensión (país, IP, etc.) | [03](03-risk-assessment-e-informes.md) |
| **Security alerts** | Alertas en Cloud Monitoring sobre cambios de puntuación o incidentes | [03](03-risk-assessment-e-informes.md) |

**No cubre** las APIs servidas con el [Apigee Adapter for Envoy](../16-adaptadores/04-envoy-adapter.md).

## Disponibilidad y habilitación

**Disponible como add-on de pago en:**

- organizaciones Subscription y Pay-as-you-go;
- organizaciones hybrid;
- organizaciones con residencia de datos.

Se puede probar gratis en organizaciones de prueba.

| Modelo | Cómo se habilita |
|---|---|
| **Subscription** | Tiene que estar en tus *entitlements* (lo gestiona ventas). Después se habilita por API en la configuración de add-ons de la organización. |
| **Pay-as-you-go** | Como add-on **por entorno**, solo en entornos **Intermediate** o **Comprehensive**. |

> [!CAUTION]
> **La llamada que habilita el add-on sobrescribe toda la configuración de add-ons de la organización.**
> - Primero lee la configuración actual (`GET` de la organización, sección de add-ons).
> - Después envíala completa, junto con el cambio. Si no lo haces, desactivas otros add-ons (por ejemplo, Analytics o AAPI Ops).
> - En Subscription, si creas un entorno nuevo después de habilitar el add-on, **hay que repetir la llamada** para que cubra ese entorno.

## Roles

| Rol | Para qué |
|---|---|
| `roles/apigee.admin` | Habilitar o deshabilitar el add-on; además, todo lo demás |
| `roles/apigee.securityAdmin` | Crear informes, gestionar perfiles de seguridad y condiciones de monitoreo, crear, editar y borrar *security actions*, y activar o desactivar el *opt-in* de los modelos de ML |
| `roles/apigee.securityViewer` | Ver informes, puntuaciones, perfiles, incidentes y *security actions* |
| `roles/monitoring.admin` o `roles/monitoring.editor` | Ver las métricas de las condiciones de monitoreo |

Para optar por los modelos de ML también vale el permiso suelto `apigee.securitySettings.update`.

## Buenas prácticas oficiales

- **Configura la resolución de la IP del cliente** por entorno, si el algoritmo por defecto no encaja con tu topología de balanceadores. Ver [client IP resolution](https://docs.cloud.google.com/apigee/docs/api-platform/system-administration/client-ip-resolution).
- **No elimines la cabecera `X-Forwarded-For`** en los balanceadores o proxies previos. Sin ella, Advanced API Security no ve la IP real del cliente: en Analytics el valor aparece como `(not set)`, y detección y acciones pierden precisión.

## Ofuscación de datos

Si ofuscas datos de Analytics (por ejemplo, la IP del cliente se sustituye por un hash):

- La **detección y las *security actions* se aplican antes de la ofuscación**, así que siguen funcionando con la IP real.
- Lo que ves en la UI está ofuscado, y **no se puede recuperar el valor en claro**. Para crear una *security action* por IP necesitas la IP original por otra vía: usar el hash no sirve.

## AAPI Ops: anomalías operativas

**Operations anomalies** es un add-on distinto (**AAPI Ops**). Detecta de forma estadística dos tipos de anomalía, a nivel de organización, entorno y región:

- un aumento de los errores **4xx o 5xx**;
- un aumento de la **latencia p90**.

Permite investigar cada anomalía y crear alertas.

- **Habilitación:** por API, entrada `advancedApiOpsConfig` en la configuración de add-ons. La misma advertencia de sobrescritura se aplica aquí.
- **Roles para usarlo:** `roles/apigee.readOnlyAdmin`, `roles/logging.viewer` y `roles/monitoring.viewer`.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Advanced API Security overview: <https://docs.cloud.google.com/apigee/docs/api-security>, contenido completo.
- Advanced API Security from your Apigee instance: <https://docs.cloud.google.com/apigee/docs/api-security/aas-apigee-overview>, contenido completo.
- Enable Advanced API Security: <https://docs.cloud.google.com/apigee/docs/api-security/enable-security>, contenido completo.
- Best practices: <https://docs.cloud.google.com/apigee/docs/api-security/best-practices>, contenido completo.
- Operations anomalies overview (AAPI Ops): <https://docs.cloud.google.com/apigee/docs/aapi-ops>, contenido completo.
