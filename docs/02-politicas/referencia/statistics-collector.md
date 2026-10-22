---
id: politica-statistics-collector
titulo: StatisticsCollector — referencia completa, solo Edge
area: politicas
tags: [statisticscollector, analytics, custom-reports, dimensiones, edge]
aplica_a: [apigee-edge]
elemento_xml: StatisticsCollector
tipo_politica: extension
fuente: https://docs.apigee.com/api-platform/reference/policies/statistics-collector-policy
revisado: 2026-10-22
---

# StatisticsCollector — referencia completa, solo Edge

> [!NOTE]
> **Solo Apigee Edge.** **Elemento raíz:** `<StatisticsCollector>`.
> La página oficial aclara que **no está disponible en Apigee hybrid**. En Apigee X y hybrid su sustituta es [DataCapture](data-capture.md), que trabaja con recursos *data collector*.

StatisticsCollector registra el valor de una o varias variables de flujo (predefinidas o propias) y lo envía al servidor de Analytics. Esos valores aparecen como **dimensiones** o **métricas personalizadas** en los informes personalizados de Edge.

## Sintaxis completa

```xml
<StatisticsCollector name="SC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <Statistics>
    <Statistic name="producto_id" ref="producto.id" type="string">desconocido</Statistic>
    <Statistic name="monto" ref="pago.monto" type="double">0</Statistic>
  </Statistics>
</StatisticsCollector>
```

## Elementos

| Atributo de `<Statistic>` | Obligatorio | Resumen |
|---|---|---|
| `name` | **Sí** | Nombre de la dimensión o métrica en los informes. |
| `ref` | **Sí** | Variable de origen. Suele venir de [ExtractVariables](extract-variables.md). |
| `type` | Ver nota | `string`, `integer`, `float`, `long`, `double` o `boolean`. `string` solo sirve como **dimensión**; los numéricos, como dimensión o como **métrica**. |
| Texto del elemento | No | Valor por defecto si `ref` no está definida. **Sin default, no se registra nada** para esa variable. |

> [!NOTE]
> **Contradicción en la documentación oficial sobre `type`:** la tabla lo marca como opcional con default `string`, y dice que se puede omitir si `ref` es una variable predefinida o si ExtractVariables declaró el tipo. Pero el error de despliegue `DatatypeMissing` se lanza cuando falta. Declara siempre el tipo.

> [!CAUTION]
> **El tipo no se puede cambiar** una vez que Edge empezó a recoger datos. Para cambiarlo, crea un `<Statistic>` con **otro nombre** sobre la misma variable.

### Reglas de nombres

- Solo `a-z`, `0-9` y `_`, sin espacios. No distingue mayúsculas y minúsculas.
- Prohibidos: `dsi`, `response_time`, `timekey`, `timestamp`, los nombres de métricas, dimensiones o filtros predefinidos de Analytics y las **palabras reservadas de PostgreSQL**.
- No crees dos collectors que solo difieran en mayúsculas (`statistics-collector` y `Statistics-Collector`): la exportación de datos falla con *duplicate column names*.

## Comportamiento

- **Una sola política por proxy.** Si hay varias, la **última** que se ejecuta determina los datos; las anteriores se pierden.
  - El caso legítimo es una en el flujo normal y otra en un *fault handler*: si hay error, la del fault handler manda y puede registrar información del fallo.
- **Latencia de la dimensión nueva:** la primera vez que se ejecuta en cada entorno, la dimensión tarda unos **30 minutos** en aparecer en la base de datos y en el desplegable de informes personalizados. Después, los datos llegan con el mismo retraso que el resto.
- **Retención por defecto:** los datos de más de **seis meses** no son accesibles sin pedirlo a soporte.
- **Consulta por API:** `GET /v1/o/{org}/environments/{env}/stats/{nombre}` con `select`, `timeRange` y `timeUnit`. Por ejemplo, `select=sum(message_count)` por día.

## Errores

**En runtime:** ninguno. **Variables de fallo:** ninguna.

### Al desplegar

| Error | Causa |
|---|---|
| `UnsupportedDatatype` | `type` no soportado. |
| `InvalidName` | El nombre choca con una variable del sistema (como `organization` o `environment`). |
| `DatatypeMissing` | Falta el `type`. |

## Migración a Apigee X

| StatisticsCollector (Edge) | DataCapture (X) |
|---|---|
| `<Statistic name>` define la dimensión en la propia política | La dimensión es un **recurso** *data collector* creado antes (`dc_…`) |
| `ref` + texto por defecto | `<Collect ref default>` |
| `type` en la política | El tipo se declara en el recurso data collector |
| Sin límites documentados de tamaño | 100 variables y 400 bytes por valor |
| La última política gana | El último que escribe cada collector gana |

## Antipatrones

- Varias políticas StatisticsCollector en el mismo flujo normal.
- Dimensiones de alta cardinalidad (IDs de usuario, tokens): degradan los informes.
- Recoger PII en Analytics.

## Fuentes

- StatisticsCollector policy — Apigee Edge: <https://docs.apigee.com/api-platform/reference/policies/statistics-collector-policy> (consultada directamente, contenido completo, 2026-10-22).
- DataCapture policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/data-capture-policy> (consultada directamente, 2026-10-22), para la tabla de migración.
