---
id: referencia-claves-de-cache
titulo: Claves de caché, alcance y funcionamiento interno
area: politicas
tags: [cache, cachekey, scope, prefix, keyfragment, l1, l2, responsecache, populatecache, lookupcache, invalidatecache]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/working-cachekeys
revisado: 2026-10-22
---

# Claves de caché, alcance y funcionamiento interno

> [!NOTE]
> Este documento es común a las cuatro políticas de caché: [ResponseCache](response-cache.md), [PopulateCache](populate-cache.md), [LookupCache](lookup-cache.md) e [InvalidateCache](invalidate-cache.md). Todas construyen la clave igual, así que la explicación vive aquí una sola vez.

## Cómo se forma la clave

Cada entrada de caché se guarda bajo una clave de texto con dos partes unidas por **doble guion bajo** (`__`):

```text
PARTE_PREFIJO__FRAGMENTO1__FRAGMENTO2__...
```

| Parte | Sale de | Notas |
|---|---|---|
| Prefijo | `<CacheKey>/<Prefix>` si existe; si no, el valor de `<Scope>` | `<Prefix>` **anula** `<Scope>` por completo. |
| Fragmentos | Cada `<CacheKey>/<KeyFragment>`, en el orden en que aparecen | Literales o variables (`ref`). Se concatenan con `__`. |
| Sufijo (solo ResponseCache) | Cabeceras `Accept*` de la petición | Solo con `<UseAcceptHeader>true</UseAcceptHeader>`. |

```xml
<CacheKey>
  <Prefix>clientes</Prefix>
  <KeyFragment>perfil</KeyFragment>
  <KeyFragment ref="request.header.x-cliente-id"/>
</CacheKey>
```

Con `x-cliente-id: 42`, la clave es `clientes__perfil__42`.

Reglas que se derivan:

- **PopulateCache y LookupCache deben tener `<CacheKey>`, `<Scope>`/`<Prefix>` y `<CacheResource>` idénticos.** Si difieren en cualquier cosa, la consulta nunca encuentra lo que se guardó. ResponseCache no tiene este problema porque una sola configuración sirve para leer y escribir.
- Un `<KeyFragment>` lleva **o** un literal **o** `ref`, no ambos.
- El orden de los fragmentos importa: `a__b` y `b__a` son claves distintas.
- Solo entra en la clave lo que se referencia explícitamente. Si la respuesta depende de un parámetro que no está en un `<KeyFragment>`, dos peticiones distintas compartirán entrada.
- `request.querystring` mete la query completa en la clave, pero sensible al orden: `a=1&b=2` y `b=2&a=1` producen claves distintas. Es preferible referenciar cada `request.queryparam.{nombre}` por separado.
- Límite de tamaño de la clave en ResponseCache: 2 KB. Ver [Límites](../../10-referencia/01-limites.md) para el resto.

## `<Scope>`: el prefijo automático

Cuando no hay `<Prefix>`, `<Scope>` genera el prefijo a partir del contexto de despliegue. Va de más amplio a más estrecho:

| Valor | Prefijo que genera | Quién comparte las entradas |
|---|---|---|
| `Global` | `org__entorno__` | Todos los proxies del entorno. |
| `Application` | `org__entorno__proxy__` | Todos los endpoints de un mismo proxy. |
| `Proxy` | `org__entorno__proxy__proxyEndpoint__` | Un ProxyEndpoint concreto. |
| `Target` | `org__entorno__proxy__targetEndpoint__` | Un TargetEndpoint concreto. |
| `Exclusive` (**default**) | `org__entorno__proxy__endpoint__`, donde `endpoint` es el ProxyEndpoint o el TargetEndpoint en el que está adjunta la política | Solo esa política en ese endpoint. |

> [!WARNING]
> **Discrepancia en la documentación oficial sobre la revisión.** La guía de claves de caché de X/hybrid dice que el prefijo `Exclusive` incluye el **número de revisión desplegada** (ejemplo: `mycompany__prod__weatherapi__16__default__hello__world`), pero las páginas de referencia de ResponseCache, PopulateCache, LookupCache e InvalidateCache de X muestran el prefijo **sin** revisión. En Edge, todas las páginas incluyen la revisión. Consecuencia práctica si la revisión forma parte de la clave: **al desplegar una revisión nueva la caché arranca vacía** y lo guardado por la revisión anterior deja de encontrarse. Si necesitas que la caché sobreviva a despliegues, usa `<Prefix>` propio y no dependas de `<Scope>`. Comprueba el comportamiento real en tu organización mirando la variable `{politica}.cachekey` en Debug.

Usa `<Prefix>` cuando:

- varias políticas o proxies deben compartir las mismas entradas (p. ej. un proxy guarda un token y otro lo lee);
- quieres invalidar un grupo de entradas de una vez con `InvalidateCache` + `<PurgeChildEntries>`;
- quieres una clave estable que no dependa de nombres de endpoint ni de revisiones.

## Caché compartida vs caché de entorno

| Opción | Cómo se elige | Cuándo |
|---|---|---|
| Caché compartida incluida | Se omite `<CacheResource>` | La mayoría de los casos. |
| Caché de entorno con nombre | `<CacheResource>nombre</CacheResource>` | Cuando quieres poder **vaciarla administrativamente** con la API de cachés, o separar dominios de datos. |

Si `<CacheResource>` nombra una caché que no existe en el entorno, el despliegue falla con `InvalidCacheResourceReference`. En X/hybrid, la gestión de cachés por API se limita a **listar y borrar**.

## Funcionamiento interno: L1 y L2

Las cuatro políticas usan el mismo almacén de dos niveles:

| Nivel | Dónde | Vida | Compartido |
|---|---|---|---|
| **L1** en memoria | Cada message processor | ~1 segundo; se desaloja por LRU si falta memoria | No: cada MP tiene la suya |
| **L2** persistente | Base de datos (Cassandra) | Hasta que vence el TTL o se invalida | Sí: entre todos los MPs del entorno, incluso de otras regiones |

Flujo de cada operación:

- **Escritura** (PopulateCache, ResponseCache): se escribe en la L1 del MP que atendió la petición y en L2.
- **Lectura** (LookupCache, ResponseCache): primero L1 del MP actual, luego L2. Si no está en ninguna, LookupCache no asigna nada y ResponseCache deja pasar la petición al backend y guarda la respuesta.
- **Invalidación o actualización** (InvalidateCache, PopulateCache, ResponseCache): el MP que recibe la petición borra la entrada de su L1 y de L2. **Otros MPs pueden servir el valor viejo desde su L1 durante hasta un segundo.** No hay evento de borrado distribuido: se confía en el vencimiento de L1.

> [!IMPORTANT]
> La caché es **eventualmente consistente** en ventanas de un segundo. No la uses para nada que requiera consistencia fuerte (saldos, contadores de seguridad, bloqueo de credenciales revocadas en el mismo instante).

Otros datos operativos:

- Tamaño máximo por objeto cacheado: **256 KB** (indicado en la página de ResponseCache). Ver [Límites](../../10-referencia/01-limites.md).
- Expiración máxima: 30 días (PopulateCache aplica ese máximo cuando `<ExpiryDate>` está en el pasado).
- **Cifrado:** en Apigee X y hybrid ≥ 1.4, la caché y los KVM se cifran siempre (L2 con AES-256). En Edge Public Cloud solo se cifra en organizaciones habilitadas para PCI o HIPAA, configurado al aprovisionar la organización.
- **Objetos JSON** (no texto) solo se guardan en L1 según la página de PopulateCache de X. Para que lleguen a L2, serialízalos a string antes de cachearlos.

## Fuentes

- Working with cache keys — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/working-cachekeys> (consultada directamente, contenido completo, 2026-10-22).
- Working with cache keys — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/working-cachekeys> (consultada directamente, 2026-10-22).
- Cache internals — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/cache/cache-internals> (consultada directamente, 2026-10-22).
- Páginas de referencia de las cuatro políticas de caché, X/hybrid y Edge (ver cada archivo).
