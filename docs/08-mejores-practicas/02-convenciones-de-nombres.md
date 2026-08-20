---
id: practicas-nombres
titulo: Convenciones de nombres
area: practicas
tags: [naming, convenciones, prefijos, estilo]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development
revisado: 2026-08-20
---

# Convenciones de nombres

## Reglas obligatorias

Estas no son estilo: si no las cumples, **el despliegue falla**.

1. **El atributo `name` de la política debe coincidir con el nombre del archivo XML** (sin extensión).
2. **En las políticas `Script` y `ServiceCallout`, el `name` debe coincidir con el nombre del archivo de recurso** cuando corresponda.
3. **Extensiones de archivo correctas**: `.js`, `.py`, `.jar`, `.xsl`, `.xml`.

```
policies/VAK-VerificarApiKey.xml
  └─ <VerifyAPIKey name="VAK-VerificarApiKey">   ✅ coincide

policies/VAK-VerificarApiKey.xml
  └─ <VerifyAPIKey name="verificar-api-key">     ❌ despliegue falla
```

## Recomendaciones de Google

- **`DisplayName` debe describir claramente la función** de la política para quien no ha visto el proxy.
- **Usa prefijos consistentes** para los nombres de política. Google da como ejemplo `AM-xxx` para `AssignMessage`.
- **Mantén un estilo de nombrado consistente** para las variables: elige `camelCase` **o** `under_score` y no mezcles.
- **Usa prefijos de variable para organizar**, por ejemplo `Consumer.username`.

## Prefijos de política sugeridos

| Prefijo | Política |
|---|---|
| `AM-` | AssignMessage |
| `EV-` | ExtractVariables |
| `VAK-` | VerifyAPIKey |
| `OA-` | OAuthV2 |
| `Q-` | Quota |
| `SA-` | SpikeArrest |
| `RC-` | ResponseCache |
| `LC-` | LookupCache |
| `PC-` | PopulateCache |
| `IC-` | InvalidateCache |
| `KVM-` | KeyValueMapOperations |
| `JS-` | Javascript |
| `JC-` | JavaCallout |
| `SC-` | ServiceCallout |
| `FC-` | FlowCallout |
| `RF-` | RaiseFault |
| `ML-` | MessageLogging |
| `DC-` | DataCapture |
| `CORS-` | CORS |
| `JTP-` | JSONThreatProtection |
| `XTP-` | XMLThreatProtection |
| `REP-` | RegularExpressionProtection |
| `OAS-` | OASValidation |
| `X2J-` | XMLtoJSON |
| `J2X-` | JSONtoXML |
| `GJWT-` / `VJWT-` / `DJWT-` | GenerateJWT / VerifyJWT / DecodeJWT |
| `HM-` | HTTPModifier |
| `AC-` | AccessControl |
| `LTQ-` | LLMTokenQuota |
| `SCL-` / `SCP-` | SemanticCacheLookup / SemanticCachePopulate |
| `SUP-` / `SMR-` | SanitizeUserPrompt / SanitizeModelResponse |

Ventaja concreta: en una sesión de Trace, o al listar `policies/`, el tipo de cada política se lee de un vistazo sin abrir el archivo.

## Nombres de proxy

```
<dominio>-<version>

pedidos-v1
clientes-v2
pagos-v1
```

- La **versión va en el nombre y en el basepath**, no en las revisiones de Apigee.
- Evita nombres genéricos (`api`, `proxy`, `test`) y nombres de proyecto interno que caducan.

## Nombres de shared flow

```
sf-<dominio>-<funcion>

sf-seguridad-oauth
sf-logging-cloudlogging
sf-cabeceras-corporativas
sf-errores-formato
```

## Nombres de API product

Los productos representan **planes o audiencias**, no piezas técnicas:

```
producto-free
producto-basico
producto-premium
producto-partners
producto-interno
```

## Nombres de TargetServer

```
<servicio>-<rol opcional>

pedidos-svc
pedidos-svc-a       (para balanceo)
pedidos-svc-b
idp-backend
```

El **mismo nombre de TargetServer en todos los entornos**, apuntando a hosts distintos. Es lo que permite que el bundle sea idéntico en dev, test y prod.

## Nombres de KVM y de caché

```
kvm:    config-backends, secretos-firma, modelos
cache:  cache-tokens, cache-catalogo, cache-perfiles
```

## Nombres de variable

Elige un estilo y no lo mezcles. Usa un prefijo de dominio:

```
peticion.canal
peticion.trace_id
pedido.id
pedido.total
backend.token
config.timeout
private.api_key_backend      ← el prefijo private. oculta el valor en Trace
```

> [!IMPORTANT]
> El prefijo **`private.`** no es una convención de estilo: es funcional. Las variables que empiezan por `private.` **no aparecen en las sesiones de Trace**. Úsalo para todos los secretos.

## Nombres de flujo

Describe la **operación de negocio**, no el mecanismo:

```xml
<Flow name="ListarPedidos">      ✅
<Flow name="CrearPedido">        ✅
<Flow name="Flow1">              ❌
<Flow name="GET-pedidos">        ⚠️ funciona, pero es menos legible en Analytics
```

El nombre del flujo aparece en `current.flow.name` y en las sesiones de Trace: un nombre descriptivo ahorra tiempo real de diagnóstico.

## Nombres de FaultRule

Describe **qué error maneja**:

```xml
<FaultRule name="errores-autenticacion">
<FaultRule name="errores-cuota">
<FaultRule name="backend-no-disponible">
```

## Checklist

- [ ] Todo `name` de política coincide con su nombre de archivo
- [ ] Todas las políticas llevan `DisplayName` descriptivo
- [ ] Los prefijos de política son consistentes en todo el repositorio
- [ ] El estilo de variables es uniforme (`camelCase` o `under_score`, no ambos)
- [ ] Los secretos usan el prefijo `private.`
- [ ] Los nombres de flujo describen operaciones de negocio
- [ ] Los TargetServer tienen el mismo nombre en todos los entornos
- [ ] La versión de la API está en el nombre del proxy y en el basepath

## Fuentes

- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
