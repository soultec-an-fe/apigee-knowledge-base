---
id: politica-flow-callout
titulo: FlowCallout — referencia completa
area: politicas
tags: [flowcallout, shared-flow, reutilizacion, parametros, extensible]
aplica_a: [apigee-x, apigee-hybrid, apigee-edge]
elemento_xml: FlowCallout
tipo_politica: extensible
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy
fuente_edge: https://docs.apigee.com/api-platform/reference/policies/flow-callout-policy
revisado: 2026-10-22
---

# FlowCallout — referencia completa

> [!NOTE]
> **Tipo:** Extensible. **Elemento raíz:** `<FlowCallout>`.
> **Aplica a:** Apigee X, hybrid y Edge, con el mismo comportamiento en las tres.

FlowCallout invoca un **shared flow** desde un API proxy o desde otro shared flow. Funciona como una llamada a función: la ejecución entra al shared flow, recorre sus pasos y vuelve a la política. Para el diseño de shared flows y la alternativa implícita (flow hooks), ver [shared flows y flow hooks](../../01-proxies/06-shared-flows-y-flow-hooks.md).

## Sintaxis completa

```xml
<FlowCallout name="FC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Parameters>
    <Parameter name="entrada" value="literal"/>
    <Parameter name="origen" ref="request.header.x-canal"/>
    <Parameter name="modo">estricto</Parameter>
    <Parameter name="cliente">{developer.app.name}</Parameter>
  </Parameters>
  <SharedFlowBundle>sf-seguridad</SharedFlowBundle>
</FlowCallout>
```

## Atributos del elemento raíz

Los comunes: `name` (obligatorio), `continueOnError`, `enabled` y `async` (obsoleto).

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<SharedFlowBundle>` | **Sí** | Nombre del shared flow a invocar. Tiene que coincidir con el atributo `name` del `<SharedFlowBundle>` del bundle del shared flow. |
| `<Parameters>` | No | Contenedor de `<Parameter>`. |
| `<Parameter name value ref>` | No | Crea una variable de runtime llamada **exactamente** como `name`. El valor sale de `value`, de `ref`, del texto del elemento o de una plantilla `{variable}` dentro del texto. |

> [!IMPORTANT]
> Las variables de `<Parameter>` **no llevan prefijo**. Con `<Parameter name="limite">`, el shared flow lee `limite` (por ejemplo `context.getVariable("limite")`), no `flowcallout.FC-Nombre.limite`. Solo existen **mientras se ejecuta el shared flow**. Elige nombres que no choquen con variables del proxy, por ejemplo con un prefijo propio como `sf.cuota.limite`.

## Variables de flujo

| Variable | Alcance | Valor |
|---|---|---|
| `apigee.edge.sharedflow.name` | Durante la ejecución del shared flow | Nombre del shared flow. |
| `apigee.edge.flowhook.name` | Durante un shared flow adjunto a un flow hook | Nombre del flow hook. |

## Errores

| Código | HTTP | Causa |
|---|---|---|
| `flow.SharedFlowNotFound` | 500 | El shared flow no existe, o existe pero **no está desplegado** en el entorno. |

No hay errores de despliegue documentados. Por eso un shared flow sin desplegar no impide desplegar el proxy, y el fallo aparece recién en runtime. Despliega primero el shared flow.

Los errores de las políticas **dentro** del shared flow se propagan al proxy invocador y los manejan sus FaultRules (ver [manejo de errores](../../01-proxies/06-shared-flows-y-flow-hooks.md#manejo-de-errores-dentro-de-un-shared-flow)).

## Ejemplo: cuota parametrizada

En el proxy:

```xml
<FlowCallout name="FC-Cuota">
  <Parameters>
    <Parameter name="sf.cuota.limite">1000</Parameter>
    <Parameter name="sf.cuota.unidad">hour</Parameter>
  </Parameters>
  <SharedFlowBundle>sf-cuota</SharedFlowBundle>
</FlowCallout>
```

En el shared flow:

```xml
<Quota name="Q-Dinamica">
  <Allow countRef="sf.cuota.limite" count="100"/>
  <Interval>1</Interval>
  <TimeUnit ref="sf.cuota.unidad">hour</TimeUnit>
</Quota>
```

## Diferencias en Apigee Edge

La sintaxis, los parámetros, las variables y el error son los mismos.

## Antipatrones

- Recursión: un shared flow que se invoca a sí mismo, directa o indirectamente.
- Nombres de parámetro genéricos (`input`, `limite`) que pisan variables del proxy.
- Desplegar el proxy antes que el shared flow, lo que causa `SharedFlowNotFound` en producción.

## Fuentes

- FlowCallout policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/flow-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
- FlowCallout policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/flow-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
