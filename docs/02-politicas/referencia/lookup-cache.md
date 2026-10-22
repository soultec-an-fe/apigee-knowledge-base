---
id: politica-lookup-cache
titulo: LookupCache — referencia completa
area: politicas
tags: [lookupcache, cache, populatecache, cachehit, rendimiento, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: LookupCache
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/lookup-cache-policy
revisado: 2026-10-22
---

# LookupCache — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<LookupCache>`.
> **Aplica a:** Apigee X, hybrid y Edge, con distinto default de `<CacheLookupTimeoutInSeconds>`.

LookupCache **lee** una entrada de la caché de propósito general y la asigna a una variable. Es la contraparte de [PopulateCache](populate-cache.md). Si no encuentra nada, la variable de destino **no se toca** y `lookupcache.{name}.cachehit` queda en `false`; el flujo sigue normalmente, sin error.

## Sintaxis completa

```xml
<LookupCache name="LC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <CacheKey>
    <Prefix>prefijo</Prefix>
    <KeyFragment ref="variable"/>
  </CacheKey>
  <CacheResource>nombre_de_cache</CacheResource>
  <CacheLookupTimeoutInSeconds>12</CacheLookupTimeoutInSeconds>
  <Scope>Exclusive</Scope>
  <AssignTo>variable.destino</AssignTo>
</LookupCache>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `lookupcache.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque falle. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<AssignTo>` | **Sí** | String | — | Variable donde se deja el valor. Debe ser escribible. |
| `<CacheKey>` | **Sí** | — | — | Clave. Debe coincidir con la de la PopulateCache. |
| `<CacheKey>/<Prefix>` | No | String | — | Anula `<Scope>`. |
| `<CacheKey>/<KeyFragment>` | No | String | — | Literal o `ref`. |
| `<CacheResource>` | No | String | caché compartida | Debe ser la misma que usó la PopulateCache. |
| `<CacheLookupTimeoutInSeconds>` | No | Integer | `12` en X/hybrid; `30` en Edge | Tras ese tiempo sin respuesta, se considera fallo de caché. |
| `<Scope>` | No | String | `Exclusive` | Prefijo automático. |

Ver [Claves de caché, alcance y funcionamiento interno](claves-de-cache.md) para la composición de la clave y el comportamiento L1/L2.

### `<AssignTo>`

Nombre de la variable que recibe el valor. Si no hay acierto, la variable **no se crea ni se vacía**: si ya tenía un valor de antes en el flujo, lo conserva. Por eso las decisiones posteriores deben basarse en `lookupcache.{name}.cachehit` y no en si la variable existe.

### `<CacheLookupTimeoutInSeconds>`

Un valor negativo hace fallar el despliegue (`InvalidTimeout`). Si la caché tarda más que este tiempo, el flujo sigue por el camino de fallo de caché.

## Variables de flujo

| Variable | Tipo | Acceso | Contenido |
|---|---|---|---|
| `lookupcache.{name}.cachename` | String | Lectura | Caché usada. |
| `lookupcache.{name}.cachekey` | String | Lectura | Clave calculada; la forma más rápida de diagnosticar por qué no hay acierto. |
| `lookupcache.{name}.cachehit` | Boolean | Lectura | `true` si encontró valor. |
| `lookupcache.{name}.assignto` | String | Lectura | Nombre de la variable de destino. |

## Errores

### En runtime

La política no lanza errores en runtime. No hay variables de fallo propias.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidCacheResourceReference` | `<CacheResource>` no existe en el entorno. |
| `InvalidTimeout` | `<CacheLookupTimeoutInSeconds>` negativo. |
| `CacheNotFound` | La caché no se ha creado en un message processor concreto. |

## Ejemplos

### 1. Leer el token guardado por PopulateCache

Pareja de [PopulateCache — ejemplo 1](populate-cache.md#1-token-del-backend-con-ttl-tomado-de-la-respuesta): misma clave, mismo prefijo, misma caché.

```xml
<LookupCache name="LC-Token">
  <CacheKey>
    <Prefix>token-backend</Prefix>
    <KeyFragment>core-bancario</KeyFragment>
  </CacheKey>
  <AssignTo>token.valor</AssignTo>
</LookupCache>
```

Después, en una AssignMessage, se usa `Bearer {token.valor}` en la cabecera `Authorization` hacia el backend.

### 2. Evitar callouts repetidos por cliente

```xml
<LookupCache name="LC-Perfil-Riesgo">
  <CacheKey>
    <Prefix>perfil-riesgo</Prefix>
    <KeyFragment ref="cliente.id"/>
  </CacheKey>
  <CacheResource>datos-clientes</CacheResource>
  <AssignTo>perfil.json.texto</AssignTo>
</LookupCache>
```

```xml
<Step>
  <Name>SC-Consultar-Riesgo</Name>
  <Condition>lookupcache.LC-Perfil-Riesgo.cachehit = false</Condition>
</Step>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Default de `<CacheLookupTimeoutInSeconds>` | `12` | `30` |
| `<Properties/>` en la plantilla | No aparece | Aparece en la sintaxis |
| Prefijo de `<Scope>` | Sin revisión en esta página | Incluye el número de revisión desplegada |
| Elementos, variables y errores | Iguales | Iguales |

## Antipatrones

- Decidir si hubo acierto comprobando si la variable de `<AssignTo>` existe, en vez de usar `cachehit`.
- Diferencias sutiles de clave con la PopulateCache (otro `<Scope>`, otra caché, fragmentos en otro orden).
- Usar la caché para valores que requieren consistencia fuerte entre message processors.

## Fuentes

- LookupCache policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/lookup-cache-policy> (consultada directamente, contenido completo, 2026-10-22).
- Lookup Cache policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/lookup-cache-policy> (consultada directamente, 2026-10-22).
