---
id: operacion-analytics
titulo: Analytics y monitoreo
area: operacion
tags: [analytics, metricas, monitoreo, cloud-logging, datacapture, sla]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/analytics/analytics-services-overview
revisado: 2026-08-20
---

# Analytics y monitoreo

## Las tres capas

| Capa | Qué responde | Herramienta |
|---|---|---|
| **Analytics** | "¿Cuánto tráfico, qué latencia, qué error rate, por qué producto?" | Analytics integrado de Apigee |
| **Logging** | "¿Qué pasó exactamente en esta petición de este cliente a las 14:32?" | `MessageLogging` → Cloud Logging |
| **Trace** | "¿Por qué falla esta petición ahora mismo?" | Sesión de depuración |

## Dimensiones y métricas integradas

Apigee recoge automáticamente, sin configuración:

**Dimensiones:** proxy, revisión, entorno, API product, developer, developer app, código de respuesta, verbo, ruta, target host, región, fault code, cliente.

**Métricas:** nº de peticiones, tasa de error, latencia total, latencia del target, latencia de procesamiento (overhead de Apigee), tamaño de petición y respuesta, cache hit rate.

## Límites de Analytics

| Límite | Valor |
|---|---|
| Rango de un informe síncrono (Apigee X) | **92 días** |
| Rango de un informe síncrono (hybrid) | 14 días |
| Rango máximo de consulta asíncrona | **365 días** |
| Llamadas a la Metrics API | 100 por minuto |
| Llamadas a la Async Query API | 300 por día |
| Llamadas a la Data Export API | 500 por día |
| Retención de datos de API Monitoring | **6 semanas** |
| Latencia máxima observable en métricas | 60 segundos |

> [!IMPORTANT]
> **La retención no es infinita.** Si necesitas histórico de más de un año para auditoría o facturación, exporta con la **Data Export API** a BigQuery o Cloud Storage de forma periódica. Descubrir esto cuando ya necesitas los datos es tarde.

## Métricas personalizadas con DataCapture

Para dimensiones de **negocio** que Apigee no conoce (tenant, tipo de operación, importe):

```xml
<DataCapture continueOnError="true" enabled="true" name="DC-MetricasNegocio">
    <Capture>
        <DataCollector>tenant</DataCollector>
        <Source>ruta.tenant_id</Source>
    </Capture>
    <Capture>
        <DataCollector>tipo_operacion</DataCollector>
        <Source>negocio.tipo</Source>
    </Capture>
</DataCapture>
```

Los data collectors se declaran a nivel de entorno y aparecen como dimensiones filtrables en los informes.

Colocación: **PostClientFlow**, para no añadir latencia.

## Logging estructurado

```xml
<MessageLogging continueOnError="true" enabled="true" name="ML-Transaccion">
    <CloudLogging>
        <LogName>projects/{organization.name}/logs/apigee-{apiproxy.name}</LogName>
        <Message contentType="application/json">
{
  "severity": "INFO",
  "proxy": "{apiproxy.name}",
  "revision": "{apiproxy.revision}",
  "entorno": "{environment.name}",
  "correlation_id": "{messageid}",
  "verbo": "{request.verb}",
  "ruta": "{proxy.pathsuffix}",
  "status": "{response.status.code}",
  "producto": "{apiproduct.name}",
  "developer": "{developer.email}",
  "app": "{developer.app.name}",
  "client_ip": "{client.ip}",
  "target_host": "{target.host}",
  "ts_inicio": "{client.received.start.timestamp}",
  "ts_fin": "{client.sent.end.timestamp}",
  "ts_target_inicio": "{target.sent.start.timestamp}",
  "ts_target_fin": "{target.received.end.timestamp}",
  "fault": "{fault.name}"
}
        </Message>
        <Labels>
            <Label><Key>entorno</Key><Value>{environment.name}</Value></Label>
            <Label><Key>proxy</Key><Value>{apiproxy.name}</Value></Label>
        </Labels>
    </CloudLogging>
</MessageLogging>
```

### Reglas de logging

| Regla | Motivo |
|---|---|
| **`PostClientFlow`** | Cero latencia percibida; se ejecuta también en errores |
| **`continueOnError="true"`** | Un fallo de logging nunca debe tumbar una petición |
| **Una sola invocación por proxy** | Invocar `MessageLogging` varias veces es un [antipatrón documentado](../09-antipatrones/01-catalogo-antipatrones.md) |
| **Formato JSON consistente** | Permite consultar con filtros estructurados en Cloud Logging |
| **Mismo shared flow en toda la plataforma** | Recomendación explícita de Google: formato estandarizado |
| **Nunca registres secretos ni PII** | Filtra `Authorization`, API keys, emails de usuario final, tarjetas |
| **Cuidado con el tamaño** | Límite de payload de MessageLogging: **11 MB** |

> [!WARNING]
> **No registres el payload completo por defecto.** Además del coste de almacenamiento, es la vía más común de filtrar datos personales a un sistema de logs con controles de acceso más laxos que la propia API. Registra el payload solo bajo un flag explícito y con retención corta.

## Calcular latencias

```
Latencia total     = client.sent.end.timestamp    - client.received.start.timestamp
Latencia backend   = target.received.end.timestamp - target.sent.start.timestamp
Overhead de Apigee = total - backend
```

El **overhead de Apigee** es la métrica que indica si tus políticas están bien diseñadas. Si crece, revisa:

| Sospechoso | Síntoma | Solución |
|---|---|---|
| `Quota` con `Synchronous=true` | Overhead constante alto | Pasar a asíncrona con `SyncIntervalInSeconds` |
| KVM sin `ExpiryTimeInSecs` | Overhead proporcional al nº de lecturas | Añadir caché en memoria |
| `ServiceCallout` sin timeout | Picos de overhead esporádicos | Fijar `<Timeout>` |
| `JavaScript` pesado | Overhead constante | Migrar a políticas nativas o JavaCallout |
| Regex con backtracking | Picos con payloads concretos | Reescribir el patrón |
| Demasiados basepaths | Latencia de despliegue y runtime | Mantenerse bajo 3.000 por entorno |

## Qué alertar

| Alerta | Umbral orientativo | Por qué |
|---|---|---|
| Error rate 5xx | > 1% durante 5 min | Fallo del backend o del proxy |
| Error rate 4xx | Salto brusco | Cambio de contrato o cliente roto |
| Latencia p99 | > SLA | Degradación |
| Overhead de Apigee | > 50 ms | Políticas mal diseñadas |
| `QuotaViolation` | Salto brusco | Cliente mal dimensionado o abuso |
| `SpikeArrestViolation` | Sostenido | Cliente sin backoff |
| Cache hit rate | Caída brusca | Cache key mal construida |
| Expiración de certificados | 30 días antes | Causa nº 1 de incidentes mTLS |
| Proxies sin desplegar tras un pipeline | Cualquiera | Despliegue fallido silencioso |

## Monitoreo del proxy en sí

Recomendación de Google sobre monitorización:

- En Apigee gestionado, **Google Cloud Operations monitoriza los componentes de la plataforma**.
- Usa **Analytics** para la monitorización no crítica (porcentajes de error, tendencias).
- Usa **Trace** para diagnosticar problemas de runtime concretos, tanto en desarrollo como en producción.

Un endpoint de health en cada proxy, servido sin backend, permite comprobar que el despliegue está vivo:

```xml
<Flow name="Health">
    <Condition>(proxy.pathsuffix MatchesPath "/health") and (request.verb = "GET")</Condition>
    <Request><Step><Name>AM-Health</Name></Step></Request>
</Flow>
```

```xml
<AssignMessage name="AM-Health">
    <Set>
        <StatusCode>200</StatusCode>
        <Payload contentType="application/json">{"estado":"ok","proxy":"{apiproxy.name}","revision":"{apiproxy.revision}","entorno":"{environment.name}"}</Payload>
    </Set>
    <AssignTo createNew="true" transport="http" type="response"/>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
</AssignMessage>
```

Devolver la **revisión** en el health es especialmente útil: confirma de un vistazo qué versión está sirviendo cada región tras un despliegue.

Excluye `/health` de la autenticación y de las cuotas:

```xml
<Step>
    <Name>VAK-VerificarApiKey</Name>
    <Condition>!(proxy.pathsuffix MatchesPath "/health")</Condition>
</Step>
```

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/analytics/analytics-services-overview>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/message-logging-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
