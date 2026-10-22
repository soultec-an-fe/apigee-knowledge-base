---
id: politica-populate-cache
titulo: PopulateCache — referencia completa
area: politicas
tags: [populatecache, cache, lookupcache, token, rendimiento, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: PopulateCache
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/populate-cache-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/populate-cache-policy
revisado: 2026-10-22
---

# PopulateCache — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<PopulateCache>`.
> **Aplica a:** Apigee X, hybrid y Edge.

PopulateCache **escribe el valor de una variable** en la caché bajo una clave. Es la mitad de escritura de la caché de propósito general; se usa con [LookupCache](lookup-cache.md), que lee, y con [InvalidateCache](invalidate-cache.md), que borra. Para cachear respuestas HTTP completas está [ResponseCache](response-cache.md).

Caso típico: un proxy necesita un token del backend que dura 1 hora. Se consulta la caché con LookupCache; si no hay acierto, se obtiene el token con ServiceCallout y se guarda con PopulateCache con un TTL algo menor que su vida real.

## Sintaxis completa

```xml
<PopulateCache name="PC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Properties/>
  <CacheKey>
    <Prefix>prefijo</Prefix>
    <KeyFragment ref="variable"/>
    <KeyFragment>literal</KeyFragment>
  </CacheKey>
  <CacheResource>nombre_de_cache</CacheResource>
  <Scope>Exclusive</Scope>
  <ExpirySettings>
    <TimeoutInSeconds ref="variable.segundos">300</TimeoutInSeconds>
  </ExpirySettings>
  <Source>variable.con.el.valor</Source>
</PopulateCache>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; máximo 255 caracteres. |
| `continueOnError` | No | `false` | Con `true`, el flujo sigue aunque la política falle. Con caché suele convenir: un fallo al guardar no debería tumbar la petición. |
| `enabled` | No | `true` | Con `false` la política no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

| Elemento | Obligatorio | Tipo | Default | Resumen |
|---|---|---|---|---|
| `<DisplayName>` | No | String | `name` | Etiqueta en la UI. |
| `<CacheKey>` | **Sí** | — | — | Clave. Ver [Claves de caché](claves-de-cache.md). |
| `<CacheKey>/<Prefix>` | No | String | — | Prefijo fijo; anula `<Scope>`. |
| `<CacheKey>/<KeyFragment>` | No (cero o más) | String | — | Literal o `ref`. |
| `<CacheResource>` | No | String | caché compartida | Caché de entorno con nombre. |
| `<Scope>` | No | String | `Exclusive` | Prefijo automático si no hay `<Prefix>`. |
| `<ExpirySettings>` | **Sí** | — | — | Cuándo vence la entrada. Un solo hijo. |
| `<Source>` | **Sí** | String | — | Variable cuyo valor se guarda. |

### `<CacheKey>`, `<Scope>` y `<CacheResource>`

Ver [Claves de caché, alcance y funcionamiento interno](claves-de-cache.md). Lo esencial: **la LookupCache que lea esta entrada debe tener `<CacheKey>`, `<Scope>`/`<Prefix>` y `<CacheResource>` idénticos.**

### `<ExpirySettings>`

Usa **exactamente un** hijo. Cada uno admite literal y `ref`; si `ref` apunta a una variable que no está definida, se usa el literal.

| Hijo | Formato | Comportamiento |
|---|---|---|
| `<TimeoutInSeconds>` | Entero, segundos | TTL relativo. Reemplaza al obsoleto `<TimeoutInSec>`. |
| `<ExpiryDate>` | `mm-dd-yyyy` | Vence ese día. Si la fecha ya pasó, se aplica el TTL máximo: **30 días**. |
| `<TimeOfDay>` | `HH:mm:ss`, 24 h, **UTC** (notación ISO 8601) | Vence a esa hora. |

Si se declara más de uno, la precedencia es `TimeoutInSeconds` > `ExpiryDate` > `TimeOfDay`.

> [!WARNING]
> La página de ResponseCache describe la zona horaria de `<TimeOfDay>` como dependiente del entorno de ejecución, mientras que esta página dice UTC. Si la hora exacta importa, usa `<TimeoutInSeconds>` con un valor calculado.

### `<Source>`

Nombre de la variable cuyo valor se escribe. Si el valor no es serializable, la política falla con `EntryCannotBeCached`.

> [!IMPORTANT]
> Según la página de X/hybrid, **los objetos JSON se guardan solo en la caché en memoria (L1)**, que dura alrededor de un segundo. Para que el valor llegue a la caché persistente (L2) y lo vean los demás message processors, guárdalo como **string**, por ejemplo con `JSON.stringify` en una política JavaScript, o asignando el contenido textual de un mensaje.

## Variables de flujo

La página oficial no documenta variables propias de PopulateCache. Para comprobar la clave real, coloca después una LookupCache con la misma configuración y mira `lookupcache.{name}.cachekey` en Debug.

## Errores

### En runtime

| Código de fallo | HTTP | Causa |
|---|---|---|
| `policies.populatecache.EntryCannotBeCached` | 500 | El objeto de `<Source>` no es serializable. |

El `errorcode` que llega en la respuesta de error usa el prefijo `steps.populatecache.EntryCannotBeCached`.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidCacheResourceReference` | `<CacheResource>` nombra una caché que no existe en el entorno. |
| `CacheNotFound` | La caché indicada no existe. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "EntryCannotBeCached"` |
| `populatecache.{name}.failed` | `populatecache.PC-Token.failed = true` |

## Ejemplos

### 1. Token del backend con TTL tomado de la respuesta

Flujo completo, en el PreFlow de petición del TargetEndpoint: busca el token; si no está, lo pide y lo guarda. La política `JS-Calcular-TTL` deja en `token.ttl` el `expires_in` del backend menos 60 segundos, y `EV-Token` deja el token en `token.valor`.

```xml
<Step><Name>LC-Token</Name></Step>
<Step>
  <Name>SC-Pedir-Token</Name>
  <Condition>lookupcache.LC-Token.cachehit = false</Condition>
</Step>
<Step>
  <Name>EV-Token</Name>
  <Condition>lookupcache.LC-Token.cachehit = false</Condition>
</Step>
<Step>
  <Name>JS-Calcular-TTL</Name>
  <Condition>lookupcache.LC-Token.cachehit = false</Condition>
</Step>
<Step>
  <Name>PC-Token</Name>
  <Condition>lookupcache.LC-Token.cachehit = false</Condition>
</Step>
```

```xml
<PopulateCache name="PC-Token" continueOnError="true">
  <CacheKey>
    <Prefix>token-backend</Prefix>
    <KeyFragment>core-bancario</KeyFragment>
  </CacheKey>
  <ExpirySettings>
    <TimeoutInSeconds ref="token.ttl">3000</TimeoutInSeconds>
  </ExpirySettings>
  <Source>token.valor</Source>
</PopulateCache>
```

La LookupCache correspondiente está en [LookupCache — ejemplo 1](lookup-cache.md#1-leer-el-token-guardado-por-populatecache).

### 2. Resultado de un callout por cliente, compartido entre proxies

Dos proxies distintos necesitan el perfil de riesgo de un cliente. Con un `<Prefix>` propio, ambos leen y escriben las mismas entradas, sin depender del nombre del proxy.

```xml
<PopulateCache name="PC-Perfil-Riesgo">
  <CacheKey>
    <Prefix>perfil-riesgo</Prefix>
    <KeyFragment ref="cliente.id"/>
  </CacheKey>
  <CacheResource>datos-clientes</CacheResource>
  <ExpirySettings>
    <TimeoutInSeconds>900</TimeoutInSeconds>
  </ExpirySettings>
  <Source>perfil.json.texto</Source>
</PopulateCache>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Objetos JSON solo en L1 | Documentado | No mencionado |
| Prefijo de `<Scope>` | Sin revisión en esta página | Incluye el número de revisión desplegada |
| Cifrado | Siempre (hybrid ≥ 1.4) | Solo organizaciones PCI o HIPAA de Edge Public Cloud |
| Elementos y errores | Iguales | Iguales |

## Antipatrones

- Guardar credenciales o datos personales en una caché `Global` o con `<Prefix>` compartido sin necesidad.
- TTL igual o mayor que la vida real del dato (el token vence en la caché antes de que la entrada expire).
- Guardar objetos en vez de strings y esperar que estén disponibles en todos los message processors.
- Configurar la clave distinta en PopulateCache y LookupCache.
- Usar la caché como almacén persistente: para datos de configuración que deben sobrevivir, usa KVM o PropertySet.

## Fuentes

- PopulateCache policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/populate-cache-policy> (consultada directamente, contenido completo, 2026-10-22).
- Populate Cache policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/populate-cache-policy> (consultada directamente, 2026-10-22).
- Cache internals: <https://docs.cloud.google.com/apigee/docs/api-platform/cache/cache-internals>
