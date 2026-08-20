---
id: operacion-debug-trace
titulo: Debug y Trace
area: operacion
tags: [trace, debug, debugsession, diagnostico, troubleshooting]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/debug/trace
revisado: 2026-08-20
---

# Debug y Trace

**Trace** (sesión de depuración) captura el recorrido completo de una petición: cada política ejecutada, el valor de cada variable en cada paso, y el mensaje tal como entra y sale de cada componente.

Es la herramienta principal de diagnóstico en Apigee, y Google la recomienda tanto en desarrollo como en producción.

## Iniciar una sesión

### Desde la CLI

```bash
# Crear sesión de depuración en un proxy y revisión concretos
apigeecli apis debug --name pedidos-v1 --rev 12 \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"
```

### Con filtro

Filtrar es esencial en producción, donde miles de peticiones pasan por el mismo proxy:

```bash
# Solo peticiones con una cabecera concreta
apigeecli apis debug --name pedidos-v1 --rev 12 \
  --filter 'request.header.x-debug == "si"' \
  --org "$ORG" --env prod --token "$(gcloud auth print-access-token)"
```

Ejemplos de filtro útiles:

```
request.header.x-debug == "si"
request.queryparam.trace == "1"
client_id == "CONSUMER_KEY_DEL_CLIENTE"
response.status.code == 500
proxy.pathsuffix MatchesPath "/pedidos/*"
```

> [!TIP]
> En producción, **siempre con filtro**. Sin él capturas tráfico de todos los clientes, lo que además de ruido puede ser un problema de privacidad: la sesión guarda payloads y cabeceras completos, incluidos datos personales.

## Qué muestra

Para cada paso del pipeline:

| Sección | Contenido |
|---|---|
| **Request recibido** | Método, URL, cabeceras, payload tal como llegó |
| **Cada política ejecutada** | Nombre, tiempo consumido, variables antes y después |
| **Variables** | Todas las variables de flujo con su valor en ese instante |
| **RouteRule seleccionada** | Cuál se evaluó como verdadera |
| **Request al target** | Lo que Apigee envió realmente al backend |
| **Response del target** | Lo que el backend devolvió |
| **Response al cliente** | La respuesta final tras toda la mediación |
| **Errores** | Qué política falló, con qué `fault.name` |

## Cómo diagnosticar con Trace

### Una condición no dispara

1. Localiza el paso anterior a la condición.
2. Busca el **valor real** de la variable en ese punto.
3. Comprueba:
   - ¿Es `null` porque estás fuera de su ámbito? (`response.*` no existe en el request flow)
   - ¿Mayúsculas? `=` es sensible; usa `:=`
   - ¿`proxy.pathsuffix` o `request.path`? Es la confusión más habitual

### Latencia inesperada

Trace muestra el tiempo de cada política. Con las variables de timestamp:

```
Latencia total   = client.sent.end.timestamp   - client.received.start.timestamp
Latencia backend = target.received.end.timestamp - target.sent.start.timestamp
Overhead Apigee  = total - backend
```

Si el overhead es alto, busca en el Trace qué política concreta consume tiempo. Los sospechosos habituales: `Quota` síncrona, KVM sin `ExpiryTimeInSecs`, `ServiceCallout` sin timeout, `JavaScript` pesado, regex con backtracking.

### Un error sin explicación

1. Busca el paso donde `is.error` pasa a `true`.
2. Lee `fault.name` y `error.message`.
3. Comprueba qué `FaultRule` se activó (o si se activó la `DefaultFaultRule`).

### El backend recibe algo distinto de lo esperado

Compara la sección **"Request al target"** con lo que enviaste. Ahí se ve el efecto acumulado de todos los `AssignMessage` y de `target.copy.pathsuffix` / `target.copy.queryparams`.

## Límites

| Límite | Valor |
|---|---|
| Sesiones de depuración por minuto | **100** |
| Duración (`timeout`) de una sesión | **10 minutos por defecto; 600 segundos (10 min) es el máximo**. No configurable desde la UI, sí desde la API |
| Transacciones capturadas (`count`) | **15 por Message Processor** |
| Tamaño de los datos de depuración | 10 KB |
| Tasa máxima de muestreo de trazado distribuido | 0,5 |
| Retraso de activación | **~15 segundos** entre iniciar la sesión y que esté activa en todo Apigee |
| Retención de una sesión completada | Se borra a las **24 horas** de finalizar |

> [!IMPORTANT]
> Una sesión termina cuando se alcanza **primero** el `timeout` o el `count`. Verificado en la documentación oficial: el `count` de 15 transacciones **es por Message Processor**, no un total global de la sesión. Como el número de MPs en un clúster varía, **el efecto real del `count` es impredecible** — Google recomienda explícitamente no personalizarlo. En un proxy con tráfico alto y sin filtro, esas transacciones por MP se consumen en milisegundos con peticiones que no te interesan. **El filtro no es opcional en producción.**

> [!TIP]
> Hay un **retraso de ~15 segundos** entre iniciar la sesión de depuración y que quede activa en todo el runtime. Las peticiones enviadas en esos primeros 15-20 segundos pueden no capturarse. Espera antes de disparar la petición que quieres depurar.

> [!NOTE]
> No puedes **detener** una sesión activa manualmente; solo puedes borrar los datos ya capturados. Una sesión termina sola al alcanzar `timeout` o `count`.

## Ocultar datos sensibles

Las variables cuyo nombre empieza por `private.` **no aparecen** en las sesiones de Trace:

```xml
<KeyValueMapOperations name="KVM-Secretos" mapIdentifier="secretos">
    <Scope>environment</Scope>
    <ExpiryTimeInSecs>3600</ExpiryTimeInSecs>
    <Get assignTo="private.api_key_backend" index="1">
        <Key><Parameter>backend_api_key</Parameter></Key>
    </Get>
</KeyValueMapOperations>
```

> [!WARNING]
> El prefijo `private.` oculta la **variable**, no la cabecera. Si asignas el secreto a `request.header.Authorization`, ese header **sí** aparece en el Trace. Esto es difícil de evitar por completo: trata las sesiones de Trace de producción como material sensible y restringe quién puede crearlas mediante IAM.

## Trazado distribuido

Apigee se integra con Cloud Trace para correlacionar la traza del gateway con la del backend. Se activa por entorno con una tasa de muestreo (máximo **0,5**).

Ventaja sobre Trace: es **continuo y agregado**, no una captura puntual de 15 transacciones. Sirve para detectar degradaciones, no para depurar un caso concreto.

## Cuándo usar cada herramienta

| Necesidad | Herramienta |
|---|---|
| "Esta petición concreta falla, ¿por qué?" | **Trace** con filtro |
| "¿Cuánto tarda cada política?" | **Trace** |
| "El error rate subió hace 10 minutos" | **Analytics** |
| "¿Qué proxies tienen más latencia esta semana?" | **Analytics** |
| "¿Dónde se pierde el tiempo entre Apigee y el backend?" | **Cloud Trace** (trazado distribuido) |
| "Necesito el histórico de todas las peticiones de un cliente" | **MessageLogging** → Cloud Logging |
| "¿Alguien está abusando de la API?" | **Advanced API Security** |

> [!NOTE]
> Trace **no es un sistema de logging**. Es una captura puntual y limitada. Para trazabilidad permanente necesitas `MessageLogging` en el `PostClientFlow`. Ver [analytics y monitoreo](03-analytics-monitoreo.md).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/debug/trace> (consultada directamente, contenido completo)
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
