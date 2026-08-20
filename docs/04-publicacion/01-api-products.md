---
id: publicacion-api-products
titulo: API products
area: publicacion
tags: [api-product, quota, scopes, operations, acceso, monetizacion]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/publish/what-api-product
revisado: 2026-08-20
---

# API products

> [!IMPORTANT]
> **El API product es el concepto más importante y peor entendido de Apigee.**
>
> - El **API proxy** es *técnico*: cómo se procesa una petición HTTP.
> - El **API product** es *de acceso y negocio*: qué operaciones puede llamar una app, con qué cuota y con qué scopes.
>
> Una API key **no da acceso a un proxy**. Da acceso a **los products que la contienen**.

## El modelo completo

```
API Proxy(s)  ──agrupados en──►  API Product  ◄──suscrita──  Developer App  ◄──posee──  Developer
                                      │                            │
                                      ├─ Cuota                     └─ consumer key + secret
                                      ├─ Scopes OAuth
                                      ├─ Operaciones (verbo + ruta)
                                      ├─ Entornos permitidos
                                      ├─ Nivel de acceso
                                      └─ Atributos personalizados
```

## Qué define un API product

| Atributo | Función |
|---|---|
| **API proxies / Operations** | Qué proxies y qué operaciones concretas (verbo + ruta) están incluidos |
| **Environments** | En qué entornos es válido |
| **Quota** | Límite de llamadas por intervalo, leído por la política `Quota` |
| **OAuth scopes** | Scopes que se conceden a los tokens emitidos para este producto |
| **Access level** | `public`, `private` o `internal`: controla la visibilidad en el portal |
| **Custom attributes** | Pares clave/valor arbitrarios. **La clave de la flexibilidad** |

## Operations — control granular

En lugar de incluir un proxy entero, se declaran operaciones concretas:

```json
{
  "name": "producto-basico",
  "displayName": "Plan Básico",
  "approvalType": "auto",
  "environments": ["prod"],
  "quota": "1000",
  "quotaInterval": "1",
  "quotaTimeUnit": "hour",
  "scopes": ["pedidos.read"],
  "operationGroup": {
    "operationConfigType": "proxy",
    "operationConfigs": [
      {
        "apiSource": "pedidos-v1",
        "operations": [
          { "resource": "/pedidos",   "methods": ["GET"] },
          { "resource": "/pedidos/*", "methods": ["GET"] }
        ],
        "quota": { "limit": "1000", "interval": "1", "timeUnit": "hour" }
      }
    ]
  },
  "attributes": [
    { "name": "nivel",      "value": "basico" },
    { "name": "feature_v2", "value": "false" }
  ]
}
```

El plan premium sería el mismo proxy con más métodos y más cuota:

```json
{
  "name": "producto-premium",
  "quota": "100000",
  "quotaInterval": "1",
  "quotaTimeUnit": "hour",
  "scopes": ["pedidos.read", "pedidos.write"],
  "operationGroup": {
    "operationConfigType": "proxy",
    "operationConfigs": [
      {
        "apiSource": "pedidos-v1",
        "operations": [
          { "resource": "/**", "methods": ["GET", "POST", "PUT", "DELETE"] }
        ]
      }
    ]
  },
  "attributes": [
    { "name": "nivel",      "value": "premium" },
    { "name": "feature_v2", "value": "true" }
  ]
}
```

**El mismo proxy, sin un solo cambio de código, sirve dos planes distintos.**

## Cómo se aplica en runtime

`VerifyAPIKey` u `OAuthV2 VerifyAccessToken` hacen la resolución:

1. Buscan la credencial.
2. Recorren los API products asociados.
3. Buscan uno que incluya **este proxy** y **esta operación** (verbo + ruta) en **este entorno**.
4. Si lo encuentran, pueblan `apiproduct.*` y dejan pasar.
5. Si no, lanzan `InvalidApiKeyForGivenResource`.

Luego la política `Quota` **lee** los valores del producto:

```xml
<Quota name="Q-DesdeProducto">
    <Identifier ref="client_id"/>
    <Allow countRef="apiproduct.developer.quota.limit" count="100"/>
    <Interval ref="apiproduct.developer.quota.interval">1</Interval>
    <TimeUnit ref="apiproduct.developer.quota.timeunit">hour</TimeUnit>
    <Distributed>true</Distributed>
    <Synchronous>false</Synchronous>
</Quota>
```

> [!TIP]
> **Este es el patrón que debes interiorizar:** el proxy no sabe nada de planes. Solo lee lo que dice el producto. Cambiar el plan de un cliente = cambiar el producto de su app. Cero despliegues, cero código.

## Atributos personalizados: feature flags sin despliegue

Los custom attributes del producto son accesibles en el flujo:

```xml
<Condition>verifyapikey.VAK-VerificarApiKey.apiproduct.feature_v2 = "true"</Condition>
```

Usos habituales:

| Atributo | Uso |
|---|---|
| `nivel` | Enrutar a backends distintos por tier |
| `feature_*` | Activar comportamiento nuevo por cliente |
| `tenant_id` | Multi-tenancy: filtrar datos por inquilino |
| `llmQuota` | Cuota de tokens para [proxies de LLM](../02-politicas/05-politicas-ai.md) |
| `backend_url` | Backend dedicado por cliente enterprise |

## approvalType

| Valor | Comportamiento |
|---|---|
| `auto` | La app queda aprobada inmediatamente al suscribirse |
| `manual` | Requiere aprobación explícita de un administrador |

Usa `manual` para productos de pago o con datos sensibles.

## Diseño de productos: patrones

### Por nivel de servicio (el más común)
```
producto-free       → 100 req/día,     solo GET
producto-basico     → 10.000 req/día,  GET + POST
producto-premium    → 1M req/día,      todos los métodos
```

### Por dominio funcional
```
producto-pedidos    → proxies de pedidos
producto-clientes   → proxies de clientes
producto-pagos      → proxies de pagos (approvalType: manual)
```

### Por audiencia
```
producto-publico    → subconjunto de solo lectura, access level public
producto-partners   → operaciones ampliadas, approvalType manual
producto-interno    → todo, access level internal
```

> [!WARNING]
> **Antipatrón de producto: un producto por proxy.**
> Si tienes 40 proxies y 40 productos que contienen uno cada uno, no estás usando el modelo: estás duplicando el catálogo de proxies. Los productos deben representar **planes o audiencias**, no piezas técnicas.

## Límites

| Límite | Valor |
|---|---|
| API products por organización | **5.000** |
| API products por API key | 50 |
| API products por app | 100 |
| Atributos personalizados | 18 |

## Gestión con CLI

```bash
# Crear producto desde un JSON
apigeecli products create -f ./producto-basico.json \
  --org "$ORG" --token "$(gcloud auth print-access-token)"

# Listar
apigeecli products list --org "$ORG" --token "$(gcloud auth print-access-token)"

# Exportar todos (para versionar en Git)
apigeecli products export --org "$ORG" --token "$(gcloud auth print-access-token)"
```

> [!TIP]
> **Versiona los API products en Git** igual que los proxies. Son configuración de negocio con impacto directo en facturación y acceso: merecen revisión por PR y trazabilidad, no clics en la consola.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/publish/what-api-product>
- <https://cloud.google.com/apigee/docs/api-platform/publish/create-api-products>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
