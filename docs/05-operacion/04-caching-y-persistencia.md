---
id: operacion-caching
titulo: Caching y persistencia
area: operacion
tags: [cache, responsecache, kvm, propertyset, cassandra, ttl]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/cache/general-purpose-caching
revisado: 2026-08-20
---

# Caching y persistencia

## Los cuatro mecanismos

| Mecanismo | Persistencia | Coste de lectura | Uso correcto |
|---|---|---|---|
| **ResponseCache** | Caché (TTL) | Bajo | Cachear respuestas HTTP completas |
| **LookupCache / PopulateCache** | Caché (TTL) | Bajo | Valores arbitrarios: tokens, resultados de callouts |
| **KeyValueMap (KVM)** | Cassandra | **Alto** sin caché en memoria | Configuración por entorno, secretos |
| **PropertySet** | En el bundle | **Cero** | Configuración estática versionada en Git |

> [!IMPORTANT]
> Ninguno de los cuatro es una base de datos. Google es explícito sobre los KVM:
> **úsalos solo para conjuntos de datos limitados; no están diseñados para almacenamiento a largo plazo**, y el impacto en rendimiento es real porque viven en Cassandra.

---

## ResponseCache

Ver la [configuración completa y las reglas de oro](../02-politicas/01-traffic-management.md#responsecache). Resumen operativo:

### Las siete reglas

1. **Nunca caches respuestas no exitosas ni métodos no-GET:**
   ```xml
   <SkipCachePopulation>response.status.code != 200 or request.verb != "GET"</SkipCachePopulation>
   ```
   Cachear un 500 propaga el fallo del backend a todos los clientes durante todo el TTL. Es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md).

2. **La cache key debe ser suficiente.** `request.querystring` suele ser el identificador único adecuado. Si olvidas un fragmento, sirves la respuesta de un cliente a otro.

3. **No incluyas la API key en la cache key** salvo que la respuesta sea realmente distinta por cliente: multiplica las entradas y destruye el hit rate.

4. **Un solo content-type por caché.** Convierte antes de cachear si es necesario.

5. **Lookup en el PreFlow del ProxyEndpoint, populate en el PostFlow del response.** Lookup lo más cerca del cliente para cortocircuitar antes; populate al final para cachear el resultado ya mediado.

6. **La respuesta de CORS no debe cachearse.** Advertencia explícita de Google.

7. **Varias políticas de caché en un proxy** → condiciones mutuamente excluyentes y **recursos de caché distintos**.

### Diseño de la cache key

```xml
<CacheKey>
    <Prefix>catalogo-v1</Prefix>
    <KeyFragment ref="proxy.pathsuffix" type="string"/>
    <KeyFragment ref="request.querystring" type="string"/>
    <KeyFragment ref="request.header.accept-language" type="string"/>
</CacheKey>
```

Pregúntate: **¿qué dos peticiones deben recibir exactamente la misma respuesta?** Todo lo que las diferencia debe estar en la clave; nada más.

| Incluir en la clave | No incluir |
|---|---|
| Ruta y query params | `client_id` (salvo respuestas personalizadas) |
| `Accept-Language` si sirves i18n | `User-Agent` |
| `Accept` si negocias formato | Timestamps, `messageid` |
| Tenant, si el contenido difiere | Cabeceras de trazado |

### Scope

| Valor | Ámbito |
|---|---|
| `Global` | Todos los proxies del entorno |
| `Application` | El proxy actual |
| `Proxy` | El ProxyEndpoint actual |
| `Target` | El TargetEndpoint actual |
| `Exclusive` | Proxy + endpoint. **Por defecto** |

Usa `Global` cuando varios proxies comparten datos (por ejemplo un token de backend común). Usa `Exclusive` en el resto.

---

## Caché de propósito general

Patrón *lookup-or-fetch* completo en [recetas XML](../02-politicas/06-recetas-xml.md#4-token-del-backend-cacheado-patrón-lookup-or-fetch).

```xml
<PreFlow name="PreFlow">
  <Request>
    <Step><Name>LC-Valor</Name></Step>
    <Step><Name>SC-Obtener</Name><Condition>dato.valor is null</Condition></Step>
    <Step><Name>PC-Valor</Name><Condition>dato.valor is null</Condition></Step>
    <Step><Name>AM-Usar</Name></Step>
  </Request>
</PreFlow>
```

### Elegir el TTL

| Dato | TTL orientativo | Criterio |
|---|---|---|
| Token OAuth del backend | `expires_in` − 60 s | Margen antes de la expiración real |
| Catálogo de productos | 5–60 min | Tolerancia del negocio a datos desactualizados |
| Configuración de feature flags | 5 min | Compromiso entre reactividad y carga |
| Datos de referencia (países, monedas) | 24 h | Cambian muy raramente |
| Cualquier dato de un usuario concreto | **No cachear** | Riesgo de servirlo a otro usuario |

---

## Límites de caché

| Límite | Valor |
|---|---|
| Cachés con scope de entorno | 100 |
| Tamaño de la clave | **2 KB** |
| Tamaño del valor | **256 KB** |
| Expiración | ≥ 1 segundo, ≤ **30 días** |
| Elementos por caché | 10 millones |

> [!CAUTION]
> **Antipatrón documentado: almacenar datos mayores de 256 KB en caché.**
> Para objetos grandes, cachea una **referencia** (una URL firmada de Cloud Storage, un identificador), no el objeto.

---

## KeyValueMap

### Cuándo usarlo

| Usa KVM para | No uses KVM para |
|---|---|
| Secretos (credenciales del backend, claves de firma) | Datos de usuario final |
| Configuración que cambia sin redesplegar | Estado de sesión |
| Listas de permitidos por entorno | Colas o contadores |
| Mapeos de tenant → backend | Cualquier cosa con crecimiento ilimitado |

### Uso correcto

```xml
<KeyValueMapOperations continueOnError="false" enabled="true"
                       name="KVM-Config" mapIdentifier="config-backends">
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>300</ExpiryTimeInSecs>
    <Get assignTo="private.api_key_backend" index="1">
        <Key><Parameter>backend_api_key</Parameter></Key>
    </Get>
</KeyValueMapOperations>
```

> [!IMPORTANT]
> **`<ExpiryTimeInSecs>` no es opcional.** Sin él, cada petición hace una lectura a Cassandra. Con él, el valor se cachea en memoria durante ese tiempo. La diferencia en latencia bajo carga es sustancial.

> [!TIP]
> Usa el prefijo `private.` en `assignTo` para secretos: no aparecen en las sesiones de Trace.

### Claves compuestas

```xml
<Get assignTo="config.backend_url" index="1">
    <Key>
        <Parameter ref="apiproduct.name"/>
        <Parameter>backend_url</Parameter>
    </Key>
</Get>
```

Produce la clave `producto-premium__backend_url`. Patrón útil para configuración por tenant o por producto.

### Límites de KVM

| Límite | Valor |
|---|---|
| Entradas totales por organización | **5 millones** |
| KVMs con scope de organización | 100 |
| KVMs con scope de entorno | **900** |
| Tamaño de la clave | 2 KB |
| Tamaño del valor | **10 KB** |

En Apigee X los KVM están **cifrados por defecto**.

### Gestión

```bash
# Crear un KVM cifrado con scope de entorno
apigeecli kvms create --name config-backends \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"

# Escribir una entrada
apigeecli kvms entries create --map config-backends \
  --key backend_api_key --value "$SECRETO" \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"
```

> [!WARNING]
> Los valores escritos en un KVM cifrado **no se pueden leer de vuelta** por la API de gestión. Es intencionado. Guarda el valor original en tu gestor de secretos: si lo pierdes, hay que rotarlo.

---

## PropertySet

Configuración estática que viaja **dentro del bundle** y se versiona en Git. Coste de lectura **cero**: no toca Cassandra.

`apiproxy/resources/properties/config.properties`:

```properties
timeout_backend=30000
version_api=v1
feature_nuevo_flujo=true
paginacion_default=20
```

Acceso directo como variable, sin política:

```
propertyset.config.timeout_backend
propertyset.config.version_api
propertyset.config.feature_nuevo_flujo
```

```xml
<Condition>propertyset.config.feature_nuevo_flujo = "true"</Condition>
```

### KVM vs PropertySet

| | PropertySet | KVM |
|---|---|---|
| Ubicación | En el bundle | Cassandra |
| Coste de lectura | Cero | Alto sin caché |
| Cambiar un valor | Requiere **redespliegue** | Inmediato |
| Distinto por entorno | ❌ No (el bundle es el mismo) | ✅ Sí |
| Apto para secretos | ❌ **Nunca** (va en Git) | ✅ Sí (cifrado) |
| Versionado en Git | ✅ Sí | Manual |
| Auditoría de cambios | Historial de Git | API de gestión |

Regla práctica:

```
¿Es un secreto?                     → KVM
¿Cambia por entorno?                → KVM
¿Debe cambiarse sin redesplegar?    → KVM
En cualquier otro caso              → PropertySet
```

---

## Estrategia de caché por capas

```
1. Cliente          Cache-Control / ETag        (lo más barato)
2. CDN              Cloud CDN sobre el LB
3. Apigee           ResponseCache               (evita la llamada al backend)
4. Apigee           LookupCache                 (tokens, datos auxiliares)
5. Backend          su propia caché
```

Cada capa que aciertas es una capa de coste y latencia que te ahorras. La disciplina de invalidación crece con cada capa: define desde el principio **cómo se invalida** cada nivel antes de añadirlo.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/cache/general-purpose-caching>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/response-cache-policy>
- <https://cloud.google.com/apigee/docs/api-platform/cache/creating-and-editing-environment-keyvalue-maps>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
