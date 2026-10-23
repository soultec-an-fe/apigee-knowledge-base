---
id: edge-diferencias-por-area
titulo: Edge frente a Apigee X — diferencias por área
area: edge
tags: [edge, migracion, diferencias, virtual-hosts, environment-groups, roles, iam, portal, monetizacion, analytics, trace, kvm]
aplica_a: [apigee-edge, apigee-x]
fuente: https://docs.apigee.com/api-platform/fundamentals/virtual-hosts
revisado: 2026-10-23
---

# Edge frente a Apigee X — diferencias por área

> **Fecha de corte: 23 de octubre de 2026.** Diferencias **de plataforma** entre Apigee Edge y Apigee X/hybrid. Las de cada política están en la sección «Diferencias en Apigee Edge» de su [referencia](../02-politicas/referencia/00-indice.md). Las tablas son una síntesis de este repositorio a partir de las páginas citadas de cada edición.

## Organización, entornos y entrada de tráfico

| Concepto | Edge | X / hybrid |
|---|---|---|
| Organización | Independiente de Google Cloud | 1 organización = 1 proyecto de Google Cloud |
| Entornos de partida (Edge Cloud) | `test` y `prod`, creados automáticamente | Los que crees |
| **Entrada de tráfico** | **Virtual hosts** en el Router: nombre, *host alias*, puerto y TLS. En Edge Cloud hay dos por entorno: `default` (80, HTTP) y `secure` (443, HTTPS), con `{org}-{env}.apigee.net`. | **Environment groups** con hostnames, y un balanceador de Google Cloud o el ingress de hybrid (ver [organizaciones y entornos](../00-fundamentos/04-organizaciones-entornos-grupos.md)) |
| El proxy elige su entrada | `<VirtualHost>` en el ProxyEndpoint | **No** hay `<VirtualHost>`: el proxy recibe el tráfico de todos los hostnames del grupo de su entorno |

> [!WARNING]
> **Al migrar:**
> - Los `<VirtualHost>` de los proxies de Edge **se ignoran** en X.
> - Si un proxy de Edge separaba tráfico por *virtual host* (por ejemplo, partners por `secure-partners` y público por `secure`), en X necesita **entornos o grupos distintos**, o condiciones sobre `request.header.host`.
> - Los hosts `*.apigee.net` desaparecen: los clientes cambian de URL salvo que uses tu propio dominio.

## Identidad y acceso

| Concepto | Edge | X / hybrid |
|---|---|---|
| Usuarios | Usuarios de Edge (cuentas Apigee), con **2FA** opcional y **SAML** para la UI | Principales de **IAM** de Google Cloud, Workforce Identity Federation y SAML para la consola (ver [usuarios y roles](../15-administracion/01-usuarios-roles-e-identidad.md)) |
| Roles predefinidos | **Organization Administrator**, **Read-only Organization Administrator**, **Operations Administrator**, **Business User**, **User**; en Private Cloud, además, **System administrator** | Roles IAM de Apigee: Org Admin, API Admin, Environment Admin, Developer Admin, Analytics… |
| Roles personalizados | Permisos por **URI de la API de gestión y verbo**; el permiso más específico prevalece | Roles IAM personalizados e IAM Conditions |
| Autenticación de la API de gestión | Tokens OAuth de Apigee (`get_token`, SSO) o Basic Auth | Tokens de Google Cloud (`gcloud auth print-access-token`) |

> [!NOTE]
> Ejemplo de la granularidad de Edge: el rol **User** puede desplegar **solo en `test`**. Tiene `PUT` sobre `/environments/test/applications/*/revisions/*/deployments` y solo `GET` sobre el resto de entornos.

## Desarrollo y depuración

| Concepto | Edge | X / hybrid |
|---|---|---|
| Depuración | **Trace**: la sesión se detiene sola a los **10 minutos** y captura **10 transacciones por Message Processor** | **Debug**: 10 minutos y **15 transacciones por MP** (ver [Debug](../05-operacion/02-debug-trace.md)) |
| Código propio en el gateway | JavaScript, Java, Python; Node.js embebido (retirado) y **Hosted Targets** | JavaScript, Java y Python; la lógica externa va a Cloud Run o Functions vía ExternalCallout o ServiceCallout (ver [Node.js y Hosted Targets](04-nodejs-hosted-targets-y-extensions.md)) |
| Conectores | **Extensions** (ExtensionCallout) | Políticas nativas (MessageLogging, PublishMessage) y [ServiceCallout](../02-politicas/referencia/service-callout.md) con autenticación de Google |
| Políticas de IA, Model Armor, caché semántica, MCP | No | Sí |
| Tipos de proxy | Un solo tipo | **Standard / Extensible**, con impacto en el coste (ver el [catálogo](../02-politicas/00-catalogo-de-politicas.md)) |

## Datos, caché y KVM

| Concepto | Edge | X / hybrid |
|---|---|---|
| KVM | **Cifrados o sin cifrar**, a elección (AES-128 con clave de Apigee) | Siempre cifrados |
| Estadísticas personalizadas | Política [StatisticsCollector](../02-politicas/referencia/statistics-collector.md) | [DataCapture](../02-politicas/referencia/data-capture.md) con recursos *data collector* |
| Retención de Analytics (Edge Cloud) | Según el plan. Por defecto, los datos de **más de seis meses** no se pueden consultar sin pedirlo a soporte. | Según el plan y la configuración de la organización (ver [Analytics](../05-operacion/03-analytics-monitoreo.md)) |
| Monitorización operativa | **API Monitoring** (Edge Cloud Enterprise) | Cloud Monitoring, AAPI Ops y Advanced API Security |

## Publicación y monetización

| Concepto | Edge | X / hybrid |
|---|---|---|
| Portal | **Portal integrado** y **Drupal**. La vía actual es Drupal 10 con *Apigee Developer Portal Kickstart*; el alojamiento de portales Drupal patrocinado por Apigee terminó el 31/05/2020. | Portal integrado y Drupal; además, **API hub** como catálogo de gobierno |
| Agrupar productos para cobrar | **API product bundles** (*API packages*) | El rate plan va directamente sobre el API product |
| Qué cuenta como transacción | **Transaction recording policy** por producto (por ejemplo, `response.reason.phrase = OK`) | Las variables de monetización con [DataCapture](../02-politicas/referencia/data-capture.md); por defecto, por código de estado |
| Tipos de rate plan | Fees, **rate card**, **revenue share**, rate card + revenue share, **adjustable notification**, **freemium**; públicos o privados | Cuotas de alta, recurrentes y por consumo (fijo o por tramos), reparto de ingresos; **solo facturación mensual** (ver [monetización](../04-publicacion/03-monetizacion.md)) |
| Clientes que pagan | **Companies** y developers | Developers y **AppGroups** |
| Pospago | Facturación mensual con límites de crédito | Apigee no genera facturas: la liquidación es tuya |

## Operación de la plataforma

| Concepto | Edge Cloud | Edge Private Cloud | X | hybrid |
|---|---|---|---|---|
| Quién opera el runtime | Google | **Tú** (RPM en tus servidores) | Google | **Tú** (Kubernetes) |
| Almacenes de datos | — | Cassandra, ZooKeeper, Postgres, Qpid y LDAP | — | Cassandra y Redis |
| Actualizaciones | Continuas | Tú, según el [ciclo LTS](01-panorama-y-ciclo-de-vida.md#ciclo-de-vida-de-private-cloud) | Continuas, con ventanas de mantenimiento | Tú, con Helm |
| Gateway ligero cerca del backend | [Edge Microgateway](03-microgateway.md) y Envoy | Microgateway y Envoy | [Envoy adapter, Extension Processor, Operator for Kubernetes](../16-adaptadores/01-panorama.md) | Ídem |

## Checklist de migración de Edge a X

1. **Inventario:**
   - proxies que usen `<HostedTarget>`, `<ScriptTarget>` (Node.js), `ConnectorCallout`, `StatisticsCollector`, `ConcurrentRatelimit` u OAuth 1.0a;
   - JavaCallout, para revisar la versión de Java.
2. **Entrada:** *virtual hosts* → environment groups, y certificados en el balanceador.
3. **Identidad:** usuarios y roles de Edge → IAM (más Spaces o IAM Conditions si se separaban equipos).
4. **Datos:**
   - KVM: en X siempre cifrados;
   - developers, apps y keys: hay que importarlas para conservar las credenciales;
   - productos.
5. **Monetización:** rediseñar los planes al modelo de X (sin *packages* ni *transaction recording policy*).
6. **Observabilidad:** API Monitoring → Cloud Monitoring y AAPI Ops; Trace → Debug.
7. **Validación:** `apigeelint --profile apigeex` sobre cada bundle (ver [bundles](../../ejemplos/bundles/README.md#validación)) y las herramientas de migración de [apigee/devrel](../../ejemplos/02-devrel.md).

La checklist es de este repositorio, no una guía oficial de Google.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Virtual hosts (Edge): <https://docs.apigee.com/api-platform/fundamentals/virtual-hosts>, contenido completo.
- Edge built-in roles: <https://docs.apigee.com/api-platform/system-administration/edge-built-roles>, contenido completo.
- Two-factor authentication: <https://docs.apigee.com/api-platform/system-administration/enable-two-factor-auth-your-apigee-account>.
- Using the Trace tool: <https://docs.apigee.com/api-platform/debug/using-trace-tool-0>, límites.
- Key value maps (Edge): <https://docs.apigee.com/api-platform/cache/key-value-maps>, cifrado.
- Analytics (Edge), notas de retención: <https://docs.apigee.com/api-platform/analytics/analytics-services-overview> y relacionadas.
- Apigee Developer Portal Kickstart (Drupal 10): <https://docs.apigee.com/api-platform/publish/drupal/d7-end-of-hosting-faq>, y deprecaciones de Edge para el fin del alojamiento patrocinado.
- Monetization basics (Edge): <https://docs.apigee.com/api-platform/monetization/basics-monetization>, contenido completo.
- Rate plans (Edge): <https://docs.apigee.com/api-platform/monetization/intro-rateplans>, tipos.
- Las páginas de Apigee X enlazadas en cada fila.
