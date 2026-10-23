---
id: fundamentos-ediciones
titulo: Ediciones de Apigee — X, hybrid y Edge
area: fundamentos
tags: [apigee-x, hybrid, edge, eol, migracion, comparativa]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.apigee.com/release/apigee-edge-release-process
revisado: 2026-10-23
---

# Ediciones de Apigee — X, hybrid y Edge

> [!IMPORTANT]
> Para cualquier proyecto nuevo: **usa Apigee X**, que es donde llegan las novedades (IA, MCP, API hub, Advanced API Security). Apigee Edge es la generación anterior. **No está en fin de vida como producto**: Edge Public Cloud sigue con versiones, y Private Cloud 4.54 tiene soporte hasta octubre de 2029. Sí lo están varias versiones y funciones (ver abajo y [17-edge](../17-edge/01-panorama-y-ciclo-de-vida.md)).

## Comparativa

| Dimensión | Apigee X | Apigee hybrid | Apigee Edge (legacy) |
|---|---|---|---|
| Plano de control | Google Cloud | Google Cloud | Apigee/Google (SaaS) o tuyo (OPDK) |
| Plano de runtime | Gestionado por Google | Tu clúster Kubernetes (GKE, EKS, AKS, OpenShift, on-prem) | SaaS o tus máquinas |
| Vinculación a proyecto GCP | 1 org = 1 proyecto GCP, mismo nombre | 1 org = 1 proyecto GCP | Org independiente de GCP |
| Networking | VPC peering / Private Service Connect, Cloud Load Balancing | Ingress de tu clúster | Virtual hosts |
| Identidad | IAM de Google Cloud | IAM de Google Cloud | Usuarios y roles propios de Edge |
| UI | Consola de Google Cloud | Consola de Google Cloud | Edge UI (`apigee.com/edge`) en Public Cloud; **New Edge UI** en Private Cloud (la Classic UI se eliminó en 4.54.00) |
| Node.js embebido (Trireme) | No | No | Sí (retirado) |
| Políticas de IA (LLM, Model Armor, caché semántica) | Sí | Parcial, según versión | No |
| Estado | Activo, recomendado | Activo | Legado: soportado, con versiones y funciones en fin de vida |

## Estado de fin de vida de Apigee Edge

Datos confirmados en la documentación de Google:

- **Classic UI de Apigee X/hybrid** (`apigee.google.com`, no la de Edge): apagado general el **29 de agosto de 2025**; apagado final para clientes con excepción aprobada el **29 de septiembre de 2025**. Fue la fase final del paso de Apigee a la consola de Google Cloud. *Corrección del 2026-10-23: este repositorio la atribuía antes a Edge.*
- **Classic UI de Edge for Private Cloud** (`edge-ui`): **eliminada en la 4.54.00** (octubre de 2026); queda la New Edge UI.
- **Edge for Private Cloud 4.53**: fin de vida el **11 de abril de 2026**.
- **Edge for Private Cloud 4.53.01**: fin de vida el **30 de junio de 2027**. *Corrección del 2026-10-23: antes figuraba el 26 de febrero de 2027; la página oficial cambió la fecha.*
- **Edge for Private Cloud 4.54.00** (LTS, octubre de 2026): soporte completo hasta **abril de 2028** y fin de vida en **octubre de 2029**.
- **Edge for Private Cloud 4.52.00 / 4.52.01 / 4.52.02**: fin de vida el 31/08/2024, 30/09/2025 y 31/12/2025 respectivamente.
- **API BaaS** y **Node.js basado en Trireme**: retirados.
- **Política `ConcurrentRateLimit`**: deprecada el 15/07/2020, retirada de Private Cloud en la versión 4.50.00 (15/07/2021). No confundir con la política `Quota`, que sigue vigente.

> [!NOTE]
> **Hasta la 4.53.01**, cada versión mayor o menor de Apigee Edge Private Cloud recibía soporte completo durante
> **~18 meses** desde su fecha de lanzamiento inicial. **Desde la 4.54.00**, las versiones LTS tienen 36 meses (18 de soporte completo y 18 de mantenimiento): ver [17-edge](../17-edge/01-panorama-y-ciclo-de-vida.md#ciclo-de-vida-de-private-cloud). Una versión de parche (p. ej. `4.53.00.04`)
> **no extiende** la ventana de soporte de la versión mayor/menor. Actualizar a una versión
> más reciente reinicia la ventana de 18 meses. El contrato comercial (2-3 años) sigue vigente
> independientemente del ciclo de vida de la versión de software concreta que estés ejecutando.
>
> Verifica siempre las fechas vigentes en <https://docs.apigee.com/release/apigee-edge-release-process>
> y <https://docs.cloud.google.com/apigee/docs/deprecations/apigee-classic-ui> antes de planificar una migración.

## Diferencias que importan al escribir código

Si migras de Edge a X, esto es lo que rompe:

| Elemento de Edge | Qué pasa en Apigee X |
|---|---|
| **Virtual hosts** | Sustituidos por **environment groups** con hostnames. Ver [entornos](04-organizaciones-entornos-grupos.md). |
| **Node.js / `hosted targets`** | No existe. Migra el backend a Cloud Run, GKE o Cloud Functions y apúntalo como TargetEndpoint. |
| **Política `Python`** | No disponible en X. Reescribe en JavaScript o JavaCallout. |
| `apigeetool` | Sustituido por [`apigeecli`](../06-devops/02-herramientas-cli.md), `gcloud apigee` y el plugin de Maven. |
| API de gestión `api.enterprise.apigee.com` | Sustituida por `apigee.googleapis.com` con autenticación OAuth de Google Cloud. |
| Usuarios y roles de Edge | Sustituidos por **IAM de Google Cloud** (`roles/apigee.*`). |
| Organizaciones "trial" | Sustituidas por orgs de **evaluación** (temporales, sin escalabilidad de producción). |
| Extensiones (Extensions) | Sustituidas por `ExternalCallout`, `IntegrationCallout` y ServiceCallout. |

> [!NOTE]
> Apigee X **no es una actualización in-place**. Es una plataforma distinta con otra API de gestión y otro modelo de despliegue. Las migraciones reales toman meses.

## Tipos de organización

| Tipo | Descripción |
|---|---|
| **Paid / producción** | Permanente, escalabilidad completa. Creada bajo modelo de Suscripción o Pay-as-you-go. |
| **Evaluación (eval)** | Temporal y self-service, para probar Apigee. Limitada en tiempo, escalabilidad y flexibilidad. No usar para producción. |

Una organización de Apigee X o hybrid **mapea a exactamente un proyecto de Google Cloud** y comparte su nombre.

## Cuándo elegir hybrid en lugar de X

Elige **hybrid** solo si tienes un requisito duro:

- Residencia de datos que obliga a que el tráfico y los payloads no salgan de tu infraestructura.
- Backends que solo son alcanzables desde una red privada sin posibilidad de peering/PSC.
- Regulación que exige control operativo del runtime.

El coste es real: operas Cassandra, el ingress, los certificados y las actualizaciones del runtime tú mismo.

## Fuentes

- <https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x>
- <https://docs.apigee.com/release/deprecated-features>
- <https://docs.apigee.com/release/private-cloud-release-lifecycle-policy> (consultada el 2026-10-23)
- <https://docs.apigee.com/release/apigee-edge-release-process> (consultada el 2026-10-23)
- <https://docs.cloud.google.com/apigee/docs/deprecations/apigee-classic-ui> (consultada el 2026-10-23)
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/organization-structure>
