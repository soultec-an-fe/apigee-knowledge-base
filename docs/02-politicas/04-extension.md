---
id: politicas-extension
titulo: Políticas de Extensión y código personalizado
area: politicas
tags: [javascript, javacallout, servicecallout, messagelogging, flowcallout, datacapture]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy
revisado: 2026-08-20
---

# Políticas de Extensión y código personalizado

## Jerarquía de decisión

Google es explícito: **usa las políticas nativas primero**. Están endurecidas, optimizadas y soportadas; tu código no.

```
1. ¿Existe una política nativa?             → úsala
2. ¿AssignMessage + ExtractVariables bastan? → úsalas
3. ¿Necesitas lógica real?                   → JavaScript
4. ¿El rendimiento es crítico?               → JavaCallout
5. Python                                     → evitar (no existe en Apigee X)
```

> [!WARNING]
> Advertencia principal de Google en las mejores prácticas:
> **"Evita programar toda la lógica del proxy en recursos JavaScript, Java o Python."**
> Un proxy que es un `JavaScript` de 800 líneas no es un proxy de Apigee: es una aplicación mal desplegada.

---

## ServiceCallout

Llama a un servicio HTTP externo desde el flujo.

```xml
<ServiceCallout continueOnError="false" enabled="true" name="SC-ObtenerPerfil">
    <DisplayName>Obtener perfil de usuario</DisplayName>
    <Request clearPayload="true" variable="peticion.perfil">
        <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
        <Set>
            <Headers>
                <Header name="Authorization">Bearer {private.token_servicio}</Header>
                <Header name="Accept">application/json</Header>
            </Headers>
            <Verb>GET</Verb>
            <Path>/usuarios/{ruta.user_id}</Path>
        </Set>
    </Request>
    <Response>respuesta.perfil</Response>
    <Timeout>5000</Timeout>
    <HTTPTargetConnection>
        <LoadBalancer>
            <Server name="servicio-perfiles"/>
        </LoadBalancer>
    </HTTPTargetConnection>
</ServiceCallout>
```

Después se extrae con `ExtractVariables` sobre `respuesta.perfil`:

```xml
<ExtractVariables name="EV-Perfil">
    <Source>respuesta.perfil</Source>
    <JSONPayload>
        <Variable name="nivel" type="string"><JSONPath>$.nivel</JSONPath></Variable>
    </JSONPayload>
    <VariablePrefix>perfil</VariablePrefix>
</ExtractVariables>
```

### Reglas de ServiceCallout

| Regla | Detalle |
|---|---|
| **Construye la petición con `AssignMessage`** | Más legible que meter todo en `<Request><Set>` |
| **El protocolo NO puede venir de una variable** | `https://` debe ser literal en la URL. Usa variables solo para dominio y ruta |
| **Guarda la respuesta en una variable separada** | `<Response>respuesta.x</Response>` preserva el payload original |
| **Pon siempre `<Timeout>`** | Sin él, un servicio lento bloquea tu proxy |
| **Válido para encadenar proxies**, pero… | …para proxies de la **misma org/entorno** usa `LocalTargetConnection`, mucho más eficiente |
| **Evita recursión infinita** | Un callout que acaba llamándose a sí mismo agota el runtime |

> [!CAUTION]
> **Antipatrón documentado: usar ServiceCallout para invocar el backend en un proxy sin target.**
> Si vas a llamar al backend, usa un `TargetEndpoint`. `ServiceCallout` no participa en el load balancing, los health monitors, los reintentos ni las métricas de target. Reserva `ServiceCallout` para llamadas *auxiliares* (enriquecimiento, autorización externa), no para el destino principal.

> [!CAUTION]
> **Antipatrón documentado: invocar la API de gestión desde un proxy.**
> Nunca llames a `apigee.googleapis.com` desde un `ServiceCallout` en el camino del tráfico. Es lenta, tiene cuotas propias y acopla el plano de datos al plano de control. Si necesitas datos de configuración, cárgalos en un KVM o PropertySet.

---

## ExternalCallout

Envía las variables de flujo a un servidor **gRPC** propio, que puede leerlas y modificarlas (a diferencia de `ServiceCallout`). Es Standard y solo existe en X/hybrid. Ver la [referencia completa](referencia/external-callout.md).

```xml
<ExternalCallout name="EC-ServicioGrpc">
    <TimeoutMs>5000</TimeoutMs>
    <GrpcConnection>
        <Server name="servicio-grpc"/>
    </GrpcConnection>
    <Configurations>
        <Property name="with.request.content">true</Property>
        <Property name="with.request.headers">true</Property>
    </Configurations>
</ExternalCallout>
```

> [!NOTE]
> Corrección (2026-10-22): el elemento del timeout es `<TimeoutMs>`, no `<Timeout>`.

---

## FlowCallout

Invoca un shared flow. Ver [shared flows](../01-proxies/06-shared-flows-y-flow-hooks.md).

```xml
<FlowCallout continueOnError="false" enabled="true" name="FC-Seguridad">
    <SharedFlowBundle>comun-seguridad</SharedFlowBundle>
</FlowCallout>
```

---

## JavaScript

```xml
<Javascript continueOnError="false" enabled="true" timeLimit="200" name="JS-Normalizar">
    <DisplayName>Normalizar payload</DisplayName>
    <ResourceURL>jsc://normalizar-payload.js</ResourceURL>
    <IncludeURL>jsc://lib-utilidades.js</IncludeURL>
    <Properties>
        <Property name="modo">estricto</Property>
    </Properties>
</Javascript>
```

> [!NOTE]
> El elemento XML es `<Javascript>` con **j minúscula en el resto**: no `<JavaScript>`.

`resources/jsc/normalizar-payload.js`:

```javascript
// Objeto context: acceso a variables de flujo
var verbo   = context.getVariable('request.verb');
var payload = context.getVariable('request.content');
var modo    = properties.modo;   // desde <Properties>

try {
    if (!payload) {
        throw new Error('Payload vacío');
    }

    var datos = JSON.parse(payload);

    // Normalizar
    var salida = {
        id:     datos.orderId || datos.order_id || null,
        total:  Number(datos.total) || 0,
        moneda: (datos.currency || 'EUR').toUpperCase()
    };

    if (salida.id === null) {
        throw new Error('Falta el identificador de pedido');
    }

    context.setVariable('request.content', JSON.stringify(salida));
    context.setVariable('pedido.normalizado', 'true');

} catch (e) {
    // Lanzar una excepción con significado: Apigee la convierte en fallo
    context.setVariable('error.negocio', e.message);
    throw new Error('PAYLOAD_INVALIDO: ' + e.message);
}
```

### Objeto `context` — API principal

```javascript
context.getVariable('nombre')          // leer
context.setVariable('nombre', valor)   // escribir
context.removeVariable('nombre')       // eliminar
context.proxyRequest                   // objeto Message de la petición
context.proxyResponse
context.targetRequest
context.targetResponse
context.flow                           // 'PROXY_REQ_FLOW', 'TARGET_RESP_FLOW', ...
context.getVariable('message.content')  // funciona en cualquier contexto
```

Objetos globales disponibles: `crypto` (hashes), `httpClient` (⚠️ ver abajo), `print()` (a Trace), `properties`.

### Reglas de JavaScript

| Regla | Motivo |
|---|---|
| **Tiene límite de tiempo** (`timeLimit`) | Bloquea bucles infinitos. Si lo excedes, la política falla |
| **Usa siempre try/catch global** | Un error no capturado produce un fallo genérico e indepurable |
| **Lanza excepciones con significado** | El mensaje llega al fault handler |
| **Comprueba null/undefined** en variables de flujo opcionales | `getVariable` de algo inexistente devuelve `null` |
| **Coloca los archivos en `resources/jsc/`** | Convención obligatoria |
| **Usa la política `Javascript`, no `Script`** | La política `Javascript` **precompila en el despliegue**: errores de sintaxis se detectan antes de producción |
| **Soporta XML vía E4X** | Alternativa a XPath para manipular XML |
| **Base64 y iteración de JSON** están soportados | No necesitas librerías externas para eso |

> [!CAUTION]
> **Evita peticiones HTTP dentro de un JavaScript.** La guía de buenas prácticas de Google recomienda `ServiceCallout`. Si usas `httpClient` (por ejemplo, para varias llamadas en paralelo), hazlo siempre con callbacks.
>
> **NO uses `waitForComplete()`** sobre `httpClient`. Es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md#2-usar-waitforcomplete-en-código-javascript): bloquea el hilo, y como mucho el 30 % de los hilos de un Message Processor puede estar ejecutando JavaScript a la vez. Al agotarse, todo el tráfico del nodo falla con `500`.
>
> Referencia completa: [JavaScript](referencia/javascript.md).

---

## JavaCallout

```xml
<JavaCallout continueOnError="false" enabled="true" name="JC-Firma">
    <DisplayName>Calcular firma</DisplayName>
    <ClassName>com.empresa.apigee.FirmaCallout</ClassName>
    <ResourceURL>java://firma-callout.jar</ResourceURL>
    <Properties>
        <Property name="algoritmo">SHA256withRSA</Property>
    </Properties>
</JavaCallout>
```

```java
package com.empresa.apigee;

import com.apigee.flow.execution.ExecutionContext;
import com.apigee.flow.execution.ExecutionResult;
import com.apigee.flow.execution.spi.Execution;
import com.apigee.flow.message.MessageContext;

public class FirmaCallout implements Execution {

    @Override
    public ExecutionResult execute(MessageContext ctx, ExecutionContext execCtx) {
        try {
            // Preferido: getMessage() funciona en cualquier contexto
            String contenido = ctx.getMessage().getContent();

            String firma = calcularFirma(contenido);
            ctx.setVariable("firma.calculada", firma);

            return ExecutionResult.SUCCESS;

        } catch (Exception e) {
            ctx.setVariable("firma.error", e.getMessage());
            return ExecutionResult.ABORT;
        }
    }

    private String calcularFirma(String contenido) { /* ... */ return ""; }
}
```

### Reglas de Java

| Regla | Motivo |
|---|---|
| **No dependas de las librerías Java que trae Apigee** | Google declara ese uso **no soportado**. Empaqueta tus dependencias |
| **Importa los JAR vía la API de recursos**, no en `resources/java/` del bundle | Recomendación explícita de Google; permite compartirlos entre proxies |
| **Usa `ctx.getMessage()`** en lugar de métodos separados de request/response | Recupera el mensaje tanto en el flujo de petición como en el de respuesta. Referencia completa: [JavaCallout](referencia/java-callout.md) |
| **No gestiones recursos** (thread pools, conexiones, ficheros) | El MP es un entorno compartido; crear hilos lo desestabiliza |
| **Versiona el código fuente Java** | El JAR compilado no es auditable |
| **Devuelve `ExecutionResult.ABORT`** para señalar fallo | `SUCCESS` con un error dentro deja el flujo en estado inconsistente |

---

## PythonScript

> [!WARNING]
> ⚠️ **Solo Apigee Edge. No existe en Apigee X.**
> Aunque estés en Edge, Google recomienda evitarla: es interpretada en runtime e introduce un cuello de botella. Migra a JavaScript o JavaCallout.

---

## MessageLogging

Envía logs a syslog o a Cloud Logging.

```xml
<MessageLogging continueOnError="true" enabled="true" name="ML-CloudLogging">
    <DisplayName>Log a Cloud Logging</DisplayName>
    <CloudLogging>
        <LogName>projects/{organization.name}/logs/apigee-{apiproxy.name}</LogName>
        <Message contentType="application/json">
            {
              "proxy": "{apiproxy.name}",
              "revision": "{apiproxy.revision}",
              "correlation_id": "{messageid}",
              "verbo": "{request.verb}",
              "ruta": "{proxy.pathsuffix}",
              "status": "{message.status.code}",
              "producto": "{apiproduct.name}",
              "developer": "{developer.email}",
              "fin_cliente_ts": "{client.sent.end.timestamp}",
              "fin_backend_ts": "{target.received.end.timestamp}",
              "error": "{fault.name}"
            }
        </Message>
        <Labels>
            <Label>
                <Key>entorno</Key>
                <Value>{environment.name}</Value>
            </Label>
        </Labels>
    </CloudLogging>
</MessageLogging>
```

Variante syslog:

```xml
<MessageLogging continueOnError="true" enabled="true" name="ML-Syslog">
    <Syslog>
        <Message>{system.time} {organization.name} {apiproxy.name} {messageid} {message.status.code}</Message>
        <Host>logs.empresa.com</Host>
        <Port>514</Port>
        <Protocol>TCP</Protocol>
        <FormatMessage>true</FormatMessage>
        <SSLInfo><Enabled>true</Enabled></SSLInfo>
    </Syslog>
</MessageLogging>
```

### Reglas de MessageLogging

| Regla | Motivo |
|---|---|
| **Colócala en `PostClientFlow`** | Se ejecuta después de responder: cero latencia percibida, y también se ejecuta en errores |
| **Usa `continueOnError="true"`** | Un fallo de logging nunca debe tumbar una petición |
| **Una sola invocación por proxy** | **Antipatrón documentado**: cada invocación abre una conexión al destino (y un handshake TLS con syslog/TLS); un syslog lento genera contrapresión en el MP (latencia, 504) y las invocaciones del flujo de respuesta se pierden si hay error |
| **Formato consistente en toda la plataforma** | Recomendación de Google: usa el mismo shared flow de logging en todos los bundles |
| **Nunca registres secretos** | Filtra `Authorization`, API keys, PII. Usa variables `private.` |
| **Cuidado con el tamaño** | Payload de MessageLogging: **11 MB** según la página de límites, con aplicación «planificada». El tope real con `<CloudLogging>` es el de Cloud Logging: **256 KB** por entrada |

---

## DataCapture

Captura datos para analytics personalizado. Sustituye al antiguo `StatisticsCollector` de Edge. Ver la [referencia completa](referencia/data-capture.md).

```xml
<DataCapture name="DC-MetricasNegocio" continueOnError="true">
    <Capture>
        <DataCollector>dc_tenant</DataCollector>
        <Collect ref="ruta.tenant_id" default="desconocido"/>
    </Capture>
    <Capture>
        <DataCollector>dc_importe</DataCollector>
        <Collect ref="pedido.total" default="0"/>
    </Capture>
</DataCapture>
```

> [!NOTE]
> Corrección (2026-10-22): el valor se indica con `<Collect ref="…"/>` (o con sus hijos de extracción), no con `<Source>` directamente bajo `<Capture>`. Cada collector se captura con un máximo de 400 bytes, y hay un límite de 100 variables.

Los data collectors se declaran a nivel de entorno y aparecen como dimensiones en Analytics.

---

## PublishMessage

Publica en Pub/Sub, para arquitecturas orientadas a eventos. Es Standard y solo existe en X/hybrid; el proxy se despliega con una cuenta de servicio con `pubsub.topics.publish`. Ver la [referencia completa](referencia/publish-message.md).

```xml
<PublishMessage name="PM-EventoPedido">
    <Source>evento.payload</Source>
    <CloudPubSub>
        <Topic>projects/{organization.name}/topics/pedidos-creados</Topic>
    </CloudPubSub>
</PublishMessage>
```

---

## IntegrationCallout / SetIntegrationRequest

Invocan flujos de **Application Integration** de Google Cloud, para orquestaciones que no deben vivir en el proxy.

```xml
<SetIntegrationRequest name="SIR-Config">
    <ProjectId>mi-proyecto</ProjectId>
    <IntegrationName>procesar-pedido</IntegrationName>
    <TriggerName>api_trigger/procesar</TriggerName>
    <Parameters>
        <Parameter name="pedido_id" ref="ruta.pedido_id"/>
    </Parameters>
    <Request clearPayload="true">peticion.integracion</Request>
</SetIntegrationRequest>

<IntegrationCallout name="IC-Ejecutar">
    <AsyncExecution>false</AsyncExecution>
    <Request clearPayload="false">peticion.integracion</Request>
    <Response>respuesta.integracion</Response>
</IntegrationCallout>
```

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/java-callout-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/service-callout-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy>
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
