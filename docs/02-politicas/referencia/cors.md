---
id: politica-cors
titulo: CORS — referencia completa
area: politicas
tags: [cors, preflight, options, navegador, same-origin, seguridad, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: CORS
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy
revisado: 2026-10-22
---

# CORS — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<CORS>`.
> **Aplica a:** Apigee X y hybrid. **No existe como política en Apigee Edge**, donde CORS se implementa con AssignMessage y un flujo condicional para `OPTIONS`.

La política CORS hace que un API pueda ser llamado desde **JavaScript en un navegador** servido desde otro dominio. Responde las peticiones *preflight* (`OPTIONS`) y añade a las respuestas las cabeceras `Access-Control-*` según la configuración.

> [!CAUTION]
> CORS **relaja** la política de mismo origen del navegador; no es un control de seguridad del API. Dos configuraciones lo anulan:
>
> - `<AllowOrigins>*</AllowOrigins>` desactiva en la práctica la protección de mismo origen.
> - `<AllowOrigins>{request.header.origin}</AllowOrigins>`, que **es la plantilla por defecto de la UI**, devuelve como permitido **el origen que mande el cliente, sea cual sea**. Es aún peor que `*` si además pones `<AllowCredentials>true</AllowCredentials>`, porque permite que cualquier web haga peticiones autenticadas con las cookies del usuario.
>
> Usa siempre una **lista explícita** de orígenes. Google indica que `AllowOrigins` no debería ser `*` por defecto.

## Sintaxis completa

```xml
<CORS name="CORS-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <AllowOrigins>https://app.ejemplo.com, https://portal.ejemplo.com</AllowOrigins>
  <AllowMethods>GET, POST, PUT, DELETE</AllowMethods>
  <AllowHeaders>origin, x-requested-with, accept, content-type, authorization</AllowHeaders>
  <ExposeHeaders>x-request-id, x-ratelimit-remaining</ExposeHeaders>
  <MaxAge>3600</MaxAge>
  <AllowCredentials>false</AllowCredentials>
  <GeneratePreflightResponse>true</GeneratePreflightResponse>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
</CORS>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `cors.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Cabecera que genera | Resumen |
|---|---|---|---|
| `<AllowOrigins>` | **Sí** | `Access-Control-Allow-Origin` | Lista de orígenes separados por comas, `*`, o plantilla de mensaje con una variable que contenga la lista. Si el origen de la petición está en la lista, se devuelve **ese** origen. Falta → `MissingAllowOrigins`. |
| `<AllowMethods>` | No | `Access-Control-Allow-Methods` | Métodos permitidos, o `*`. Un método inválido → `InvalidHTTPMethods`. |
| `<AllowHeaders>` | No | `Access-Control-Allow-Headers` | Cabeceras que el navegador puede enviar. |
| `<ExposeHeaders>` | No | `Access-Control-Expose-Headers` | Cabeceras de la respuesta que el JavaScript puede leer, o `*`. |
| `<MaxAge>` | No | `Access-Control-Max-Age` | Segundos que el navegador puede cachear el preflight; `-1` desactiva la caché (un `OPTIONS` antes de cada llamada). No numérico → `InvalidMaxAge`. |
| `<AllowCredentials>` | No | `Access-Control-Allow-Credentials` | Permitir que la petición real lleve credenciales (cookies, `Authorization` gestionado por el navegador). |
| `<GeneratePreflightResponse>` | No | — | `true`: la política responde el preflight. `false`: no responde y deja el resultado en variables. |
| `<IgnoreUnresolvedVariables>` | No | — | Seguir o fallar si una variable no resuelve. |

`<AllowHeaders>` y `<ExposeHeaders>` demasiado largos hacen fallar el despliegue (`AllowHeadersSizeTooLarge`, `ExposeHeadersSizeTooLarge`).

> [!NOTE]
> La spec CORS no permite combinar `Access-Control-Allow-Origin: *` con `Access-Control-Allow-Credentials: true`: el navegador rechaza la respuesta. Si necesitas credenciales, usa la lista explícita.

## Cómo funciona en el flujo

- **Preflight (`OPTIONS`):** cuando la política procesa un `OPTIONS` (con `<GeneratePreflightResponse>true</GeneratePreflightResponse>`), el flujo **salta directamente al PreFlow de respuesta del ProxyEndpoint**, sin pasar por el resto del flujo de petición ni por el backend. No hace falta una condición para excluir `OPTIONS` del resto de políticas.
- **Peticiones reales:** justo antes de enviar la respuesta al cliente, un paso especial (`CORSResponseOrErrorFlowExecution`) añade `Access-Control-Allow-Credentials`, `Access-Control-Allow-Origin` y `Access-Control-Expose-Headers`, también en respuestas de **error**.

> [!IMPORTANT]
> Pon la política CORS **al principio** del PreFlow de petición del ProxyEndpoint, **antes** de la autenticación: el preflight del navegador no lleva credenciales y, si VerifyAPIKey u OAuthV2 se ejecutan antes, lo rechazarán con 401 y el navegador bloqueará todas las llamadas.

## Variables de flujo

Todas con prefijo `cross_origin_resource_sharing.`, de lectura/escritura y disponibles desde la petición del proxy: `allow.credentials`, `allow.headers`, `allow.methods`, `allow.origin` (el origen permitido, vacío si no está en la lista), `allow.origins.list`, `expose.headers`, `max.age`, `preflight.accepted`, `request.headers`, `request.method`, `request.origin` y `request.type` (`ACTUAL` o `PRE_FLIGHT`). En Debug aparece un objeto `CorsFlowInfo`.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.cors.UnresolvedVariable` | 500 | Una variable no existe o está fuera de alcance. |

Con `<GeneratePreflightResponse>true</GeneratePreflightResponse>`, si hay un error la política responde directamente y **no** se pueblan las variables de fallo.

### Al desplegar

`InvalidMaxAge`, `MissingAllowOrigins`, `InvalidHTTPMethods`, `AllowHeadersSizeTooLarge`, `ExposeHeadersSizeTooLarge`.

### Variables de fallo

`fault.name` y `cors.{name}.failed`.

## Ejemplos

### 1. SPA y portal propios

```xml
<CORS name="CORS-Web">
  <AllowOrigins>https://app.ejemplo.com, https://portal.ejemplo.com</AllowOrigins>
  <AllowMethods>GET, POST, PUT, PATCH, DELETE</AllowMethods>
  <AllowHeaders>content-type, authorization, x-request-id</AllowHeaders>
  <ExposeHeaders>x-request-id</ExposeHeaders>
  <MaxAge>3600</MaxAge>
  <GeneratePreflightResponse>true</GeneratePreflightResponse>
</CORS>
```

### 2. Orígenes por entorno desde un PropertySet

```xml
<CORS name="CORS-Por-Entorno">
  <AllowOrigins>{propertyset.cors.origenes}</AllowOrigins>
  <AllowMethods>GET, POST</AllowMethods>
  <AllowHeaders>content-type, authorization</AllowHeaders>
  <GeneratePreflightResponse>true</GeneratePreflightResponse>
</CORS>
```

Con `cors.origenes=https://app-dev.ejemplo.com` en desarrollo y `https://app.ejemplo.com` en producción.

## Diferencias en Apigee Edge

La política CORS **no existe en Edge**. Allí se usa un flujo condicional para `request.verb = "OPTIONS"` que responde con AssignMessage (sin `RouteRule` al backend), y otra AssignMessage que añade las cabeceras `Access-Control-*` a las respuestas. Al migrar a X, sustitúyelo por la política.

## Antipatrones

- `AllowOrigins` con `*` o `{request.header.origin}`, sobre todo con credenciales.
- Poner CORS después de la autenticación.
- `ExposeHeaders` con `*` sin necesidad.
- Usar CORS como si protegiera el API: solo afecta a navegadores; `curl` o un servidor lo ignoran.

## Fuentes

- CORS policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/cors-policy> (consultada directamente, contenido completo, 2026-10-22).
