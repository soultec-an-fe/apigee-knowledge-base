---
id: seguridad-apikeys
titulo: API keys y VerifyAPIKey
area: seguridad
tags: [apikey, consumer-key, verifyapikey, autenticacion]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/security/api-keys
revisado: 2026-08-20
---

# API keys y VerifyAPIKey

## Qué es realmente una API key en Apigee

Una API key es el **consumer key** de una developer app. No identifica a un usuario final: identifica a una **aplicación cliente**.

```
Developer  ──posee──►  Developer App  ──suscrita a──►  API Products  ──contienen──►  API Proxies
                            │
                            └─ consumer key    (la "API key")
                            └─ consumer secret (para OAuth client credentials)
```

## Qué valida `VerifyAPIKey`

En un único paso comprueba **cuatro** cosas:

1. La key **existe** y su estado es aprobado.
2. La **app** está aprobada (no revocada).
3. El **developer** está activo.
4. **Algún API product** asociado a la key incluye este proxy **y** la operación concreta (verbo + ruta) que se está invocando.

El punto 4 es la autorización real. Una key no da acceso "al proxy": da acceso a lo que declaran sus productos.

```xml
<VerifyAPIKey continueOnError="false" enabled="true" name="VAK-VerificarApiKey">
    <DisplayName>Verificar API key</DisplayName>
    <APIKey ref="request.header.x-api-key"/>
</VerifyAPIKey>
```

## Dónde poner la key

| Ubicación | Recomendación |
|---|---|
| Cabecera `X-API-Key` o `apikey` | ✅ **Recomendado** |
| Cabecera `Authorization` custom | ✅ Válido |
| Query param `?apikey=` | ⚠️ Evitar: queda en logs de acceso, historial del navegador y cabecera `Referer` |
| Form param | ⚠️ Solo POST, poco convencional |

## Contexto que puebla

Un `VerifyAPIKey` exitoso deja disponible todo el contexto de autorización:

```
apiproduct.name
apiproduct.developer.quota.limit / .interval / .timeunit
developer.id / developer.email
developer.app.name / app.name
client_id
verifyapikey.<NOMBRE>.*         ← incluye atributos personalizados
```

Los atributos personalizados de la app y del producto son accesibles:

```xml
<Condition>verifyapikey.VAK-VerificarApiKey.apiproduct.nivel = "premium"</Condition>
<Condition>verifyapikey.VAK-VerificarApiKey.tenant_id != null</Condition>
```

Esto es la base del patrón de [feature flags por producto](../02-politicas/06-recetas-xml.md).

## Errores

| `fault.name` | Causa | Respuesta recomendada |
|---|---|---|
| `FailedToResolveAPIKey` | La variable de `<APIKey ref>` no existe (no se envió la key) | 401 |
| `InvalidApiKey` | La key no existe | 401 |
| `InvalidApiKeyForGivenResource` | La key existe, pero ningún producto cubre esta operación | 403 |
| `DeveloperStatusNotActive` | Developer inactivo | 403 |
| `ApplicationNotApproved` | App revocada | 403 |
| `keymanagement.service.CompanyStatusNotActive` | Empresa / AppGroup inactivo | 403 |

> [!TIP]
> Distinguir 401 (no te has identificado / credencial inválida) de 403 (te identificaste, pero no tienes acceso a esto) ayuda enormemente al desarrollador consumidor. Configura FaultRules separadas.

## Rotación de keys

Una app admite hasta **10 API keys** simultáneas. Eso permite rotación sin corte:

```
1. Añadir una key nueva a la app
2. Los clientes migran a la key nueva
3. Revocar la key antigua
```

```bash
# Añadir credencial nueva
apigeecli apps keys create --name mi-app --dev developer@example.com \
  --prods producto-basico --org "$ORG" --token "$(gcloud auth print-access-token)"

# Revocar la antigua
apigeecli apps keys delete --name mi-app --dev developer@example.com \
  --key KEY_ANTIGUA --org "$ORG" --token "$(gcloud auth print-access-token)"
```

## Límites

| Límite | Valor |
|---|---|
| Tamaño del consumer key | 2 KB |
| Tamaño del consumer secret | 2 KB |
| API keys por app | **10** |
| Apps por developer | 100 |
| Apps por organización | 1 millón |
| Developers por organización | 1 millón |
| Atributos personalizados | 18 |
| API products por API key | 50 |
| API products por app | 100 |

## Cuándo NO usar API keys

| Escenario | Alternativa correcta |
|---|---|
| App móvil o SPA (el secreto no se puede guardar) | OAuth 2.0 con PKCE, o un BFF que guarde la credencial |
| Necesitas identificar al **usuario final**, no a la app | OAuth 2.0 o JWT de un IdP |
| Necesitas revocación granular por sesión | OAuth 2.0 con tokens de vida corta |
| Servicio a servicio dentro de Google Cloud | `VerifyIAM` con identidades de servicio |
| El consumidor ya tiene identidad corporativa (SSO) | `VerifyJWT` contra el JWKS del IdP |

> [!WARNING]
> Una API key embebida en una app móvil o en JavaScript de navegador **no es un secreto**. Cualquiera puede extraerla. Sirve para *identificar* y *medir*, no para *autorizar* acceso sensible.

## Combinación con cuota

El patrón canónico completo:

```xml
<PreFlow name="PreFlow">
    <Request>
        <Step><Name>VAK-VerificarApiKey</Name></Step>  <!-- resuelve producto -->
        <Step><Name>SA-FrenoDePicos</Name></Step>       <!-- protege runtime -->
        <Step><Name>Q-CuotaProducto</Name></Step>       <!-- aplica plan -->
    </Request>
</PreFlow>
```

El orden importa: `SpikeArrest` y `Quota` necesitan `client_id` y el contexto de producto, que solo existen **después** de `VerifyAPIKey`.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/security/api-keys>
- <https://cloud.google.com/apigee/docs/api-platform/reference/policies/verify-api-key-policy>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
