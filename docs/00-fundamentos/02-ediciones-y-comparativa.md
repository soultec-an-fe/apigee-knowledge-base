---
id: fundamentos-ediciones
titulo: Ediciones de Apigee — X, hybrid y Edge
area: fundamentos
tags: [apigee-x, hybrid, edge, eol, migracion, comparativa]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.apigee.com/migration-to-x/compare-apigee-edge-to-apigee-x
revisado: 2026-08-20
---

# Ediciones de Apigee — X, hybrid y Edge

> [!IMPORTANT]
> Para cualquier proyecto nuevo: **usa Apigee X**. Apigee Edge está en fin de vida.

## Comparativa

| Dimensión | Apigee X | Apigee hybrid | Apigee Edge (legacy) |
|---|---|---|---|
| Plano de control | Google Cloud | Google Cloud | Apigee/Google (SaaS) o tuyo (OPDK) |
| Plano de runtime | Gestionado por Google | Tu clúster Kubernetes (GKE, EKS, AKS, OpenShift, on-prem) | SaaS o tus máquinas |
| Vinculación a proyecto GCP | 1 org = 1 proyecto GCP, mismo nombre | 1 org = 1 proyecto GCP | Org independiente de GCP |
| Networking | VPC peering / Private Service Connect, Cloud Load Balancing | Ingress de tu clúster | Virtual hosts |
| Identidad | IAM de Google Cloud | IAM de Google Cloud | Usuarios y roles propios de Edge |
| UI | Consola de Google Cloud | Consola de Google Cloud | Classic UI (**apagada el 2 de noviembre de 2025**) |
| Node.js embebido (Trireme) | No | No | Sí (retirado) |
| Políticas de IA (LLM, Model Armor, caché semántica) | Sí | Parcial, según versión | No |
| Estado | Activo, recomendado | Activo | **EOL** |

## Estado de fin de vida de Apigee Edge

Datos confirmados en la documentación de Google:

- **Classic UI de Apigee Edge**: apagada el **2 de noviembre de 2025**.
- **Edge for Private Cloud 4.53**: fin de vida el **11 de abril de 2026**.
- **Edge for Private Cloud 4.53.01**: fin de vida el **26 de febrero de 2027**.
- **API BaaS** y **Node.js basado en Trireme**: retirados.

> [!WARNING]
> Las fechas de EOL cambian. Verifica siempre en
> <https://docs.apigee.com/release/deprecated-features> antes de planificar una migración.

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
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/organization-structure>
