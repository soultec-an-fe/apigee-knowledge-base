---
id: edge-panorama
titulo: Apigee Edge — panorama, estado y ciclo de vida
area: edge
tags: [edge, public-cloud, private-cloud, opdk, ciclo-de-vida, lts, eol, migracion, 4.54]
aplica_a: [apigee-edge]
fuente: https://docs.apigee.com/release/private-cloud-release-lifecycle-policy
revisado: 2026-10-23
---

# Apigee Edge — panorama, estado y ciclo de vida

> **Fecha de corte: 23 de octubre de 2026.** ⚠️ Este documento trata **Apigee Edge**. Para proyectos nuevos, este repositorio recomienda **Apigee X**; ver la [comparativa de ediciones](../00-fundamentos/02-ediciones-y-comparativa.md).

**Apigee Edge** es la generación anterior de Apigee, previa a la integración en Google Cloud. Tiene dos variantes:

| Variante | Quién la opera | Gestión |
|---|---|---|
| **Edge for Public Cloud** (Edge Cloud) | Google (SaaS) | Edge UI (`apigee.com/edge`) y API de gestión `api.enterprise.apigee.com` |
| **Edge for Private Cloud** (OPDK) | **Tú**, en tus servidores (RPM sobre RHEL y derivados) | New Edge UI y la API del Management Server que instalas |

Ninguna de las dos usa IAM de Google Cloud ni proyectos de GCP: tienen **usuarios, roles y organizaciones propios**.

## Estado a la fecha de corte

> [!IMPORTANT]
> **Edge no está en fin de vida como producto**, a diferencia de lo que decía una versión anterior de este repositorio:
> - **Edge Public Cloud** sigue publicando versiones: correcciones de SSO y de seguridad en octubre de 2026.
> - **Edge Private Cloud 4.54.00** salió el **15 de octubre de 2026** con soporte hasta **octubre de 2029**.
>
> Lo que sí tiene fin de vida son **versiones concretas** de Private Cloud y **funciones** concretas (ver las tablas siguientes).

### Ciclo de vida de Private Cloud

**Desde la 4.54.00: versiones LTS de 36 meses.**

| Fase | Meses | Qué entrega Google |
|---|---|---|
| Soporte completo | 1–18 | Correcciones, parches de seguridad, actualización de componentes incluidos y soporte |
| Mantenimiento | 19–36 | Solo defectos críticos y de severidad alta, seguridad de severidad alta y mitigaciones operativas |
| Fin de vida | Después del mes 36 | Nada: ni parches ni soporte |

| Versión LTS | Publicada | Fin del soporte completo | Fin de vida |
|---|---|---|---|
| **4.54.00.00** | Octubre de 2026 | **Abril de 2028** | **Octubre de 2029** |

- **Minor y parches de la 4.54 no mueven las fechas:** la 4.54.01, prevista para finales del primer trimestre de 2027, comparte el ciclo de la 4.54.00. Solo cambia el ciclo pasar a la **siguiente LTS**.
- **Numeración:** `4.5N.XX.YY`, sin la quinta parte de *hotfix* que tenían las versiones anteriores.
- **Actualización:** directa desde 4.53.00 o 4.53.01 a 4.54.00.

**Hasta la 4.53.01:** unos **18 meses** de soporte completo desde la publicación de cada versión menor. Un parche no alarga el plazo, y el contrato comercial sigue vigente aunque la versión llegue a su fin de vida.

| Versión | Fin de vida |
|---|---|
| 4.53.00 (todos sus parches) | **11 de abril de 2026** (ya pasado) |
| 4.53.01 (todos sus parches) | **30 de junio de 2027** |
| 4.52.00 / 4.52.01 / 4.52.02 | 31/08/2024, 30/09/2025 y 31/12/2025 (ya pasados) |

> [!WARNING]
> La fecha de fin de vida de la 4.53.01 **cambió**: este repositorio daba antes el 26 de febrero de 2027, y la página oficial dice ahora el **30 de junio de 2027**. Las fechas de ciclo de vida se mueven: compruébalas siempre en la página oficial antes de planificar.

### Funciones retiradas o eliminadas

| Función | Estado |
|---|---|
| Node.js embebido (Trireme) y `apigee-access` | Retirado en Public Cloud (10/10/2019) y en Private Cloud 4.50.00 (15/07/2021). Ver [Node.js y Hosted Targets](04-nodejs-hosted-targets-y-extensions.md). |
| OAuth 1.0a (OAuthV1 y relacionadas) | Retiradas (ver el [catálogo](../02-politicas/00-catalogo-de-politicas.md)) |
| ConcurrentRateLimit | Retirada (ver la [referencia](../02-politicas/referencia/concurrent-rate-limit.md)) |
| API BaaS | Retirado (30/06/2019) |
| Integración con Istio Mixer | Retirada; su sustituto es el adapter for Envoy |
| **Classic UI de Private Cloud** (`edge-ui`) y componente `apigee-sso` | **Eliminados en la 4.54.00**: solo queda la New Edge UI |
| *Security reporting*, *traffic alerts* y *advanced security reporting* de Edge Cloud | Retirada anunciada en julio de 2025 para **julio de 2026** |

## Qué hay en este área

| Documento | Contenido |
|---|---|
| [02-private-cloud.md](02-private-cloud.md) | Arquitectura, topologías, requisitos, puertos, instalación, operación y cambios de la 4.54 |
| [03-microgateway.md](03-microgateway.md) | Edge Microgateway |
| [04-nodejs-hosted-targets-y-extensions.md](04-nodejs-hosted-targets-y-extensions.md) | Node.js, Hosted Targets y Extensions |
| [05-api-monitoring-y-troubleshooting.md](05-api-monitoring-y-troubleshooting.md) | API Monitoring y diagnóstico en Edge |
| [06-diferencias-por-area.md](06-diferencias-por-area.md) | Qué cambia entre Edge y X en cada área (UI, identidad, redes, portal, monetización, Analytics…) |

Las diferencias **por política** están en la sección «Diferencias en Apigee Edge» de cada [referencia de política](../02-politicas/referencia/00-indice.md).

## Migrar a Apigee X

Google ofrece herramientas de apoyo:

- el **Apigee Edge to X Migration Accelerator** y el **Proxy Bundle Modifier & Validator**, en [apigee/devrel](../../ejemplos/02-devrel.md);
- `apigeecli` y `apigee-sackmesser` (ver [herramientas CLI](../06-devops/02-herramientas-cli.md)).

Lo que más trabajo da al migrar está en las [diferencias por área](06-diferencias-por-area.md):

- Node.js y Hosted Targets;
- Extensions;
- virtual hosts frente a environment groups;
- usuarios de Edge frente a IAM;
- monetización.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Edge for Private Cloud release and lifecycle policy: <https://docs.apigee.com/release/private-cloud-release-lifecycle-policy>, contenido completo.
- Apigee release process (4.53.01 y anteriores): <https://docs.apigee.com/release/apigee-edge-release-process>, contenido completo.
- Edge for Private Cloud release notes: <https://docs.cloud.google.com/apigee/docs/edge-private-cloud/release-notes>, entradas del 15 de octubre de 2026.
- Edge for Public Cloud release notes: <https://docs.cloud.google.com/apigee/docs/edge-public-cloud/release-notes>, contenido completo.
- Apigee deprecations and retirements: <https://docs.apigee.com/release/deprecated-features>, contenido completo.
