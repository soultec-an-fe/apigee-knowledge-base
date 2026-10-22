---
id: politica-response-cache
titulo: ResponseCache — referencia completa
area: politicas
tags: [responsecache, cache, rendimiento, latencia, cache-control, etag, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: ResponseCache
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/response-cache-policy
revisado: 2026-10-22
---

# ResponseCache — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<ResponseCache>`.
> **Aplica a:** Apigee X, hybrid y Edge, con un default distinto en `<ExcludeErrorResponse>` (ver [Diferencias en Apigee Edge](#diferencias-en-apigee-edge)).

ResponseCache guarda **la respuesta completa del backend** y la devuelve en peticiones posteriores con la misma clave, sin llamar al backend. Reduce latencia y carga cuando los datos cambian poco: catálogos, tipos de cambio publicados cada X minutos, configuraciones.

Una misma política se adjunta **dos veces**: en el flujo de petición (consulta la caché y, si hay acierto, corta el flujo y responde) y en el flujo de respuesta (guarda lo que devolvió el backend).

## Cuándo usarla (y cuándo no)

| Necesidad | Política correcta |
|---|---|
| Cachear la respuesta HTTP entera de un recurso | **ResponseCache** |
| Cachear un dato suelto (un token, un resultado de callout, un fragmento) | [PopulateCache](populate-cache.md) + [LookupCache](lookup-cache.md) |
| Borrar entradas antes de que venzan | [InvalidateCache](invalidate-cache.md) (para las de PopulateCache) o la API de cachés |
| Respuestas personalizadas por usuario | ResponseCache **solo** si la identidad del usuario forma parte de la clave; si no, no la uses |
| Respuestas semánticamente similares de un LLM | `SemanticCacheLookup` / `SemanticCachePopulate` |

## Restricciones de adjunto

- Solo puede adjuntarse **una vez en el flujo de petición y una vez en el de respuesta** de un proxy. Adjuntarla en más sitios hace fallar el despliegue (`ResponseCacheStepAttachmentNotAllowedReq` / `...Resp`).
- **No se puede usar en un shared flow** (X/hybrid).
- Lugar habitual: PreFlow de petición del ProxyEndpoint (después de autenticar y de las protecciones de tráfico) y PostFlow de respuesta del mismo endpoint, o del TargetEndpoint.

```xml
<!-- ProxyEndpoint -->
<PreFlow name="PreFlow">
  <Request>
    <Step><Name>VAK-Header</Name></Step>
    <Step><Name>RC-Catalogo</Name></Step>
  </Request>
</PreFlow>
<PostFlow name="PostFlow">
  <Response>
    <Step><Name>RC-Catalogo</Name></Step>
  </Response>
</PostFlow>
```

## Sintaxis completa

```xml
<ResponseCache name="RC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Properties/>
  <CacheKey>
    <Prefix>prefijo</Prefix>
    <KeyFragment ref="request.uri"/>
  </CacheKey>
  <Scope>Exclusive</Scope>
  <ExpirySettings>
    <ExpiryDate ref="variable.fecha">12-31-2026</ExpiryDate>
    <TimeOfDay ref="variable.hora">23:59:00</TimeOfDay>
    <TimeoutInSeconds ref="variable.segundos">300</TimeoutInSeconds>
  </ExpirySettings>
  <CacheResource>nombre_de_cache</CacheResource>
  <CacheLookupTimeoutInSeconds>30</CacheLookupTimeoutInSeconds>
  <ExcludeErrorResponse>true</ExcludeErrorResponse>
  <SkipCacheLookup>condicion</SkipCacheLookup>
  <SkipCachePopulation>condicion</SkipCachePopulation>
  <UseAcceptHeader>false</UseAcceptHeader>
  <UseResponseCacheHeaders>false</UseResponseCacheHeaders>
</ResponseCache>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; máximo 255 caracteres. Da nombre a las variables `responsecache.{name}.*`. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la política falle. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<CacheKey>` | **Sí** | — | — | Cómo se forma la clave. Ver [Claves de caché](claves-de-cache.md). |
| `<CacheKey>/<Prefix>` | No | String | — | Prefijo propio; anula `<Scope>`. |
| `<CacheKey>/<KeyFragment>` | No | String | — | Literal o `ref` a variable. Varios se concatenan con `__`. |
| `<Scope>` | No | String | `Exclusive` | `Global`, `Application`, `Proxy`, `Target` o `Exclusive`. |
| `<ExpirySettings>` | **Sí** | — | — | Cuándo vence la entrada. |
| `<CacheResource>` | No | String | caché compartida | Caché de entorno con nombre. |
| `<CacheLookupTimeoutInSeconds>` | No | Integer | `30` | Segundos tras los que una consulta sin respuesta cuenta como fallo de caché. |
| `<ExcludeErrorResponse>` | No | Boolean | `true` en X/hybrid; `false` en Edge | No guardar respuestas con códigos de error. |
| `<SkipCacheLookup>` | No | Condición | — | Si es verdadera, no consulta la caché y la refresca con la respuesta nueva. |
| `<SkipCachePopulation>` | No | Condición | — | Si es verdadera, no escribe en la caché. |
| `<UseAcceptHeader>` | No | Boolean | `false` | Añade las cabeceras `Accept*` de la petición a la clave. |
| `<UseResponseCacheHeaders>` | No | Boolean | `false` | Tiene en cuenta `Cache-Control` y `Expires` del backend al calcular el TTL. |

### `<CacheKey>`, `<Prefix>`, `<KeyFragment>` y `<Scope>`

Funcionan igual en las cuatro políticas de caché. Ver [Claves de caché, alcance y funcionamiento interno](claves-de-cache.md). Punto específico de ResponseCache: como la respuesta entera se reutiliza, **todo lo que haga variar la respuesta debe estar en la clave** (ruta, parámetros relevantes, idioma, identidad del cliente si la respuesta es personalizada).

### `<ExpirySettings>`

Obligatorio. Admite tres hijos, cada uno con literal y/o `ref`:

| Hijo | Formato | Nota |
|---|---|---|
| `<TimeoutInSeconds>` | Entero, segundos | Si está presente, **anula** a los otros dos. Da un literal de respaldo además de `ref`, por si la variable no tiene valor. |
| `<ExpiryDate>` | `mm-dd-yyyy` | Fecha de vencimiento. |
| `<TimeOfDay>` | `HH:mm:ss`, reloj de 24 h | Hora del día de vencimiento. |
| `<TimeoutInSec>` | — | **Obsoleto.** Si coexiste con `<TimeoutInSeconds>`, gana este último. |

> [!WARNING]
> **Zona horaria de `<TimeOfDay>`.** La página de ResponseCache dice que la zona y el locale "dependen de dónde se ejecute el código" y no se pueden conocer al configurar; la de PopulateCache dice que es **UTC**. Para no depender de esto, prefiere `<TimeoutInSeconds>` o calcula los segundos hasta la hora deseada en una variable.

### `<CacheLookupTimeoutInSeconds>`

Si la consulta a la caché tarda más de este tiempo, se trata como fallo de caché y la petición sigue hacia el backend. Default `30` en ResponseCache (en LookupCache de X es `12`). Un valor negativo hace fallar el despliegue con `InvalidTimeout`.

### `<ExcludeErrorResponse>`

ResponseCache puede guardar respuestas de **cualquier** código de estado. Con `true`, solo guarda **200 a 205**, que son los únicos códigos que Apigee considera de éxito para este fin; un `3xx`, `4xx` o `5xx` no se cachea. Con `false` se guarda lo que venga, incluidos errores.

> [!IMPORTANT]
> En Edge el default es `false`: si migras de Edge a X sin declararlo, el comportamiento cambia (en X deja de cachear errores). Declara siempre el valor que quieres.

### `<SkipCacheLookup>` y `<SkipCachePopulation>`

Contienen una **condición** (misma sintaxis que `<Condition>`). Una condición mal formada hace fallar el despliegue con `InvalidMessagePatternForErrorCode`.

| Elemento | Se evalúa en | Si es verdadera |
|---|---|---|
| `<SkipCacheLookup>` | Petición | No consulta la caché; la petición va al backend y su respuesta **refresca** la entrada. |
| `<SkipCachePopulation>` | Respuesta | No escribe la respuesta en la caché. |

Usos típicos: `request.verb != "GET"` en ambos (no cachear escrituras), `response.status.code >= 400` en `<SkipCachePopulation>` si `<ExcludeErrorResponse>` no basta.

> [!WARNING]
> Un `<SkipCacheLookup>` controlado por una cabecera del cliente (p. ej. `request.header.bypass-cache = "true"`) permite a cualquier cliente forzar llamadas al backend. Si lo usas, restríngelo a clientes internos (comprueba también la identidad de la app o la IP de origen).

### `<UseAcceptHeader>`

Con `true`, Apigee añade a la clave los valores de `Accept`, `Accept-Encoding`, `Accept-Language` y `Accept-Charset` de la petición. Evita, por ejemplo, devolver una respuesta comprimida con gzip a un cliente que no la pidió, o una respuesta en inglés a quien pidió español.

### `<UseResponseCacheHeaders>`

Con `true`, Apigee lee las cabeceras de caché de la respuesta del backend, las compara con `<ExpirySettings>` y usa el **menor** de los TTL. Entre cabeceras, la prioridad es:

1. `Cache-Control: s-maxage`
2. `Cache-Control: max-age`
3. `Expires`

Ejemplo: sin `s-maxage`, `max-age=300`, `Expires` dentro de tres días y `<TimeoutInSeconds>600</TimeoutInSeconds>` → TTL de 300 s.

## Soporte de cabeceras HTTP de caché

Apigee implementa solo una parte de la semántica de caché HTTP/1.1, y **solo sobre las respuestas del backend** (ignora `Cache-Control` de las peticiones del cliente). Solo modela cachés **públicas** (compartidas).

| Directiva / cabecera de la respuesta | Comportamiento |
|---|---|
| `s-maxage`, `max-age` | Usadas para el TTL si `<UseResponseCacheHeaders>` es `true`. El contenido conserva el valor original, así que puede llegar al cliente más viejo de lo que su `max-age` sugiere. |
| `no-cache` (y `Pragma: no-cache`) | Se cachea, pero debe revalidarse con el backend antes de usarse; un `304` del backend hace servir lo cacheado. |
| `private` | La respuesta **no** se cachea. |
| `public` | Se cachea aunque otras directivas digan lo contrario, salvo que la respuesta lleve `Authorization`. |
| `no-store`, `no-transform`, `must-revalidate`, `proxy-revalidate`, extensiones | **No soportadas.** Ojo con `no-store`: el backend puede pedir "no guardar" y Apigee no lo respeta por sí solo. |
| `Expires` | Usada para el TTL (por debajo de `max-age`/`s-maxage`). Un valor a más de un año se respeta tal cual, no como "nunca vence". |
| `ETag` con `If-Match` / `If-None-Match` | Apigee guarda el ETag; en GET compara ETags fuertes y puede responder `304` sin ir al backend. Las peticiones que no son GET pasan al backend. |
| `If-Modified-Since` | En GET se pasa **siempre** al backend aunque haya entrada válida. |
| `Accept-Encoding` | Apigee puede servir versión comprimida o sin comprimir de la misma entrada según la petición. |

> [!TIP]
> Si el backend marca respuestas con `Cache-Control: no-store` o `private` por motivos de privacidad y quieres respetarlo de forma explícita, añade `<SkipCachePopulation>` con una condición sobre `response.header.Cache-Control`.

## Variables de flujo

| Variable | Tipo | Acceso | Contenido |
|---|---|---|---|
| `responsecache.{name}.cachename` | String | Lectura | Caché usada. |
| `responsecache.{name}.cachekey` | String | Lectura | Clave calculada. Útil en Debug para comprobar la composición real. |
| `responsecache.{name}.cachehit` | Boolean | Lectura | `true` si la respuesta salió de la caché. |
| `responsecache.{name}.invalidentry` | Boolean | Lectura | `true` si la entrada no es válida. |

## Errores

### En runtime

La política **no lanza errores en runtime**: un fallo de caché simplemente deja pasar la petición al backend. No hay variables de fallo propias.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidTimeout` | `<CacheLookupTimeoutInSeconds>` negativo. |
| `InvalidCacheResourceReference` | `<CacheResource>` nombra una caché que no existe en el entorno. |
| `ResponseCacheStepAttachmentNotAllowedReq` | La misma política está adjunta en más de un punto del flujo de petición. |
| `ResponseCacheStepAttachmentNotAllowedResp` | La misma política está adjunta en más de un punto del flujo de respuesta. |
| `InvalidMessagePatternForErrorCode` | Condición inválida en `<SkipCacheLookup>` o `<SkipCachePopulation>`. |
| `CacheNotFound` | La caché indicada no se ha creado en un message processor concreto. |

## Ejemplos

### 1. Catálogo público, 10 minutos, solo GET

```xml
<ResponseCache name="RC-Catalogo">
  <CacheKey>
    <Prefix>catalogo</Prefix>
    <KeyFragment ref="request.path"/>
    <KeyFragment ref="request.queryparam.categoria"/>
    <KeyFragment ref="request.queryparam.pagina"/>
  </CacheKey>
  <ExpirySettings>
    <TimeoutInSeconds>600</TimeoutInSeconds>
  </ExpirySettings>
  <ExcludeErrorResponse>true</ExcludeErrorResponse>
  <SkipCacheLookup>request.verb != "GET"</SkipCacheLookup>
  <SkipCachePopulation>request.verb != "GET"</SkipCachePopulation>
  <UseAcceptHeader>true</UseAcceptHeader>
</ResponseCache>
```

### 2. Respuesta por cliente: la identidad va en la clave

Datos de cuenta que cambian poco pero son distintos para cada app. Sin el `client_id` en la clave, una app vería los datos de otra.

```xml
<ResponseCache name="RC-Cuenta">
  <CacheKey>
    <Prefix>cuenta</Prefix>
    <KeyFragment ref="client_id"/>
    <KeyFragment ref="request.path"/>
  </CacheKey>
  <ExpirySettings>
    <TimeoutInSeconds>60</TimeoutInSeconds>
  </ExpirySettings>
  <ExcludeErrorResponse>true</ExcludeErrorResponse>
  <SkipCacheLookup>request.verb != "GET"</SkipCacheLookup>
  <SkipCachePopulation>request.verb != "GET"</SkipCachePopulation>
</ResponseCache>
```

### 3. TTL dictado por el backend, con techo de 1 hora

El backend publica `Cache-Control: max-age`. Apigee usa ese valor salvo que supere 3600 s, y no guarda nada marcado `private`.

```xml
<ResponseCache name="RC-Tasas">
  <CacheKey>
    <KeyFragment ref="request.uri"/>
  </CacheKey>
  <ExpirySettings>
    <TimeoutInSeconds>3600</TimeoutInSeconds>
  </ExpirySettings>
  <UseResponseCacheHeaders>true</UseResponseCacheHeaders>
  <ExcludeErrorResponse>true</ExcludeErrorResponse>
  <SkipCachePopulation>response.header.Cache-Control ~~ ".*(private|no-store).*"</SkipCachePopulation>
</ResponseCache>
```

### 4. Refresco forzado solo para un job interno

Un proceso interno con su propia app (`client_id` conocido) puede saltarse la caché para refrescarla; los clientes externos no.

```xml
<ResponseCache name="RC-Refrescable">
  <CacheKey>
    <Prefix>config</Prefix>
    <KeyFragment ref="request.path"/>
  </CacheKey>
  <ExpirySettings>
    <TimeoutInSeconds>1800</TimeoutInSeconds>
  </ExpirySettings>
  <SkipCacheLookup>request.header.x-refrescar = "true" and client_id = "id-de-la-app-interna"</SkipCacheLookup>
</ResponseCache>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Default de `<ExcludeErrorResponse>` | `true` | `false` (Google anunció que cambiaría a `true` en una versión futura sin fecha) |
| Prefijo de `<Scope>` | Sin revisión en esta página (ver [discrepancia](claves-de-cache.md#scope-el-prefijo-automático)) | Incluye el número de revisión desplegada |
| Uso en shared flows | No permitido | La página de Edge no lo menciona |
| Cifrado de la caché | Siempre (hybrid ≥ 1.4) | Solo en organizaciones PCI o HIPAA de Edge Public Cloud |
| Gestión administrativa | API de cachés (listar y borrar) | API de gestión de cachés de Edge |
| Elementos, variables y errores | Iguales | Iguales |

## Antipatrones

- Cachear respuestas personalizadas sin la identidad del cliente en la clave (fuga de datos entre clientes).
- Dejar `<ExcludeErrorResponse>` sin declarar al migrar de Edge.
- Usar ResponseCache para respuestas de escrituras (`POST`, `PUT`, `DELETE`).
- Confiar en que Apigee respeta `Cache-Control: no-store` del backend.
- `<SkipCacheLookup>` controlado libremente por una cabecera del cliente.
- Usar `request.querystring` como único fragmento cuando el orden de parámetros varía.

Ver también el [catálogo de antipatrones](../../09-antipatrones/01-catalogo-antipatrones.md).

## Fuentes

- ResponseCache policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy> (consultada directamente, contenido completo, 2026-10-22). La página anuncia una tabla de prioridad de cabeceras que no incluye; la prioridad se tomó de la guía de cabeceras HTTP.
- Response Cache policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/response-cache-policy> (consultada directamente, 2026-10-22).
- Support for HTTP response headers — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/cache/http-response-caching> (consultada directamente, 2026-10-22).
- Cache internals: <https://docs.cloud.google.com/apigee/docs/api-platform/cache/cache-internals>
