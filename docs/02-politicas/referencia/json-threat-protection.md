---
id: politica-json-threat-protection
titulo: JSONThreatProtection — referencia completa
area: politicas
tags: [jsonthreatprotection, json, dos, parser, limites, seguridad, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: JSONThreatProtection
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/json-threat-protection-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/json-threat-protection-policy
revisado: 2026-10-22
---

# JSONThreatProtection — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<JSONThreatProtection>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento.

JSONThreatProtection rechaza cuerpos JSON que superen límites de **estructura**: arrays enormes, anidamiento profundo, objetos con miles de claves, nombres o strings gigantes. Es la defensa contra ataques que buscan **agotar el parser** (memoria y CPU) del gateway o del backend. Ver la [guía de threat protection](../../03-seguridad/05-threat-protection.md) para el orden recomendado junto con las demás protecciones.

> [!IMPORTANT]
> **Solo se ejecuta si `Content-Type` es `application/json`.** Con otro tipo (por ejemplo `text/plain`), la política no hace nada aunque el cuerpo sea JSON. Si tu backend parsea JSON sin mirar la cabecera, un atacante puede saltarse la protección cambiando el `Content-Type`. Rechaza antes, con una condición, los tipos de contenido que tu API no acepta.

## Sintaxis completa

```xml
<JSONThreatProtection name="JTP-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Source>request</Source>
  <ArrayElementCount>100</ArrayElementCount>
  <ContainerDepth>10</ContainerDepth>
  <ObjectEntryCount>50</ObjectEntryCount>
  <ObjectEntryNameLength>64</ObjectEntryNameLength>
  <StringValueLength>2048</StringValueLength>
</JSONThreatProtection>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `jsonattack.{name}.failed`. |
| `continueOnError` | No | `false` | Con `true`, un payload malicioso **pasa**. No lo uses aquí. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |
| `async` | No | `false` | **Obsoleto.** |

## Elementos hijos

Todos los límites son enteros opcionales; si se omiten o son negativos, **no hay límite**.

| Elemento | Limita | Ejemplo |
|---|---|---|
| `<ArrayElementCount>` | Elementos de cualquier array | `[1,2,3]` = 3 |
| `<ContainerDepth>` | Profundidad de anidamiento de objetos y arrays | Un array que contiene un objeto que contiene otro objeto = 3 |
| `<ObjectEntryCount>` | Entradas (clave-valor) de cualquier objeto | `{"a":1,"b":2}` = 2 |
| `<ObjectEntryNameLength>` | Longitud del nombre de una clave | — |
| `<StringValueLength>` | Longitud de un valor string | — |
| `<Source>` | Mensaje a inspeccionar | `request` (default), `response` o `message` (petición en el flujo de petición, respuesta en el de respuesta) |

Un JSON **mal formado** también hace fallar la política.

> [!TIP]
> Calibra los límites contra tu **payload legítimo más grande**, con margen. Revisa también `<StringValueLength>` si aceptas contenido en base64 (documentos, imágenes): un archivo de 1 MB en base64 es un string de ~1,4 millones de caracteres.

## Variables de flujo

No publica variables de éxito.

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.jsonthreatprotection.ExecutionFailed` | 500 | Se superó algún límite, o el JSON es inválido. El motivo concreto va en el `faultstring`. |
| `steps.jsonthreatprotection.SourceUnavailable` | 500 | `<Source>` fuera de alcance o con un valor no válido. |
| `steps.jsonthreatprotection.NonMessageVariable` | 500 | `<Source>` apunta a una variable que no es de tipo mensaje. |

> [!IMPORTANT]
> Por defecto, un payload rechazado devuelve **500** y el código genérico `ExecutionFailed`. Con la propiedad de organización `features.isPolicyHttpStatusEnabled=true` (la activa el soporte de Google Cloud en X), en el **flujo de petición** devuelve **400** con un código de error específico. Si no puedes activarla, traduce el error a 400 en una FaultRule: el fallo es del cliente.

### Al desplegar

No tiene errores de despliegue propios.

### Variables de fallo

| Variable | Ejemplo |
|---|---|
| `fault.name` | `fault.name = "ExecutionFailed"` |
| `jsonattack.{name}.failed` | `jsonattack.JTP-Peticion.failed = true` |

El `faultstring` indica el límite superado (p. ej. "Exceeded object entry name length at line 2"). Útil para depurar, pero no se lo devuelvas al cliente tal cual.

## Ejemplos

### 1. Protección estándar en peticiones con cuerpo

```xml
<JSONThreatProtection name="JTP-Peticion">
  <Source>request</Source>
  <ArrayElementCount>200</ArrayElementCount>
  <ContainerDepth>8</ContainerDepth>
  <ObjectEntryCount>60</ObjectEntryCount>
  <ObjectEntryNameLength>64</ObjectEntryNameLength>
  <StringValueLength>4096</StringValueLength>
</JSONThreatProtection>
```

```xml
<Step>
  <Name>RF-Tipo-No-Soportado</Name>
  <Condition>(request.verb = "POST" or request.verb = "PUT" or request.verb = "PATCH") and not (request.header.Content-Type =| "application/json")</Condition>
</Step>
<Step>
  <Name>JTP-Peticion</Name>
  <Condition>request.verb = "POST" or request.verb = "PUT" or request.verb = "PATCH"</Condition>
</Step>
```

`RF-Tipo-No-Soportado` es una RaiseFault que responde `415 Unsupported Media Type`. El operador `=|` es "empieza por", así se acepta también `application/json; charset=utf-8`.

### 2. Respuesta 400 si no se puede activar la propiedad de organización

```xml
<FaultRule name="fr-json-malicioso">
  <Condition>jsonattack.JTP-Peticion.failed = true</Condition>
  <Step>
    <Name>AM-Error-400-Payload</Name>
  </Step>
</FaultRule>
```

## Diferencias en Apigee Edge

| Aspecto | Apigee X / hybrid | Apigee Edge |
|---|---|---|
| Elementos y errores | Iguales | Iguales |
| `features.isPolicyHttpStatusEnabled` | La activa el soporte de Google Cloud | Soporte de Edge (Public Cloud) o API de gestión (Private Cloud) |

## Antipatrones

- Confiar en la política sin controlar el `Content-Type`.
- No declarar ningún límite (la política no hace nada).
- `continueOnError="true"`.
- Devolver el 500 por defecto al cliente.

## Fuentes

- JSONThreatProtection policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/json-threat-protection-policy> (consultada directamente, contenido completo, 2026-10-22).
- JSON Threat Protection policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/json-threat-protection-policy> (consultada directamente, 2026-10-22).
- La propiedad `features.isPolicyHttpStatusEnabled` se describe en la página de XMLThreatProtection y aplica a las dos políticas de threat protection.
