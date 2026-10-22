---
id: politica-external-callout
titulo: ExternalCallout — referencia completa
area: politicas
tags: [externalcallout, grpc, targetserver, cloud-run, google-id-token, standard]
aplica_a: [apigee-x, apigee-hybrid]
elemento_xml: ExternalCallout
tipo_politica: standard
fuente: https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/external-callout-policy
revisado: 2026-10-22
---

# ExternalCallout — referencia completa

> [!NOTE]
> **Tipo:** Standard (se puede desplegar en cualquier tipo de entorno). **Elemento raíz:** `<ExternalCallout>`.
> **Aplica a:** Apigee X y hybrid. **No existe en Apigee Edge.**

ExternalCallout envía las variables de flujo a un **servidor gRPC propio**. El servidor las lee, ejecuta tu lógica y devuelve **todas** las variables a Apigee. Apigee aplica entonces los cambios: crea las variables nuevas y actualiza las modificables que hayan cambiado. Es la forma de sacar lógica del gateway sin perder el acceso al contexto del mensaje, cosa que un [ServiceCallout](service-callout.md) no da.

En la guía de buenas prácticas, Google la recomienda para externalizar lógica que necesita leer o modificar el contexto. La propone como reemplazo de los *Hosted Targets* de Edge, alojando el servidor en Cloud Run. Según esa guía, puede rendir mejor que un ServiceCallout. Para lógica ligera que se ejecuta rápido en línea, mejor [JavaScript](javascript.md).

## Flujo de ejecución

1. Apigee envía al servidor gRPC un mensaje con las variables de flujo. Lo que se incluye depende de `<Configurations>`.
2. Tu servidor ejecuta su lógica y responde con el conjunto de variables, modificadas o no.
3. Apigee incorpora la respuesta: variables nuevas y cambios en las de escritura.

El contrato gRPC (archivo `.proto`) y servidores de ejemplo están en los *External Callout Samples* de Apigee en GitHub, enlazados desde la página oficial.

## Sintaxis completa

```xml
<ExternalCallout name="EC-Nombre" continueOnError="false" enabled="true">
  <DisplayName>Nombre legible</DisplayName>
  <TimeoutMs>5000</TimeoutMs>
  <GrpcConnection>
    <Server name="ts-grpc-reglas"/>
    <Authentication>
      <HeaderName ref="flujo.cabecera.token">X-Serverless-Authorization</HeaderName>
      <GoogleIDToken>
        <Audience ref="flujo.audiencia" useTargetUrl="false">https://reglas-xyz.a.run.app</Audience>
        <IncludeEmail>false</IncludeEmail>
      </GoogleIDToken>
    </Authentication>
  </GrpcConnection>
  <Configurations>
    <Property name="with.request.content">true</Property>
    <Property name="with.request.headers">false</Property>
    <Property name="with.response.content">false</Property>
    <Property name="with.response.headers">false</Property>
    <FlowVariable>reglas.entrada</FlowVariable>
  </Configurations>
</ExternalCallout>
```

## Elementos hijos

| Elemento | Obligatorio | Resumen |
|---|---|---|
| `<TimeoutMs>` | **Sí** | Timeout de la llamada gRPC en ms. Debe ser positivo. Ojo: el elemento es `TimeoutMs`, no `Timeout`. |
| `<GrpcConnection>/<Server name>` | **Sí** | Nombre de un **TargetServer** existente con protocolo **`GRPC`** (ver [TargetServer](../../01-proxies/05-target-endpoints-y-servidores.md#targetserver)). El TLS y el host se configuran en el TargetServer. |
| `<GrpcConnection>/<Authentication>` | No | Genera un **ID token de Google** (OIDC) para servicios como Cloud Run. Hybrid ≥ 1.6. |
| `<Configurations>` | No | Qué se envía al servidor. |
| `.../<Property name>` | Ver nota | `with.request.content`, `with.request.headers`, `with.response.content`, `with.response.headers`. Cada una vale `true` o `false`; el default es `false`. |
| `.../<FlowVariable>` | Ver nota | **Prefijo** de variables adicionales a enviar. `a.b.c` envía `a.b.c` y `a.b.c.x`, pero no `a.b.cd`. |

> [!NOTE]
> La tabla de `<Configurations>` marca `<Property>` y `<FlowVariable>` como «Required», pero el propio `<Configurations>` es opcional y `<Property>` tiene default `false`. La lectura coherente es que son opcionales: si no declaras nada, el servidor recibe solo las variables de flujo estándar, sin cuerpo ni cabeceras.

### `<Authentication>`

| Elemento | Resumen |
|---|---|
| `<HeaderName ref>` | Cabecera donde va el token. Default: `Authorization`. Con Cloud Run es habitual `X-Serverless-Authorization`, que deja intacto el `Authorization` original. Si `ref` resuelve, su valor manda sobre el literal. |
| `<GoogleIDToken>/<Audience ref useTargetUrl>` | Audiencia del token. Con `useTargetUrl="true"` y sin valor, se usa `https://` más el host del TargetServer. El default de `useTargetUrl` es `false`; en hybrid existe desde 1.8. |
| `<GoogleIDToken>/<IncludeEmail ref>` | Con `true`, el token incluye los claims `email` y `email_verified` de la cuenta de servicio. |

Para usar `<Authentication>`, el proxy se despliega con una **cuenta de servicio** (autenticación de Google) que tenga permiso para invocar el servicio. En Cloud Run, eso es `roles/run.invoker`; la página de la política no lo menciona, pero es el rol estándar de Cloud Run para invocar un servicio.

## Variables de flujo

La política no define variables propias. Las que devuelve el servidor quedan disponibles en el flujo.

## Errores

### Al desplegar

| Error | Causa |
|---|---|
| `FAILED_PRECONDITION` | Hay `<Authentication>` pero el proxy se desplegó sin cuenta de servicio. |
| `PERMISSION_DENIED` | La cuenta de servicio no existe, está en otro proyecto, o quien despliega no tiene `iam.serviceAccounts.actAs` sobre ella. |

### En runtime

Todos devuelven `500`.

| Código | Causa |
|---|---|
| `GrpcTlsInitFailed` | Fallo al iniciar TLS con el servidor (keystore, truststore). |
| `steps.externalcallout.{errorCode}` | El servidor devolvió un fallo propio: el código sale del campo `errorCode` y el `faultstring` del suyo. |
| `steps.externalcallout.ExecutionError` | Cualquier otra excepción. El `faultstring` incluye la causa gRPC. |
| `googletoken.EmptyIDTokenAudience` | `<GoogleIDToken>` sin audiencia y con `useTargetUrl="false"`. |

Diagnóstico frecuente de `ExecutionError` según el `faultstring`:

- **`UNAVAILABLE: Credentials failed to obtain metadata`:** la cuenta de servicio del despliegue se borró o se deshabilitó. En hybrid también puede faltar `roles/iam.serviceAccountTokenCreator` para la cuenta `apigee-runtime`, o estar deshabilitada la API IAMCredentials.
- **`PERMISSION_DENIED: HTTP status code 403`:** la cuenta no tiene permiso sobre el servicio, o el servicio exige autenticación y la política no la envía.

### Otros

| Código | Causa |
|---|---|
| `ReferencesExistToGrpcServer` | Se intenta borrar un TargetServer gRPC que todavía usan políticas desplegadas. |

### Variables de fallo

`fault.name` y `externalcallout.{policy_name}.failed`.

## Ejemplo: reglas de elegibilidad en Cloud Run

```xml
<ExternalCallout name="EC-Elegibilidad">
  <TimeoutMs>800</TimeoutMs>
  <GrpcConnection>
    <Server name="ts-grpc-elegibilidad"/>
    <Authentication>
      <HeaderName>X-Serverless-Authorization</HeaderName>
      <GoogleIDToken>
        <Audience useTargetUrl="true"/>
      </GoogleIDToken>
    </Authentication>
  </GrpcConnection>
  <Configurations>
    <Property name="with.request.content">true</Property>
    <FlowVariable>elegibilidad</FlowVariable>
  </Configurations>
</ExternalCallout>
```

El servidor lee el cuerpo y las variables `elegibilidad.*` que dejó el proxy, y devuelve por ejemplo `elegibilidad.resultado = "APROBADO"`. Una condición posterior en el flujo actúa sobre ese valor.

## Diferencias en Apigee Edge

No existe en Edge. Lo más parecido eran los *Hosted Targets* o los ServiceCallout hacia servicios propios.

## Antipatrones

- **Timeout alto.** La llamada está en el camino crítico de cada petición: fija un `<TimeoutMs>` acorde a tu SLO.
- **Enviar cuerpo y cabeceras sin necesidad** (`with.*` en `true`). Más latencia y más superficie de exposición de datos.
- **Prefijos de `<FlowVariable>` demasiado amplios** (por ejemplo `request`). Mandan muchas más variables de las necesarias.
- **Servidor gRPC sin TLS o sin autenticación.** El servidor puede **modificar variables** del flujo; trátalo como parte del gateway.

## Fuentes

- ExternalCallout policy — Apigee X/hybrid: <https://docs.cloud.google.com/apigee/docs/api-platform/reference/policies/external-callout-policy> (consultada directamente, contenido completo, 2026-10-22).
- Best practices for API proxy design and development, sección *Custom Logic in API Proxies*: <https://docs.cloud.google.com/apigee/docs/api-platform/fundamentals/best-practices-api-proxy-design-and-development> (consultada directamente, contenido completo, 2026-10-22).
