---
id: politica-assert-condition
titulo: AssertCondition — referencia completa
area: politicas
tags: [assertcondition, condiciones, variables, dialogflow, mediacion, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: AssertCondition
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/assert-condition-policy
revisado: 2026-10-22
---

# AssertCondition — referencia completa

> [!NOTE]
> **Tipo:** Standard. **Elemento raíz:** `<AssertCondition>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

AssertCondition **evalúa una condición** en tiempo de ejecución y guarda el resultado (`true`/`false`) en la variable `assertcondition.{name}.truthValue`. No corta el flujo ni lanza error si la condición es falsa: solo calcula el booleano para usarlo después. Google la presenta en el contexto de las políticas de Dialogflow, pero sirve en cualquier proxy.

Las condiciones usan la misma sintaxis y operadores que `<Condition>` en los pasos y flujos: ver [Condiciones](../../01-proxies/03-condiciones.md).

## Sintaxis completa

```xml
<AssertCondition name="AC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Condition>(transferencia.monto > 0) and (transferencia.monto LesserThan 1000000)</Condition>
</AssertCondition>
```

## Atributos del elemento raíz

| Atributo | Obligatorio | Default | Qué hace |
|---|---|---|---|
| `name` | Sí | — | Nombre interno; da nombre a `assertcondition.{name}.truthValue`. |
| `continueOnError` | No | `false` | Con `true`, un error de evaluación no corta el flujo. |
| `enabled` | No | `true` | Con `false` no se ejecuta. |

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<Condition>` | **Sí** | Expresión booleana; puede combinar varias condiciones con operadores lógicos. |
| `<DisplayName>` | No | Etiqueta en la UI. |

## Variables de flujo

| Variable | Contenido |
|---|---|
| `assertcondition.{name}.truthValue` | `true` si la condición se cumple, `false` si no. |

## Errores

### En runtime

| Código | HTTP | Causa |
|---|---|---|
| `steps.assertcondition.ConditionEvaluationFailed` | 500 | No se pudo evaluar la condición (p. ej. valores inesperados en las variables). |

### Al desplegar

| Error | Causa |
|---|---|
| `InvalidCondition` | Condición mal formada u operadores no soportados. |

### Variables de fallo

`fault.name` y `AssertCondition.{name}.failed` (con mayúsculas, según la página).

## Ejemplo: calcular una vez, usar varias

```xml
<AssertCondition name="AC-Operacion-Alto-Riesgo">
  <Condition>(transferencia.monto > 5000000) or (riesgo.puntaje > 700)</Condition>
</AssertCondition>
```

```xml
<Step>
  <Name>SC-Notificar-Antifraude</Name>
  <Condition>assertcondition.AC-Operacion-Alto-Riesgo.truthValue = true</Condition>
</Step>
<Step>
  <Name>AM-Marcar-Revision</Name>
  <Condition>assertcondition.AC-Operacion-Alto-Riesgo.truthValue = true</Condition>
</Step>
```

Centralizar la regla en una política evita repetir la misma condición en varios `<Step>` y que se desincronicen. Si lo que quieres es **rechazar** cuando no se cumple, usa directamente una [RaiseFault](raise-fault.md) con esa condición.

## Diferencias en Apigee Edge

No existe en Edge. Alternativa: AssignMessage con `<AssignVariable>` no evalúa condiciones; usa una política JavaScript que calcule el booleano.

## Antipatrones

- Esperar que la política bloquee la petición cuando la condición es falsa.

## Fuentes

- AssertCondition policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/assert-condition-policy> (consultada directamente, contenido completo, 2026-10-22).
