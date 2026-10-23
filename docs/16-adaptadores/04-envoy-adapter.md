---
id: adaptadores-envoy
titulo: Apigee Adapter for Envoy
area: adaptadores
tags: [envoy, adapter, istio, service-mesh, remote-service, ext-authz, jwt, multicloud]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/concepts
revisado: 2026-10-23
---

# Apigee Adapter for Envoy

> **Fecha de corte: 23 de octubre de 2026.** Versión documentada: **v2.0.x** (la más reciente del índice oficial; las v1.x siguen publicadas).

El **Apigee Adapter for Envoy** es un gateway ligero, gestionado por Apigee, que usa **Envoy** como proxy. Se ejecuta **cerca de los backends**: on-premises, en otra nube o dentro de una service mesh. Apigee aporta tres cosas:

- autenticación y autorización (API keys y OAuth);
- gestión de cuotas;
- Analytics.

## Arquitectura

| Plano | Componente | Función |
|---|---|---|
| Datos (remoto) | **Envoy** | Recibe la llamada del cliente y pasa el contexto de seguridad, por cabeceras, al Remote Service (filtro `ext_authz`) |
| Datos (remoto) | **Apigee Remote Service for Envoy** | **PDP:** indica a Envoy si permite o deniega cada petición |
| Gestión (Google Cloud) | Organización de Apigee | El Remote Service le consulta **de forma asíncrona** (*polling*) y descarga productos, configuración y proxies |

Si la llamada se permite, Envoy la reenvía al backend. Los datos de analítica se envían a Apigee de forma asíncrona, sin añadir latencia.

## Tolerancia a cortes con el plano de gestión

El adapter **tolera interrupciones temporales**, pero con el tiempo pierde funciones. Necesita conexión para:

- **generar tokens OAuth**;
- **verificar API keys**: la primera verificación de cada key necesita conexión, y después queda en caché;
- **aplicar cuotas**;
- **enviar Analytics**.

> [!CAUTION]
> Una API key nueva no funciona mientras no haya conexión con Apigee, porque su primera verificación necesita el plano de gestión. Si el sitio remoto puede quedar aislado, pruébalo antes de prometer disponibilidad.

## Modos de instalación

| Modo | Descripción |
|---|---|
| **Envoy nativo** | Envoy y el Remote Service como procesos locales, fuera de Kubernetes. Válido para Apigee y hybrid. |
| **Istio / service mesh** (con hybrid) | El Remote Service se despliega en la mesh y da servicio a los sidecars de Istio de los servicios destino. |

## Puesta en marcha

1. Descargar dos binarios en `$ENVOY_HOME`: **`apigee-remote-service-cli`** y **`apigee-remote-service-envoy`**.
2. **`apigee-remote-service-cli provision`:** instala dos proxies de Apigee en la organización (entre ellos `remote-service`), configura un certificado y genera las credenciales del adapter. Con `--force-proxy-install` se reinstalan.
3. **`samples create`:** genera la configuración de Envoy o de Istio a partir de plantillas (`--template`; la lista sale con `samples templates`).
4. Crear developer, API product y app en Apigee, igual que para un proxy normal.

> [!NOTE]
> La página de referencia de X dice que `provision` instala los proxies «en tu organización de Apigee **Edge**». Es un resto de la documentación de Edge: en X/hybrid se instalan en la organización de Apigee correspondiente.

## Operación

- **Credenciales del cliente:**
  - API key, o **JWT emitido por Apigee** (`apigee-remote-service-cli token create`, `token inspect`, `token rotate-cert`).
  - Si el JWT falla, Envoy rechaza la petición.
  - También se admite un **proveedor de identidad propio**.
- **Analytics:** las métricas de Envoy y de Istio conviven con las de Apigee, y se pueden capturar datos para informes personalizados.
- **Otras opciones:**
  - soporte multi-tenant;
  - un proxy de red de salida;
  - cambiar el nombre del *policy secret*;
  - **mTLS entre el adapter y el runtime de Apigee**.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Concepts (v2.0.x): <https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/concepts>, contenido completo.
- Getting started (v2.0.x): <https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/getting-started>, contenido completo.
- Operations guide (v2.0.x): <https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/operation>, estructura y secciones.
- Reference (v2.0.x): <https://docs.cloud.google.com/apigee/docs/api-platform/envoy-adapter/v2.0.x/reference>, comandos `provision`, `samples` y `token`.
