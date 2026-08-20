---
id: referencia-limites
titulo: Límites de la plataforma
area: referencia
tags: [limites, cuotas, quotas, restricciones, dimensionamiento]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/limits
revisado: 2026-08-20
---

# Límites de la plataforma

> [!IMPORTANT]
> Estos límites cambian. **Verifica siempre en <https://cloud.google.com/apigee/docs/api-platform/reference/limits> antes de dimensionar una arquitectura sobre ellos.** Algunos son ajustables mediante ticket de soporte; la mayoría no.

## API proxies y despliegue

| Límite | Valor |
|---|---|
| Tamaño del bundle de proxy | **15 MB** |
| Tamaño de un archivo de recurso | 15 MB |
| Revisiones retenidas por proxy | **250** |
| Revisiones retenidas por shared flow | 250 |
| Proxies desplegados por organización (Apigee X) | 6.000 |
| Proxies desplegados por organización (hybrid 2021) | 4.250 |
| Proxies desplegados por organización (hybrid 2024) | 6.000 |
| Proxies por entorno (Apigee X) | 6.000 |
| Proxies por entorno (hybrid 2021) | 50 |
| Proxies por entorno (hybrid 2024) | 6.000 |
| Shared flows por entorno (Apigee X) | **75** |
| Shared flows por entorno (hybrid 2021) | 10 |
| Shared flows por entorno (hybrid 2024) | 75 |
| **ProxyEndpoints por proxy** | **10** (recomendado: 1) |
| **Flows máximos por proxy** | **200** |
| TargetEndpoints por proxy | 1.000 |
| Despliegues por instancia | 6.000 |

> [!WARNING]
> Además del límite duro, Google recomienda **no superar ~3.000 basepaths por entorno o environment group**. Por encima, aumenta la latencia de **todos** los despliegues, nuevos y existentes.

## Organización, entornos e instancias

| Límite | Valor |
|---|---|
| Entornos por organización (Apigee X) | Hasta **85** |
| Entornos por organización (hybrid) | 85 |
| Environment groups por organización | 85 |
| Attachments por environment group | 100 |
| **Hostnames por environment group** | **100** |
| Instancias por organización | 10 (11 en hybrid) |
| Regiones por organización | 10 |
| Basepaths de API por organización | 6.000 |
| Keystores por entorno | 100 |
| Truststores por entorno | 1.000 |
| **TargetServers por entorno** | **8.000** |
| Apigee Spaces por organización | 20 |
| QPS de operaciones list (Spaces) | 10 |

## Caché

| Límite | Valor |
|---|---|
| Cachés con scope de entorno | 100 |
| **Tamaño de la clave** | **2 KB** |
| **Tamaño del valor** | **256 KB** |
| Expiración | **≥ 1 segundo, ≤ 30 días** |
| Elementos por caché | 10 millones |

## KeyValueMaps

| Límite | Valor |
|---|---|
| **Entradas totales por organización** | **5 millones** |
| KVMs con scope de organización | 100 |
| KVMs con scope de entorno | **900** |
| Tamaño de la clave | 2 KB |
| **Tamaño del valor** | **10 KB** |

## Claves, developers y aplicaciones

| Límite | Valor |
|---|---|
| Tamaño del consumer key | 2 KB |
| Tamaño del consumer secret | 2 KB |
| Atributos personalizados | **18** |
| Developers por organización | 1 millón |
| **API keys por app** | **10** |
| Apps por developer | 100 |
| Apps por organización | 1 millón |
| **API products por organización** | **5.000** |
| API products por API key | 50 |
| API products por app | 100 |
| AppGroups por organización | 1 millón |
| Apps por AppGroup | 30.000 |

## OAuth

| Límite | Valor |
|---|---|
| **Expiración de access token** | **≥ 180 segundos, ≤ 30 días** |
| **Expiración de refresh token** | **≥ 1 día, ≤ 2 años** |
| Tamaño del token | 2 KB |
| Atributos personalizados en el token | 18 |

## Mensajes, peticiones y respuestas

| Límite | Valor |
|---|---|
| **Payload bufferizado** | **30 MB** |
| **Payload en streaming** | **10 MB** (con salvedades de rendimiento) |
| Payload de MessageLogging | **11 MB** |
| Tamaño de la URL de petición | 10 KB |
| Tamaño de cabeceras de petición | **60 KB** |
| Tamaño de cabeceras de respuesta | 60 KB |
| Tamaño del mensaje de handshake TLS | 128 KB |
| **Timeout de conexión al target** | **300 segundos** |

Superar el límite de payload produce `protocol.http.TooBigBody`.

## Cuota y rate limiting

| Límite | Valor |
|---|---|
| Intervalo de sincronización de cuota | **≥ 10 segundos** |
| Intervalo máximo de cuota | 1 año |
| Intervalo mínimo de cuota | 1 minuto |
| **SpikeArrest máximo por segundo** | **4.000** |
| **SpikeArrest máximo por minuto** | **240.000** |

## Analytics y monitorización

| Límite | Valor |
|---|---|
| Rango de informe síncrono (Apigee X) | **92 días** |
| Rango de informe síncrono (hybrid) | 14 días |
| **Rango máximo de consulta asíncrona** | **365 días** |
| Llamadas a la Analytics Metrics API | 100 por minuto |
| Llamadas a la Asynchronous Query API | 300 por día |
| Llamadas a la Data Export API | 500 por día |
| **Retención de datos de API Monitoring** | **6 semanas** |
| Latencia máxima observable | 60 segundos |

> [!WARNING]
> **La retención no es infinita.** Si necesitas histórico más allá de estos rangos para auditoría o facturación, exporta periódicamente con la **Data Export API** a BigQuery o Cloud Storage.

## Debug y trazado

| Límite | Valor |
|---|---|
| **Sesiones de depuración por minuto** | **100** |
| **Transacciones por sesión de depuración** | **15** |
| Tamaño de los datos de depuración | 10 KB |
| Tasa máxima de muestreo de trazado distribuido | **0,5** |

## Developer portals

| Límite | Valor |
|---|---|
| Páginas por portal | 1.000 |
| APIs/productos publicados por portal | 1.200 |
| Tamaño de documentación por API | 4 MB |
| Categorías por portal | 200 |
| Elementos de menú por portal | 200 |
| Archivos por portal | 500 |
| Tamaño por archivo | 10 MB |
| Almacenamiento total de archivos | 100 MB |
| Audiencias por portal | 16 |
| Cuentas de developer por audiencia | 800.000 |
| Campo de JavaScript personalizado | 150.000 caracteres |

## Redes

| Límite | Valor |
|---|---|
| NEGs de Private Service Connect por proyecto | Hasta 100 |
| Conexiones totales de PSC | Ilimitadas (aplican cuotas de Google Cloud) |
| Endpoint attachments por organización | 1.000 |
| Zonas de peering DNS por organización | 1.000 |

## Otros

| Límite | Valor |
|---|---|
| Herramientas MCP por organización | 1.000 |

---

## Los 15 límites que más veces te van a morder

En orden aproximado de frecuencia con la que causan problemas reales:

| # | Límite | Valor | Síntoma cuando lo superas |
|---|---|---|---|
| 1 | Transacciones por sesión de Trace | **15** | La sesión se cierra antes de capturar lo que buscabas |
| 2 | Valor de caché | **256 KB** | La caché "no funciona" con objetos grandes |
| 3 | Valor de KVM | **10 KB** | No puedes guardar un certificado o un JSON grande |
| 4 | Atributos personalizados | **18** | No puedes añadir más metadatos a un producto o app |
| 5 | API keys por app | **10** | La rotación falla al llegar al décimo |
| 6 | Payload bufferizado | **30 MB** | `protocol.http.TooBigBody` |
| 7 | Basepaths por entorno | **~3.000** recomendado | Los despliegues se vuelven lentos, todos |
| 8 | Retención de API Monitoring | **6 semanas** | Los datos que necesitas para auditoría ya no están |
| 9 | Shared flows por entorno | **75** | No puedes añadir el siguiente shared flow |
| 10 | Flows por proxy | **200** | El despliegue se rechaza |
| 11 | Expiración de access token | **≤ 30 días** | La configuración se rechaza |
| 12 | Bundle de proxy | **15 MB** | El despliegue se rechaza |
| 13 | Cabeceras de petición | **60 KB** | Fallo con tokens JWT muy grandes en cabecera |
| 14 | Intervalo de sync de cuota | **≥ 10 s** | La configuración se rechaza |
| 15 | Rango de consulta asíncrona | **365 días** | No puedes consultar más de un año de golpe |

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
