---
id: edge-nodejs-hosted-targets-extensions
titulo: Edge — Node.js, Hosted Targets y Extensions
area: edge
tags: [edge, nodejs, trireme, apigee-access, hosted-targets, app-yaml, extensions, connectorcallout, migracion]
aplica_a: [apigee-edge]
fuente: https://docs.apigee.com/api-platform/nodejs/node-overview
revisado: 2026-10-23
---

# Edge — Node.js, Hosted Targets y Extensions

> **Fecha de corte: 23 de octubre de 2026.** ⚠️ **Solo Apigee Edge.** Ninguna de estas tres funciones existe en Apigee X ni en hybrid: la tabla del final da sus equivalentes.

Edge ofrecía tres formas de ejecutar o conectar código fuera de las políticas estándar: **Node.js embebido** (Trireme), **Hosted Targets** y **Extensions**.

## Node.js embebido (Trireme)

El Node.js «tradicional» de Edge ejecutaba el código **dentro del runtime Java de Edge**, con un puente de código abierto (**Trireme**) y el intérprete **Rhino**. El código vivía en `resources/node/` y servía de target a los proxies del mismo entorno. Con el módulo **`apigee-access`** podía leer variables de flujo, caché, KVM y cuotas.

| Edición | Estado |
|---|---|
| **Edge Public Cloud** | **Retirado el 10 de octubre de 2019**. Con él se retiró también `apigee-access`. |
| **Edge Private Cloud** | Deprecado el 15/07/2020 y **retirado en la 4.50.00** (15/07/2021). Google recomienda llevar los proxies Node.js a un entorno Node.js nativo **fuera** de Apigee, y los *secure vaults* a KVM cifrados. |

**Limitaciones que tenía, según la documentación:**

- solo **Node.js 0.10.32**;
- diferencias sutiles de comportamiento con el Node.js estándar;
- depuración difícil una vez desplegado;
- módulos restringidos: sin servidores TCP (`net`), sin UDP hacia internet (`dgram`), `fs` limitado a `resources/node`, `cluster` desactivado y `child_process` sin poder crear subprocesos.

## Hosted Targets

**Hosted Targets** ejecuta aplicaciones **Node.js nativas** en un entorno gestionado por Apigee, construido sobre **Google App Engine**. Es lo que Google recomendaba en lugar de Trireme.

- **Disponibilidad:** en todas las organizaciones de **Edge Public Cloud**, sin instalación. Se comprueba con `features.isEdgeFunctionsEnabled = true` en la organización.
- **Runtimes:** solo Node.js. La versión se elige en el manifiesto; el default es la LTS v10.x.
- **Estructura:**
  - el código va en `apiproxy/resources/hosted/`;
  - un manifiesto **`app.yaml`** en esa carpeta: `runtime: node` (obligatorio), `runtimeVersion` y `env` (variables de entorno);
  - el TargetEndpoint lleva `<HostedTarget/>` en lugar de `<HTTPTargetConnection>`.

| Limitación | Detalle |
|---|---|
| Acceso al contexto del proxy | **No hay**: sin `apigee-access`, sin variables de flujo, caché ni KVM. Alternativas: políticas estándar, cabeceras o variables de entorno alimentadas desde un KVM. |
| Aplicaciones por proxy | **Una** (la de `resources/hosted`) |
| Varias revisiones desplegadas | No se admite, aunque Edge sí lo permite en proxies normales con *basepaths* distintos |
| IP de salida | **Sin IP estática**: App Engine usa un rango de IPs |
| TLS | PEM con OpenSSL nativo, no JKS |
| Streaming | No: App Engine no lo admite |
| Timeout de petición | **60 s**, el de App Engine |
| Cabeceras | 8 KB por defecto en versiones recientes de Node.js |
| Disco temporal | Sistema de archivos **en memoria**: borra siempre los temporales |
| Migración desde Trireme | Manual, sin herramienta automática |

> [!NOTE]
> La implementación de referencia [`apigee/openbank`](../../ejemplos/03-openbank.md) usa Hosted Targets para sus sandboxes. Por eso no se despliega tal cual en Apigee X.

## Extensions

Las **Extensions** conectan un proxy con un recurso externo, sobre todo servicios de Google Cloud, mediante un conector configurado por el administrador y la política **ExtensionCallout** (elemento `<ConnectorCallout>`). Ver la [referencia de la política](../02-politicas/referencia/extension-callout.md).

- **Disponibilidad:** en la UI de Edge, para clientes de Google Cloud Apigee con plan de soporte **Enterprise**.
- **Funcionamiento:**
  1. El administrador **añade, configura y despliega** una extensión en un entorno, con credenciales y parámetros.
  2. El desarrollador la invoca con una **acción** y su **entrada** JSON.
- **Paquetes de extensión documentados:**
  - Google Authentication, BigQuery, Cloud Data Loss Prevention, Firestore, Cloud Functions;
  - Cloud Logging y Stackdriver Logging, Natural Language, Pub/Sub, Spanner;
  - Cloud Storage, Vision, Machine Learning Engine;
  - Amazon S3, AWS Lambda;
  - Informatica Integration, Salesforce.

## Equivalencias en Apigee X

| En Edge | En X / hybrid |
|---|---|
| Node.js embebido o Hosted Targets como backend | Backend propio en **Cloud Run** (o GKE/Functions) invocado como target con autenticación de Google, o un [ExternalCallout](../02-politicas/referencia/external-callout.md) si necesita el contexto del proxy |
| `apigee-access` para variables, KVM y caché | Pasar los datos por cabeceras, o resolver la lógica con políticas ([KeyValueMapOperations](../02-politicas/referencia/key-value-map-operations.md), [LookupCache](../02-politicas/referencia/lookup-cache.md), [JavaScript](../02-politicas/referencia/javascript.md)) |
| Lógica JavaScript ligera en Node.js | Política [JavaScript](../02-politicas/referencia/javascript.md) (Rhino 1.7.13) |
| Extension de Cloud Logging | [MessageLogging](../02-politicas/referencia/message-logging.md) con `<CloudLogging>` |
| Extension de Pub/Sub | [PublishMessage](../02-politicas/referencia/publish-message.md) |
| Otras extensiones de Google Cloud | [ServiceCallout](../02-politicas/referencia/service-callout.md) con `<Authentication>` (token de Google) |

Las equivalencias de la tabla son una síntesis de este repositorio. Google recomienda Cloud Run o Cloud Functions como sustitutos de Hosted Targets en su guía de buenas prácticas de lógica propia (ver [ExternalCallout](../02-politicas/referencia/external-callout.md)).

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Node.js overview (Edge): <https://docs.apigee.com/api-platform/nodejs/node-overview>, contenido completo.
- Overview of Node.js on Apigee Edge: <https://docs.apigee.com/api-platform/nodejs/overview-nodejs-apigee-edge>, contenido completo.
- Understanding Edge support for Node.js modules: <https://docs.apigee.com/api-platform/nodejs/understanding-edge-support-nodejs-modules>, tabla de módulos.
- Hosted Targets overview: <https://docs.apigee.com/api-platform/hosted-targets/hosted-targets-overview>, contenido completo.
- Hosted Targets FAQ: <https://docs.apigee.com/api-platform/hosted-targets/hosted-targets-faq>, contenido completo.
- Hosted Targets reference: <https://docs.apigee.com/api-platform/hosted-targets/hosted-targets-reference>, manifiesto `app.yaml`.
- Extensions overview: <https://docs.apigee.com/api-platform/extensions/extensions-overview>, contenido completo.
- Apigee deprecations and retirements: <https://docs.apigee.com/release/deprecated-features>.
