---
id: politica-javascript
titulo: JavaScript — referencia completa y modelo de objetos
area: politicas
tags: [javascript, jsc, rhino, context, httpclient, crypto, e4x, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: Javascript
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/javascript-policy
revisado: 2026-10-22
---

# JavaScript — referencia completa y modelo de objetos

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<Javascript>` (con **s minúscula**: no `<JavaScript>`).
> **Aplica a:** Apigee X, hybrid y Edge.

La política JavaScript ejecuta código propio dentro del flujo del proxy. El código puede leer y escribir variables de flujo, manipular mensajes, calcular hashes, firmar SOAP (solo X/hybrid) y hacer llamadas HTTP con `httpClient`. En Apigee X el motor es **Rhino 1.7.13**: no es Node.js y no hay `require` ni npm.

## Cuándo usarla y cuándo no

Esta jerarquía la recomienda Google en su guía de buenas prácticas:

1. **Primero, las políticas estándar.** AssignMessage, ExtractVariables y compañía están optimizadas y tienen soporte. No reimplementes en JavaScript lo que ya hace una política.
2. **JavaScript para lógica simple en línea:** cuando es más claro que una cadena de políticas (por ejemplo, armar `target.url` con muchas combinaciones de URI), para iterar JSON o para Base64.
3. **[PythonScript](python-script.md)** solo si es imprescindible. Es interpretado y más lento; Google prefiere JavaScript.
4. **[JavaCallout](java-callout.md)** si el rendimiento es lo prioritario.
5. **Fuera del gateway** (ExternalCallout o ServiceCallout hacia Cloud Run o Cloud Functions) si la lógica tarda más de un segundo o es lógica de negocio. El gateway no es un servidor de aplicaciones.

No la uses para:

- **Logging.** Usa [MessageLogging](message-logging.md) en el PostClientFlow.
- **Llamadas al sistema.** Leer o escribir archivos, consultar procesos, CPU o memoria. El modelo de seguridad no lo permite, y lo que hoy funcione puede bloquearse sin aviso.

## Sintaxis completa

```xml
<Javascript name="JS-Nombre" timeLimit="200" languageVersion="VERSION_DEFAULT" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Properties>
    <Property name="modo">estricto</Property>
  </Properties>
  <SSLInfo>
    <Enabled>true</Enabled>
    <ClientAuthEnabled>false</ClientAuthEnabled>
    <TrustStore>ref://ts-backends</TrustStore>
  </SSLInfo>
  <IncludeURL>jsc://lib-utilidades.js</IncludeURL>
  <ResourceURL>jsc://principal.js</ResourceURL>
</Javascript>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Resumen |
|---|---|---|---|
| `timeLimit` | **Sí** | — | Tiempo máximo de ejecución en ms. Si se excede, la política falla con `Javascript runtime exceeded limit of {N}ms`. En cuentas de prueba gratuitas el tope es 200 ms. |
| `languageVersion` | No | `VERSION_DEFAULT` | `VERSION_1_0` … `VERSION_1_8` o `VERSION_ES6`. Solo lo documenta X/hybrid. |
| `name`, `continueOnError`, `enabled`, `async` | — | — | Los comunes (`async` está obsoleto). |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<ResourceURL>` | Uno de los dos | Archivo principal, `jsc://archivo.js`. Puede vivir en el bundle (`apiproxy/resources/jsc/`) o como recurso del entorno o de la organización, para reutilizarlo. |
| `<Source>` | Uno de los dos | Código en línea dentro del XML. **Si aparecen `<Source>` y `<ResourceURL>`, se ignora `<ResourceURL>`.** |
| `<IncludeURL>` | No | Librería que se carga **antes** del principal. Puede repetirse; se evalúan en el orden en que aparecen. |
| `<Properties>/<Property name>` | No | Valores literales que el código lee como `properties.{name}`. Siempre llegan como **cadenas**: `"true"`, no `true`. |
| `<SSLInfo>` | No | TLS para **todos** los clientes HTTP que cree el script (`httpClient`). Se configura igual que en un TargetEndpoint. |

> [!NOTE]
> **Contradicción en la documentación oficial:** los elementos `<ResourceURL>` y `<Source>` dicen que basta con uno de los dos. La descripción del error `NoResourceURLOrSource`, en cambio, dice que `<ResourceURL>` «es obligatorio». El nombre del error y el ejemplo oficial con `<Source>` sin `<ResourceURL>` indican que basta con uno.

> [!WARNING]
> Si subes archivos `.js` como recursos del entorno o de la organización por API, hazlo como `multipart/form-data` (`curl -F`). Un archivo subido de otra forma puede quedar mal guardado.

## Modelo de objetos

Al ejecutarse, el script recibe estos objetos globales:

| Objeto | Para qué |
|---|---|
| `context` | Variables de flujo y los cuatro mensajes de la transacción. |
| `request` / `response` | Atajos al mensaje de petición o respuesta **del contexto actual**: el del proxy en el ProxyEndpoint, el del target en el TargetEndpoint. |
| `crypto` | Hashes, formato de fechas y firma WS-Security. |
| `httpClient` | Llamadas HTTP asíncronas. |
| `properties` | Los `<Property>` de la política. |
| `print()` | Salida de depuración hacia la herramienta Debug. |

### `context`

| Miembro | Resumen |
|---|---|
| `getVariable(nombre)` | Lee una variable. Devuelve `null` si no existe. |
| `setVariable(nombre, valor)` | Escribe una variable propia o una predefinida que sea de escritura (por ejemplo `target.url`). |
| `removeVariable(nombre)` | Elimina una variable. |
| `flow` | `PROXY_REQ_FLOW`, `PROXY_RESP_FLOW`, `TARGET_REQ_FLOW` o `TARGET_RESP_FLOW`. Cada valor cubre el PreFlow, el PostFlow y los flujos condicionales de ese segmento. Sirve para que un mismo script se comporte distinto según dónde se adjunte. |
| `session` | Mapa clave/valor para pasar **objetos JavaScript** entre políticas de la misma transacción (`context.session['k'] = {...}`). Las variables de flujo, en cambio, son visibles para todas las políticas, condiciones y plantillas. |
| `proxyRequest`, `targetRequest` | Mensajes de petición: `url` (lectura y escritura), `headers`, `queryParams` (mapas `String => List`), `method` y `body.asJSON`, `body.asXML`, `body.asForm`. |
| `targetResponse`, `proxyResponse` | Mensajes de respuesta: `headers`, `status.code`, `status.message` y `content` (`.asJSON`, `.asXML`). |

- **XML con E4X:** `context.targetRequest.body.asXML.name` navega elementos, y `.@number` lee atributos. Como cadena, `content.asXML` sale limpio de declaraciones y comentarios, a diferencia de `content`.
- **Enteros grandes y `asJSON`:** en X, leer `request.content.asJSON` (aunque solo sea para leer) convierte los enteros grandes a notación exponencial **y reescribe el cuerpo del mensaje** con esos valores. Si el payload trae IDs numéricos largos, usa `JSON.parse(context.getVariable('request.content'))` y no escribas el cuerpo de vuelta sin necesidad.

### `crypto`

Solo hashes, **no cifrado reversible**.

| Función | Resumen |
|---|---|
| `crypto.getSHA1()`, `getSHA256()`, `getSHA512()`, `getMD5()` | Crea un objeto hash. También existe `crypto.getHash('SHA-256')` y equivalentes. |
| `.update(cadena)` | Añade datos; se puede llamar varias veces. |
| `.digest()` / `.digest64()` | Resultado en hexadecimal o en Base64. |
| `crypto.dateFormat(formato, [zona], [ms])` | Formatea una fecha con `SimpleDateFormat` de Java. La zona por defecto es UTC y el tiempo por defecto, ahora. |
| `crypto.wsSecRsaSign(payload, opciones)` | Firma un SOAP con WS-Security y X.509 (solo X/hybrid). |
| `crypto.wsSecRsaValidate(payload, opciones)` | Valida esa firma (solo X/hybrid). |

> [!WARNING]
> **Patrón de fecha:** los ejemplos oficiales de `dateFormat` usan `YYYY-MM-DD`. En `SimpleDateFormat`, `YYYY` es el año de semana ISO y `DD` el día del año, así que ese patrón da fechas erróneas cerca de fin de año. Usa `yyyy-MM-dd`.

> [!CAUTION]
> **WS-Security:**
> - En `wsSecRsaSign`, `signing_method` vale por defecto `rsa-sha1`. Pásalo siempre como `rsa-sha256`.
> - Al validar un documento que trae el certificado embebido, define `accept_thumbprints_sha256` (o `accept_subject_cns`). Sin eso, Apigee comprueba que la firma es correcta pero **no que el firmante sea de confianza**.
> - No actives `ignore_security_header_placement`: expone a ataques de *signature wrapping*.

### `httpClient`

Llamadas HTTP asíncronas, una o varias en paralelo, desde el script.

| Miembro | Resumen |
|---|---|
| `httpClient.get(url \| Request, [callback])` | GET simple. Con un objeto `Request` admite cabeceras. |
| `httpClient.send(Request, [callback])` | Petición completa, con un objeto `new Request(url, verbo, cabeceras)`. |
| Objeto `exchange` (si no pasas callback) | `isError()` (no hubo conexión; un 4xx/5xx **no** cuenta como error), `isSuccess()`, `isComplete()`, `getResponse()`, `getError()` y `waitForComplete()`. |
| Callback | `function onComplete(response, error) { … }` |

> [!CAUTION]
> **`waitForComplete()` es un [antipatrón documentado](../../09-antipatrones/01-catalogo-antipatrones.md#2-usar-waitforcomplete-en-código-javascript).** Bloquea el hilo mientras espera al backend. En un Message Processor, como mucho el **30 %** de los hilos puede estar ejecutando JavaScript a la vez. Cuando se agotan, las peticiones nuevas fallan con `500` «Timed out», incluso antes de que venza el `timeLimit` de la política. Usa siempre un callback.

Además, la guía de buenas prácticas de Google recomienda **evitar peticiones HTTP dentro de un script** y usar [ServiceCallout](service-callout.md), que gestiona mejor las conexiones. `httpClient` con callbacks queda para casos de composición (*mashups*) donde varias llamadas en paralelo justifican el código.

### Depuración con `print()`

`print()` escribe en la herramienta Debug. En X se ve en la propiedad `stepExecution-stdout` de la política o en «Output from all transactions»; en Edge, en el panel de salida de Trace.

## Variables de flujo

La política no fija variables por sí misma: las que haga falta las escribe el código con `context.setVariable`.

## Errores

### En runtime

Todos devuelven `500`.

| Código | Causa |
|---|---|
| `steps.javascript.ScriptExecutionFailed` | Excepción en el script (`RangeError`, `ReferenceError`, `SyntaxError`, `TypeError`, `URIError`…). |
| `steps.javascript.ScriptExecutionFailedLineNumber` | Error en el código; el `faultstring` indica la línea. |
| `steps.javascript.ScriptSecurityError` | El script intentó algo que el modelo de seguridad prohíbe. |

Un `throw` en tu código termina como `ScriptExecutionFailed`, y su mensaje aparece en el `faultstring`.

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidResourceUrlFormat` | Formato no válido en `<ResourceURL>` o `<IncludeURL>`. |
| `InvalidResourceUrlReference` | El archivo referenciado no existe ni en el proxy, ni en el entorno, ni en la organización. |
| `WrongResourceType` | La referencia no es de tipo `jsc`. |
| `NoResourceURLOrSource` | No hay código, o hay un `<IncludeURL>` vacío. |

### Variables de fallo

`fault.name` (por ejemplo `fault.name Matches "ScriptExecutionFailed"`) y `javascript.{policy_name}.failed`.

## Ejemplos

### 1. Normalizar un payload con errores con significado

```xml
<Javascript name="JS-Normalizar" timeLimit="200">
  <Properties>
    <Property name="monedaPorDefecto">COP</Property>
  </Properties>
  <ResourceURL>jsc://normalizar.js</ResourceURL>
</Javascript>
```

```javascript
// resources/jsc/normalizar.js
var crudo = context.getVariable('request.content');
if (!crudo) {
  context.setVariable('error.negocio', 'PAYLOAD_VACIO');
  throw new Error('PAYLOAD_VACIO');
}
var datos;
try {
  datos = JSON.parse(crudo);
} catch (e) {
  context.setVariable('error.negocio', 'JSON_INVALIDO');
  throw new Error('JSON_INVALIDO');
}
if (!datos.pedidoId) {
  context.setVariable('error.negocio', 'FALTA_PEDIDO_ID');
  throw new Error('FALTA_PEDIDO_ID');
}
context.setVariable('request.content', JSON.stringify({
  id: String(datos.pedidoId),
  total: Number(datos.total) || 0,
  moneda: (datos.moneda || properties.monedaPorDefecto).toUpperCase()
}));
```

Una FaultRule con `javascript.JS-Normalizar.failed = true` puede devolver un 400 legible a partir de `error.negocio`.

### 2. Hash de identificador para un log sin datos personales

```javascript
var h = crypto.getSHA256();
h.update(context.getVariable('private.salt.logs'));
h.update(context.getVariable('request.header.x-documento') || '');
context.setVariable('log.cliente_hash', h.digest());
```

### 3. Dos llamadas en paralelo con callbacks

```javascript
function guardar(prefijo) {
  return function (response, error) {
    if (response) {
      context.setVariable(prefijo + '.estado', response.status.code);
      context.setVariable(prefijo + '.cuerpo', response.content);
    } else {
      context.setVariable(prefijo + '.error', error);
    }
  };
}
httpClient.get(new Request('https://cuentas.interno.ejemplo.com/v1/saldo', 'GET', {}), guardar('saldo'));
httpClient.get(new Request('https://riesgo.interno.ejemplo.com/v1/score', 'GET', {}), guardar('score'));
```

Sin `waitForComplete()`. Si la composición es solo de una llamada, usa ServiceCallout.

## Diferencias en Apigee Edge

- **Motor:** la página de Edge remite a *Supported software* y no fija la versión de Rhino. No documenta `languageVersion`.
- **`crypto.wsSecRsaSign` y `wsSecRsaValidate`** no aparecen en el modelo de objetos de Edge.
- **Depuración:** `print()` sale en el panel *Output from all Transactions* de Trace.
- **Errores:** los mismos códigos de runtime y de despliegue.
- **Nota de enteros grandes con `asJSON`:** solo la documenta X.

## Antipatrones

- **`waitForComplete()`.** Agota los hilos JavaScript del Message Processor (ver arriba).
- **Peticiones HTTP en el script cuando basta un ServiceCallout.** Lo desaconseja la guía de buenas prácticas.
- **Toda la lógica del proxy en JavaScript.** Pierdes visibilidad en Debug, rendimiento y soporte. Usa políticas estándar.
- **Lógica de negocio pesada (más de un segundo).** Sácala del gateway.
- **`timeLimit` muy alto** para disimular un script lento. El límite protege al Message Processor.
- **Comparar `properties.x == true`.** Los valores llegan como cadena; compara con `"true"`.
- **Patrón `YYYY-MM-DD` en `crypto.dateFormat`.** Usa `yyyy-MM-dd`.

## Fuentes

- JavaScript policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/javascript-policy> (consultada directamente, contenido completo, 2026-10-22).
- JavaScript object model — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/javascript-object-model> (consultada directamente, contenido completo, 2026-10-22).
- Antipatrón «Use waitForComplete() in JavaScript code»: <https://docs.cloud.google.com/apigee/docs/api-platform/antipatterns/wait-for-complete> (consultada directamente, 2026-10-22).
- Best practices for API proxy design and development: <https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/best-practices-api-proxy-design-and-development> (consultada directamente, contenido completo, 2026-10-22).
- JavaScript policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/javascript-policy> (consultada directamente, contenido completo, 2026-10-22).
- JavaScript object model — Apigee Edge: <https://docs.apigee.com/api-platform/reference/javascript-object-model> (consultada directamente, contenido completo, 2026-10-22).
