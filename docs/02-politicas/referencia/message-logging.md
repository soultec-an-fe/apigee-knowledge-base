---
id: politica-message-logging
titulo: MessageLogging — referencia completa
area: politicas
tags: [messagelogging, logging, cloud-logging, syslog, postclientflow, observabilidad, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: MessageLogging
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/message-logging-policy
revisado: 2026-10-22
---

# MessageLogging — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<MessageLogging>`.
> **Aplica a:** Apigee X, hybrid y Edge. Los destinos cambian según la edición: **Cloud Logging** y **syslog** en X/hybrid; **syslog** y **archivo local** en Edge (el archivo solo en Edge for Private Cloud).

MessageLogging escribe un mensaje personalizado, armado con texto y variables de flujo, en un destino externo de logs. Sirve para auditoría, diagnóstico y para mandar trazas a Splunk, Sumo Logic, Loggly o Cloud Logging.

Dos ideas que hay que tener claras desde el principio:

1. **Es asíncrona.** El mensaje va a un búfer en memoria y un proceso aparte lo envía. La respuesta al cliente no espera, así que no añade latencia.
2. **Que falle el envío no hace fallar el proxy.** Si el servidor syslog está caído, el proxy sigue respondiendo bien. Las variables de fallo solo se llenan cuando falla **la política** (configuración, plantilla), no cuando falla la entrega. Es posible perder mensajes sin ver ningún error.

## Cuándo usarla

- Para registrar cada transacción con sus métricas finales (latencia, código de estado, app, desarrollador). Ponla en el **PostClientFlow**.
- Para mandar eventos de auditoría (quién accedió a qué) a un SIEM.
- No la uses como mecanismo de entrega garantizada. Si un evento no se puede perder, usa [ServiceCallout](service-callout.md) contra un endpoint con acuse, o PublishMessage hacia Pub/Sub en X.

## Sintaxis completa

Una política usa **un solo** destino. `<CloudLogging>` y `<Syslog>` no pueden ir juntos.

```xml
<!-- Destino Cloud Logging (X/hybrid ≥ 1.7) -->
<MessageLogging name="ML-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <CloudLogging>
    <LogName>projects/{organization.name}/logs/apigee-transacciones</LogName>
    <Message contentType="application/json" defaultVariableValue="na">{"proxy":"{apiproxy.name}","estado":"{message.status.code}"}</Message>
    <Labels>
      <Label>
        <Key>ambiente</Key>
        <Value>{environment.name}</Value>
      </Label>
    </Labels>
    <ResourceType>api</ResourceType>
  </CloudLogging>
</MessageLogging>
```

```xml
<!-- Destino syslog (X, hybrid y Edge) -->
<MessageLogging name="ML-Syslog" continueOnError="false" enabled="true">
  <Syslog>
    <Message contentType="text/plain">Texto con {variables}</Message>
    <Host>logs.ejemplo.com</Host>
    <Port>6514</Port>
    <Protocol>TCP</Protocol>
    <FormatMessage>true</FormatMessage>
    <PayloadOnly>false</PayloadOnly>
    <DateFormat>yyyy-MM-dd'T'HH:mm:ss.SSSZ</DateFormat>
    <SSLInfo>
      <Enabled>true</Enabled>
    </SSLInfo>
  </Syslog>
  <logLevel>INFO</logLevel>
</MessageLogging>
```

## Atributos del elemento raíz

Los comunes: `name` (obligatorio), `continueOnError`, `enabled` y `async` (obsoleto). No tiene atributos propios.

## Elementos hijos

### `<CloudLogging>` (X/hybrid)

Disponible en Apigee X y en hybrid desde la versión 1.7.0. Requiere tener habilitada la **Cloud Logging API** en el proyecto.

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<LogName>` | **Sí** | Formato `projects/{PROJECT_ID}/logs/{LOG_ID}`, con variables permitidas en ambas partes. Si al resolverse no cumple el formato, la política falla con `InvalidGoogleCloudLogName`. |
| `<Message contentType>` | **Sí** | El mensaje. `contentType` puede ser `text/plain` o `application/json`. Con JSON, el texto resuelto tiene que ser JSON válido, o falla con `InvalidJsonMessage`. |
| `<Labels>/<Label>` | No | Pares `<Key>`/`<Value>` que se adjuntan a la entrada de log. |
| `<ResourceType>` | No | Recurso monitoreado que genera el log. Default: `global`. |

> [!CAUTION]
> La documentación advierte que `<LogName>` admite variables, lo que permite generar un nombre de log distinto en cada llamada. No lo hagas con variables de alta cardinalidad (ID de cliente, ID de petición). Cada valor crea un log nuevo en Cloud Logging y se vuelve inmanejable. Usa un nombre fijo y pon lo variable en el mensaje o en las etiquetas.

#### Autenticación hacia Cloud Logging

- El proxy se despliega con una **cuenta de servicio** (autenticación de Google). Apigee usa esa identidad para escribir los logs.
- Esa cuenta de servicio necesita el permiso `logging.logEntries.create`. Lo más simple es el rol `roles/logging.logWriter`.
- En **hybrid**, la cuenta de servicio de runtime tiene que poder suplantar a la cuenta del proxy. Para eso necesita el rol `iam.serviceAccountTokenCreator` sobre ella.

### `<Syslog>`

| Elemento | Obligatorio | Default | Resumen |
|---|---|---|---|
| `<Message contentType>` | **Sí** | — | El mensaje, con plantillas de variables. |
| `<Host>` | No | `localhost` | Servidor syslog (nombre o IP). |
| `<Port>` | No | `514` | Puerto. Ver la nota de abajo sobre `InvalidPort`. |
| `<Protocol>` | No | `UDP` | `TCP` o `UDP`. UDP rinde más pero no garantiza la entrega. TLS solo funciona con `TCP`. |
| `<FormatMessage>` | No | `false` | Con `true`, antepone un encabezado fijo de Apigee al mensaje. **Loggly lo exige en `true`.** |
| `<PayloadOnly>` | No | `false` | Con `true`, envía solo el cuerpo, sin encabezado. Tiene prioridad sobre `FormatMessage`. |
| `<DateFormat>` | No | `yyyy-MM-dd'T'HH:mm:ss.SSSZ` | Plantilla de la marca de tiempo, con la sintaxis de `SimpleDateFormat` de Java. |
| `<SSLInfo>` | No | Sin TLS | Envío por TLS. Se configura igual que el `<SSLInfo>` de un TargetEndpoint, incluido TLS mutuo. Solo con `TCP`. |

**El encabezado de `FormatMessage=true`** tiene esta forma:

```text
<14>1 2026-10-22T09:24:39.039+0000 {uuid-del-message-processor} Apigee - - - Aquí empieza el mensaje
```

Incluye la prioridad syslog (calculada a partir de `logLevel` y la *facility*), la versión de syslog (`1`), la fecha con desfase UTC, el UUID del Message Processor y la cadena fija `Apigee - - -`. En Edge la cadena es `Apigee-Edge - - -`.

> [!WARNING]
> Con `FormatMessage=false` **el mensaje sigue llevando la prioridad y la fecha**. En Edge esto figura como *Known Issue 68722102*; la página de X describe el mismo comportamiento sin llamarlo error. Si el colector espera solo el cuerpo (por ejemplo, JSON puro), usa `<PayloadOnly>true</PayloadOnly>`.

> [!NOTE]
> **Contradicción en la documentación oficial sobre `<Port>`:** la tabla de elementos dice que es opcional, con default 514. El error de despliegue `InvalidPort`, en cambio, dice que se lanza «si el número de puerto no se especifica» o no es válido. Hasta verificarlo en un entorno real, declara siempre el puerto de forma explícita.

### `<logLevel>`

Valores: `INFO` (default), `ALERT`, `WARN`, `ERROR`. Cuando `FormatMessage=true`, el nivel cambia la prioridad numérica que va entre `< >` en el encabezado. En X, la página lo documenta dentro de la sección de syslog.

### Valores por defecto en la plantilla del mensaje

Si una variable no resuelve, se puede dar un valor de reserva de dos maneras:

- **Por variable**, con dos puntos: `{request.header.id:desconocido}`.
- **Para todo el mensaje**, con el atributo `defaultVariableValue` de `<Message>`: `<Message defaultVariableValue="desconocido">`.

El valor por defecto **no puede contener espacios**.

## Dónde ubicarla: PostClientFlow

Coloca MessageLogging en el **PostClientFlow** del ProxyEndpoint. Ese flujo tiene dos características que lo hacen ideal para esto:

- Se ejecuta **después** de enviar la respuesta al cliente, así que todas las métricas de la transacción ya están disponibles.
- Es el único flujo que se ejecuta **incluso si el proxy entró en estado de error**. Un log puesto ahí se escribe siempre.

```xml
<ProxyEndpoint name="default">
  <PostClientFlow>
    <Response>
      <Step>
        <Name>ML-Transaccion</Name>
      </Step>
    </Response>
  </PostClientFlow>
</ProxyEndpoint>
```

> [!IMPORTANT]
> Las variables `response.*` **no están disponibles** en el PostClientFlow cuando el flujo anterior fue un flujo de error. Usa `message.*` (por ejemplo `message.status.code` o `message.header.X`): en el PostClientFlow apunta a la respuesta, tanto si hubo error como si no. Ver [variables de flujo](../../01-proxies/04-variables-de-flujo.md).

## Variables de flujo

Solo se fijan cuando **la política** falla:

| Variable | Valor |
|---|---|
| `messagelogging.failed` | `true` si la política falló. |
| `messagelogging.{policy_name}.failed` | Lo mismo, con el nombre de la política. |

## Errores

### En runtime

Todos devuelven `500`.

| Código | Edición | Causa |
|---|---|---|
| `steps.messagelogging.StepDefinitionExecutionFailed` | Todas | Fallo genérico de ejecución; ver el `faultstring`. |
| `steps.messagelogging.InvalidGoogleCloudLogName` | X/hybrid | `LogName` no resolvió al formato `projects/{project}/logs/{logid}`. |
| `steps.messagelogging.InvalidJsonMessage` | X/hybrid | Con `contentType="application/json"`, el mensaje resuelto no es JSON válido. |
| `steps.messagelogging.TooManyPendingLoggingRequest` | X/hybrid | Hay más de **2500** peticiones pendientes de escribir en Cloud Logging **por pod de runtime**. Con dos pods, el límite efectivo es 5000. |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidProtocol` | `<Protocol>` distinto de `TCP` o `UDP`. |
| `InvalidPort` | Puerto ausente o no válido: debe ser un entero mayor que cero. |

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name Matches "StepDefinitionExecutionFailed"` |
| `messagelogging.{policy_name}.failed` | `messagelogging.ML-Transaccion.failed = true` |

### Tamaño del mensaje

La [página de límites](https://docs.cloud.google.com/apigee/docs/api-platform/reference/limits) de Apigee fija el payload de MessageLogging en **11 MB**, pero con aplicación «planificada» (todavía no se exige). Con `<CloudLogging>` el tope efectivo es el de Cloud Logging: **256 KB por entrada**.

### Desbordamiento del búfer

Si se escribe en el búfer más rápido de lo que se lee, el búfer se desborda y se pierden mensajes. Las señales son:

- Con Cloud Logging: el error `TooManyPendingLoggingRequest`.
- Con syslog: un mensaje en el log del sistema, `Log message size exceeded. Increase the max message size setting`.

La página de X menciona ajustar la propiedad `max.log.message.size.in.kb` (default 128 KB) en `message-logging.properties`. En Apigee X ese archivo no está a tu alcance, porque el runtime lo administra Google. Es un ajuste para Edge for Private Cloud (ver más abajo) y, posiblemente, para hybrid. **Pendiente de verificación** si hybrid expone esa propiedad.

## Ejemplos

### 1. Transacción completa a Cloud Logging en JSON

```xml
<MessageLogging name="ML-Transaccion">
  <CloudLogging>
    <LogName>projects/mi-proyecto/logs/apigee-transacciones</LogName>
    <Message contentType="application/json" defaultVariableValue="na">{"proxy":"{apiproxy.name}","revision":"{apiproxy.revision}","ambiente":"{environment.name}","verbo":"{request.verb}","ruta":"{request.path}","estado":"{message.status.code}","app":"{developer.app.name}","clienteIp":"{client.ip}","fin":"{client.sent.end.timestamp}"}</Message>
    <Labels>
      <Label>
        <Key>proxy</Key>
        <Value>{apiproxy.name}</Value>
      </Label>
    </Labels>
  </CloudLogging>
</MessageLogging>
```

Ponla en el PostClientFlow. Fíjate en que usa `message.status.code` y no `response.status.code`, para que el log salga bien también en las transacciones que terminaron en error.

### 2. Syslog por TLS hacia un SIEM, solo el cuerpo

```xml
<MessageLogging name="ML-Auditoria">
  <Syslog>
    <Message contentType="application/json">{"evento":"acceso","app":"{developer.app.name:anonima}","recurso":"{request.path}","estado":"{message.status.code}"}</Message>
    <Host>siem.interno.ejemplo.com</Host>
    <Port>6514</Port>
    <Protocol>TCP</Protocol>
    <PayloadOnly>true</PayloadOnly>
    <SSLInfo>
      <Enabled>true</Enabled>
      <TrustStore>ref://ts-siem</TrustStore>
    </SSLInfo>
  </Syslog>
  <logLevel>INFO</logLevel>
</MessageLogging>
```

### 3. Loggly (exige `FormatMessage`)

```xml
<MessageLogging name="ML-Loggly">
  <Syslog>
    <Message>[TOKEN-LOGGLY tag="{organization.name}.{apiproxy.name}.{environment.name}"] Petición a {request.path}</Message>
    <Host>logs-01.loggly.com</Host>
    <Port>514</Port>
    <Protocol>TCP</Protocol>
    <FormatMessage>true</FormatMessage>
  </Syslog>
  <logLevel>ALERT</logLevel>
</MessageLogging>
```

Sustituye `TOKEN-LOGGLY` por la clave de tu cuenta. Guárdala en un KVM cifrado y referénciala como variable, no la dejes escrita en el bundle.

## Diferencias en Apigee Edge

- **No existe `<CloudLogging>`.** En Edge los destinos son `<Syslog>` y `<File>`.
- **`<File>` solo en Edge for Private Cloud** (en Edge cloud no está disponible). Escribe en el disco de cada Message Processor:

  ```xml
  <MessageLogging name="ML-Archivo">
    <File>
      <Message>Petición {request.header.messageid:sin-id}</Message>
      <FileName>transacciones.log</FileName>
      <FileRotationOptions rotateFileOnStartup="true">
        <FileRotationType>TIME_SIZE</FileRotationType>
        <MaxFileSizeInMB>10</MaxFileSizeInMB>
        <RotationFrequency unit="minute">10</RotationFrequency>
        <MaxFilesToRetain>10</MaxFilesToRetain>
      </FileRotationOptions>
    </File>
    <logLevel>ERROR</logLevel>
  </MessageLogging>
  ```

  | Elemento | Resumen |
  |---|---|
  | `<FileName>` | Solo el nombre base, **sin ruta**. `/opt/.../mylog.log` es inválido. |
  | `<FileRotationOptions rotateFileOnStartup>` | Con `true`, rota el archivo cada vez que el motor de mensajería se reinicia. |
  | `<FileRotationType>` | Por tamaño, por tiempo o ambos. La tabla dice `size` o `time`, pero los ejemplos oficiales usan `SIZE`, `TIME` y `TIME_SIZE`. Usa los de los ejemplos. |
  | `<MaxFileSizeInMB>` | Tamaño que dispara la rotación (si se rota por tamaño). |
  | `<RotationFrequency unit="minute">` | Intervalo de rotación (si se rota por tiempo). |
  | `<MaxFilesToRetain>` | Archivos que se conservan. Default `8`. Con `0` se conservan **indefinidamente**, con riesgo de llenar el disco. |

  - **Ubicación por defecto** (4.16.01 y posteriores): `/opt/apigee/var/log/edge-message-processor/messagelogging/{org}/{env}/{proxy}/{revision}/{policy}/`.
  - **Cambiar la ubicación:** se cambia con `bin_setenv_data_dir`, o con la propiedad absoluta `conf/message-logging.properties+log.root.dir` en `/opt/apigee/customer/application/message-processor.properties`. La segunda tiene prioridad. Después hay que reiniciar el Message Processor.
- **`<BufferMessage>`** (Edge): si el proxy tiene *streaming* HTTP activado, los mensajes no se almacenan en búfer. Ponlo en `true` cuando el log necesita contenido analizado del mensaje. Default `false`.
- **Tamaño máximo de mensaje** (Edge for Private Cloud):
  - **4.15.07 y anteriores:** se edita `max.log.message.size.in.kb` en `message-logging.properties`.
  - **4.16.01 y posteriores:** se usa `conf/message-logging.properties+max.log.message.size.in.kb` en `message-processor.properties` y se reinicia el MP. La propiedad viene comentada por defecto.
- **Arranque en frío:** al configurar un destino syslog **nuevo**, el MP puede acumular hasta **1000 mensajes** en memoria antes de enviar el primero. En entornos de poco tráfico, eso se nota como un retraso inicial.
- **`DateFormat`**: el formato de fecha por defecto es global del sistema, y `<DateFormat>` lo sobrescribe solo para destinos syslog.
- **Errores:** en runtime, Edge solo documenta `StepDefinitionExecutionFailed`. Los errores de despliegue son los mismos (`InvalidProtocol`, `InvalidPort`).
- **Encabezado de `FormatMessage`:** usa `Apigee-Edge - - -` en lugar de `Apigee - - -`.

## Antipatrones

- **Invocarla varias veces, o fuera del PostClientFlow.** Es un [antipatrón documentado](../../09-antipatrones/01-catalogo-antipatrones.md#7-invocar-messagelogging-varias-veces-en-un-proxy). Cada invocación abre una conexión (y un handshake TLS con syslog/TLS), un syslog lento genera contrapresión en el MP (latencia, 504), y las invocaciones del flujo de respuesta no se ejecutan si hubo error. Guarda los datos en variables a lo largo del flujo y registra **una sola vez** en el PostClientFlow.
- **Usar `response.*` en el mensaje.** Esas variables salen vacías en las transacciones con error. Usa `message.*`.
- **Confiar en que no ver errores significa que todo se entregó.** La entrega es asíncrona y sus fallos no se reportan. Vigila el colector (volumen esperado contra volumen recibido).
- **Usar syslog por UDP para auditoría.** UDP puede perder paquetes sin avisar. Usa TCP con TLS.
- **Registrar secretos o datos personales.** Nunca pongas cabeceras `Authorization`, tokens, cuerpos completos o datos de tarjeta. El log sale de Apigee y queda bajo la retención de otro sistema.
- **Usar un `LogName` dinámico de alta cardinalidad.** Cada valor distinto crea un log nuevo (ver la advertencia en `<CloudLogging>`).
- **Dejar `MaxFilesToRetain` en `0` en Edge Private Cloud** sin un proceso que purgue los archivos viejos.

## Fuentes

- MessageLogging policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy> (consultada directamente, contenido completo, 2026-10-22).
- Límites de Apigee: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/limits> (consultada directamente, fila «Message logging payload», 2026-10-22).
- Antipatrón «Invoke MessageLogging multiple times»: <https://docs.cloud.google.com/apigee/docs/api-platform/antipatterns/messagelogging-multiple-times> (consultada directamente, 2026-10-22).
- MessageLogging policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/message-logging-policy> (consultada directamente, contenido completo, 2026-10-22).
