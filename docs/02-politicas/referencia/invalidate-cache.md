---
id: politica-invalidate-cache
titulo: InvalidateCache — referencia completa
area: politicas
tags: [invalidatecache, cache, purga, purgechildentries, cachecontext, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: InvalidateCache
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/invalidate-cache-policy
revisado: 2026-10-22
---

# InvalidateCache — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<InvalidateCache>`.
> **Aplica a:** Apigee X, hybrid y Edge.

InvalidateCache **borra** entradas de la caché de propósito general antes de que venzan: una sola entrada, o todas las que comparten prefijo. Se usa cuando el dato de origen cambió (p. ej. tras un `PUT` sobre un recurso cuyo `GET` está cacheado) o para forzar que se pida un token nuevo.

Para vaciar una caché fuera del flujo de mensajes, sin políticas, está la API de gestión de cachés (en X/hybrid, la operación de borrado de cachés).

## Sintaxis completa

```xml
<InvalidateCache name="IC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <CacheKey>
    <Prefix>prefijo</Prefix>
    <KeyFragment ref="variable"/>
    <KeyFragment>literal</KeyFragment>
  </CacheKey>
  <CacheResource>nombre_de_cache</CacheResource>
  <Scope>Exclusive</Scope>
  <CacheContext>
    <APIProxyName ref="variable">proxy-que-escribio</APIProxyName>
    <ProxyName ref="variable">proxy-endpoint</ProxyName>
    <TargetName ref="variable">target-endpoint</TargetName>
  </CacheContext>
  <PurgeChildEntries>false</PurgeChildEntries>
</InvalidateCache>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; máximo 255 caracteres. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<CacheKey>` | **Sí** | — | — | Clave de la entrada a borrar. |
| `<CacheResource>` | No | String | caché compartida | Debe ser la caché donde se escribió. |
| `<Scope>` | No | String | `Exclusive` | Prefijo automático si no hay `<Prefix>`. |
| `<CacheContext>` | No | — | — | Reconstruye el prefijo de `<Scope>` de **otro** proxy. |
| `<PurgeChildEntries>` | No | Boolean | `false` | Borra todas las entradas que comparten el prefijo. |

### `<CacheKey>`, `<Scope>` y `<CacheResource>`

Deben reproducir exactamente la clave con la que la [PopulateCache](populate-cache.md) escribió. Ver [Claves de caché](claves-de-cache.md).

### `<CacheContext>`

Cuando la entrada la escribió **otro proxy** con un `<Scope>` (no con `<Prefix>`), el prefijo contiene el nombre de ese proxy y de su endpoint. `<CacheContext>` permite indicar esos valores para reconstruir la clave:

| Hijo | Qué indica | Admite `ref` |
|---|---|---|
| `<APIProxyName>` | Proxy que escribió la entrada. | Sí |
| `<ProxyName>` | ProxyEndpoint en el que se cacheó. | Sí |
| `<TargetName>` | TargetEndpoint en el que se cacheó. | Sí |

Los tres son **obligatorios** cuando se borran entradas de otro proxy sin `<Prefix>` propio. En la práctica es más simple y robusto usar `<Prefix>` en las tres políticas y olvidarse de `<CacheContext>`.

### `<PurgeChildEntries>`

Con `true`, borra todas las entradas que comparten el prefijo de esta política, sin importar los `<KeyFragment>` con los que se escribieron. Permite purgar un grupo entero (p. ej. todo lo de `catalogo`) con una sola ejecución.

> [!WARNING]
> **Discrepancia entre ediciones.** La página de X/hybrid habla de borrar las entradas que comparten el mismo **prefijo**; la de Edge habla de las que comparten el mismo **valor de fragmento de clave**. Prueba en tu organización qué entradas se borran antes de diseñar sobre una de las dos lecturas.

### Consistencia tras invalidar

La invalidación borra la entrada de la caché en memoria (L1) del message processor que ejecuta la política y de la caché persistente (L2). **Los demás message processors pueden seguir sirviendo el valor viejo desde su L1 durante hasta un segundo.** Ver [Funcionamiento interno](claves-de-cache.md#funcionamiento-interno-l1-y-l2).

## Variables de flujo

La página oficial no documenta variables propias.

## Errores

### En runtime

La política no lanza errores en runtime. No hay variables de fallo propias.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidCacheResourceReference` | `<CacheResource>` no existe en el entorno. |
| `CacheNotFound` | La caché no se ha creado en un message processor concreto. |

## Ejemplos

### 1. Invalidar el token cuando el backend lo rechaza

Si el backend responde `401` con el token cacheado (fue revocado antes de tiempo), se borra la entrada para que la siguiente petición pida uno nuevo. Misma clave que [PopulateCache — ejemplo 1](populate-cache.md#1-token-del-backend-con-ttl-tomado-de-la-respuesta).

```xml
<InvalidateCache name="IC-Token">
  <CacheKey>
    <Prefix>token-backend</Prefix>
    <KeyFragment>core-bancario</KeyFragment>
  </CacheKey>
</InvalidateCache>
```

```xml
<!-- TargetEndpoint, flujo de respuesta -->
<Step>
  <Name>IC-Token</Name>
  <Condition>response.status.code = 401</Condition>
</Step>
```

### 2. Purgar todo un grupo tras una actualización

Tras un `PUT` exitoso sobre `/catalogo`, se borran todas las entradas con prefijo `catalogo-v2`.

```xml
<InvalidateCache name="IC-Catalogo-Completo">
  <CacheKey>
    <Prefix>catalogo-v2</Prefix>
  </CacheKey>
  <PurgeChildEntries>true</PurgeChildEntries>
</InvalidateCache>
```

### 3. Borrar una entrada escrita por otro proxy con `<Scope>`

El proxy `perfiles-api`, en su ProxyEndpoint `default`, guardó la entrada con `<Scope>Proxy</Scope>`. Este proxy administrativo la borra reconstruyendo el contexto.

```xml
<InvalidateCache name="IC-Perfil-De-Otro-Proxy">
  <CacheKey>
    <KeyFragment ref="admin.cliente_id"/>
  </CacheKey>
  <Scope>Proxy</Scope>
  <CacheContext>
    <APIProxyName>perfiles-api</APIProxyName>
    <ProxyName>default</ProxyName>
    <TargetName>default</TargetName>
  </CacheContext>
</InvalidateCache>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Alcance de `<PurgeChildEntries>` | Mismo prefijo | Mismo valor de fragmento de clave (ver discrepancia arriba) |
| Prefijo de `<Scope>` | Sin revisión en esta página | Incluye el número de revisión desplegada |
| Borrado fuera de flujo | API de cachés de X/hybrid | API de gestión "Clear a cache entry" de Edge |
| Elementos y errores | Iguales | Iguales |

## Antipatrones

- Depender de `<CacheContext>` cuando se podría usar un `<Prefix>` compartido.
- Asumir que, tras invalidar, ningún message processor servirá el valor viejo.
- `<PurgeChildEntries>true</PurgeChildEntries>` con un prefijo demasiado amplio, que vacía más de lo previsto.

## Fuentes

- InvalidateCache policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/invalidate-cache-policy> (consultada directamente, contenido completo, 2026-10-22).
- Invalidate Cache policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/invalidate-cache-policy> (consultada directamente, 2026-10-22).
- Cache internals: <https://docs.cloud.google.com/apigee/docs/api-platform/cache/cache-internals>
