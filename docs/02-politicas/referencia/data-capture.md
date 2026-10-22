---
id: politica-data-capture
titulo: DataCapture — referencia completa
area: politicas
tags: [datacapture, analytics, data-collector, dimensiones-personalizadas, monetizacion, extensible]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: DataCapture
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/data-capture-policy
revisado: 2026-10-22
---

# DataCapture — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<DataCapture>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge**: allí se usaba *StatisticsCollector*. En organizaciones de pago por uso (*Pay-as-you-go*), requiere el complemento **Apigee API Analytics**.

DataCapture toma datos de la transacción (una variable, una cabecera, un parámetro, un campo del payload) y los envía a **Analytics** como valores de un *data collector*. Esos valores sirven para informes personalizados, monetización y reglas de monitoreo.

**Requisito previo:** el *data collector* tiene que existir como recurso de la organización (se crea por UI o por API, con nombre `dc_…` y un tipo). Si no existe, el proxy no despliega (`DeploymentAssertionError`).

## Sintaxis completa

```xml
<DataCapture name="DC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <IgnoreUnresolvedVariables>false</IgnoreUnresolvedVariables>
  <ThrowExceptionOnLimit>false</ThrowExceptionOnLimit>
  <Capture>
    <DataCollector>dc_tenant</DataCollector>
    <Collect ref="ruta.tenant_id" default="desconocido"/>
  </Capture>
  <Capture>
    <DataCollector>dc_moneda</DataCollector>
    <Collect default="NA">
      <Source>response</Source>
      <JSONPayload>
        <JSONPath>$.resultado.moneda</JSONPath>
      </JSONPayload>
    </Collect>
  </Capture>
</DataCapture>
```

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Capture>` | **Sí** (uno o más) | Una captura: un data collector y cómo obtener su valor. |
| `.../<DataCollector scope>` | **Sí** | Nombre del data collector. Con `scope="monetization"` captura variables de monetización. |
| `.../<Collect ref default>` | **Sí** | De dónde sale el valor: `ref` (una variable existente) **o exactamente uno** de los hijos de extracción. |
| `<IgnoreUnresolvedVariables>` | No | Comportamiento ante variables sin resolver. La página lo incluye en la sintaxis pero no lo describe. |
| `<ThrowExceptionOnLimit>` | No | Qué pasa al superar los límites de captura (ver abajo). Con `false`, se envían los datos (recortados o sin la variable descartada); con `true`, se devuelve un error y no se envía nada. |

> [!IMPORTANT]
> - **Un data collector por `<Capture>`, sin repetir dentro de la misma política.** Puedes tener varios `<Capture>` siempre que apunten a collectors distintos.
> - Si **varias políticas** escriben el mismo collector, **gana la última que se ejecuta**.

### Atributo `default` de `<Collect>`

Es el valor que se envía si la variable no tiene valor en runtime. Sin `default`, se envía `null` para collectors numéricos y `"Not set"` para los de texto.

> [!NOTE]
> La tabla oficial marca `default` como «Required», pero en la misma fila describe qué se envía cuando no se especifica, y varios ejemplos oficiales lo omiten. En la práctica es opcional. Declararlo sigue siendo buena idea para no ensuciar los informes con `"Not set"`.

### Hijos de extracción de `<Collect>`

> [!CAUTION]
> Estos elementos **se llaman igual que en [ExtractVariables](extract-variables.md) pero no funcionan igual**. Aquí no se anidan en `<Variable>`, y cada patrón debe tener **una sola** variable, llamada exactamente `{$}`.

| Elemento | Resumen |
|---|---|
| `<Source>` | Mensaje a analizar. Default: `message` (petición o respuesta según el flujo). Si no resuelve o no es un mensaje, la política falla. |
| `<URIPath>/<Pattern ignoreCase>` | Contra `proxy.pathsuffix` (sin basepath). Solo en peticiones; en una respuesta no hace nada. Admite varios `<Pattern>`: gana el primero que coincide. |
| `<QueryParam name>/<Pattern>` | Parámetro de query de la petición. Para repetidos: `code.2`, `code.3`… |
| `<Header name>/<Pattern>` | Cabecera de la petición o la respuesta. Para repetidas: `h.2`, o `h.values` para todas. |
| `<FormParam name>/<Pattern>` | Solo con `Content-Type: application/x-www-form-urlencoded`. |
| `<JSONPayload>/<JSONPath>` | Solo con `Content-Type: application/json`. |
| `<XMLPayload>` con `<Namespaces>` y `<XPath>` | Solo con `text/xml`, `application/xml` o `application/*+xml`. XPath 1.0, sin los ejes `parent`, `ancestor`, `following` ni `preceding`. |

## Límites de captura

| Límite | Valor | Al superarlo |
|---|---|---|
| Variables capturadas | **100** | La variable nueva se descarta. |
| Tamaño por valor (incluidas listas) | **400 bytes** | El valor se recorta. |

En ambos casos se escribe un mensaje en el log del Message Processor y se añade un error *limit reached* a `dataCapturePolicyErrors` (solo uno para el límite de cantidad). Si `<ThrowExceptionOnLimit>` es `true`, en vez de eso se devuelve un error al cliente y no se envían datos.

## Errores

### En runtime

| Código | Causa |
|---|---|
| `DataCollectorTypeMismatch` | El valor no es del tipo del data collector. |
| `ExtractionFailure` | Falló la extracción. |
| `UnresolvedVariable` | La variable no existe. |
| `VariableCountLimitExceeded` | Más de 100 variables. |
| `VariableValueLimitExceeded` | Un valor de más de 400 bytes. |
| `MsgContentParsingFailed` | El contenido no se pudo analizar como XML o JSON. |
| `InvalidMsgContentType` | El `Content-Type` no corresponde al de la cláusula de captura. |
| `NonMsgVariable` | `<Source>` no apunta a un mensaje. |
| `JSONPathQueryFailed` / `XPathEvaluationFailed` | La expresión no resolvió a un valor. |
| `PrivateVariableAccess` | Intento de capturar una variable `private.*`. |

La página no indica el código HTTP de estos errores.

**Dos vías de reporte:**

- Con `continueOnError="false"`, el error **corta el procesamiento** y se devuelve al cliente. Antes, la política intenta reunir todos sus errores.
- Siempre: el campo de Analytics **`dataCapturePolicyErrors`** guarda la lista de errores (`errorType`, `policyName`, `dataCollector`). La variable también se ve en Debug. Este campo está sujeto al mismo límite de 400 bytes.

### Al desplegar

| Código | Causa |
|---|---|
| `DeploymentAssertionError` | El data collector no existe en la organización. |
| `JsonPathCompilationFailed` | JSONPath no válido. |
| `XPathCompilationFailed` | Prefijo o expresión XPath con un namespace no declarado. |
| `PatternCompilationFailed` | Patrón no válido. |

## Ejemplos

### 1. Dimensiones de negocio para informes

```xml
<DataCapture name="DC-Negocio" continueOnError="true">
  <Capture>
    <DataCollector>dc_canal</DataCollector>
    <Collect default="desconocido">
      <Header name="X-Canal">
        <Pattern ignoreCase="true">{$}</Pattern>
      </Header>
    </Collect>
  </Capture>
  <Capture>
    <DataCollector>dc_producto_financiero</DataCollector>
    <Collect default="NA">
      <URIPath>
        <Pattern>/cuentas/{$}/movimientos</Pattern>
      </URIPath>
    </Collect>
  </Capture>
</DataCapture>
```

`continueOnError="true"` evita que un fallo de analítica tumbe la petición. Los errores siguen quedando en `dataCapturePolicyErrors`.

### 2. Valor de la respuesta

```xml
<DataCapture name="DC-Monto" continueOnError="true">
  <Capture>
    <DataCollector>dc_monto_transferencia</DataCollector>
    <Collect default="0">
      <Source>response</Source>
      <JSONPayload>
        <JSONPath>$.transferencia.monto</JSONPath>
      </JSONPayload>
    </Collect>
  </Capture>
</DataCapture>
```

`dc_monto_transferencia` debe ser numérico en el recurso. Si el backend devuelve el monto como texto, el resultado es `DataCollectorTypeMismatch`.

## Diferencias en Apigee Edge

No existe en Edge. Su equivalente era *StatisticsCollector*, que no usaba recursos de data collector sino nombres de estadística definidos en la política.

## Antipatrones

- **Capturar datos personales o identificadores únicos** (documento, email, número de cuenta). Analytics no es un almacén para PII, y la alta cardinalidad degrada los informes.
- **Reutilizar el mismo collector en varias políticas** sin querer: solo queda el valor de la última.
- **Valores largos** (cuerpos, tokens). Se recortan a 400 bytes.
- **`continueOnError="false"` en producción.** Un fallo de analítica no debería cortar una transacción de negocio.

## Fuentes

- DataCapture policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/data-capture-policy> (consultada directamente, contenido completo, 2026-10-22).
