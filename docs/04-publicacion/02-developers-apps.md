---
id: publicacion-developers-apps
titulo: Developers, apps y AppGroups
area: publicacion
tags: [developer, app, appgroup, credenciales, onboarding]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/publish/adding-developers-your-api-product
revisado: 2026-08-20
---

# Developers, apps y AppGroups

## Jerarquía

```
Developer  (identificado por email, único en la org)
  └── Developer App   (hasta 100 por developer)
        ├── consumer key + consumer secret   (hasta 10 credenciales)
        └── suscripciones a API Products     (hasta 100 productos por app)
```

Para escenarios B2B se añade una capa:

```
AppGroup  (una empresa cliente)
  └── App  (hasta 30.000 por AppGroup)
```

## Developer

```json
{
  "email": "dev@cliente.com",
  "firstName": "Ana",
  "lastName": "García",
  "userName": "anagarcia",
  "attributes": [
    { "name": "empresa",   "value": "Cliente SA" },
    { "name": "cif",       "value": "B12345678" },
    { "name": "onboarding","value": "2026-08-20" }
  ]
}
```

El **email es la clave primaria** y es único dentro de la organización.

```bash
apigeecli developers create \
  --email dev@cliente.com --first Ana --last García --user anagarcia \
  --org "$ORG" --token "$(gcloud auth print-access-token)"
```

### Estados

| Estado | Efecto |
|---|---|
| `active` | Sus credenciales funcionan |
| `inactive` | **Todas** sus apps dejan de funcionar → `DeveloperStatusNotActive` |

Desactivar un developer es la forma más rápida de cortar el acceso de un cliente completo.

## Developer App

```json
{
  "name": "app-movil-produccion",
  "apiProducts": ["producto-basico"],
  "callbackUrl": "https://cliente.com/oauth/callback",
  "attributes": [
    { "name": "plataforma",  "value": "ios" },
    { "name": "entorno",     "value": "produccion" }
  ]
}
```

```bash
apigeecli apps create \
  --name app-movil-produccion --email dev@cliente.com \
  --prods producto-basico \
  --org "$ORG" --token "$(gcloud auth print-access-token)"
```

La respuesta contiene las credenciales:

```json
{
  "credentials": [{
    "consumerKey": "…",
    "consumerSecret": "…",
    "status": "approved",
    "apiProducts": [{ "apiproduct": "producto-basico", "status": "approved" }]
  }]
}
```

### Estados en tres niveles

La autorización se puede cortar en tres puntos independientes:

| Nivel | Estado | Efecto al revocar |
|---|---|---|
| **Developer** | active / inactive | Todas sus apps caen |
| **App** | approved / revoked | Esa app cae |
| **Credencial → producto** | approved / revoked | Esa key pierde acceso a ese producto, conserva los demás |

El tercer nivel es el más útil: permite quitarle a un cliente el acceso a un producto concreto sin tocar el resto.

```bash
# Revocar el acceso de una key a un producto concreto
apigeecli apps keys manage \
  --name app-movil-produccion --dev dev@cliente.com \
  --key CONSUMER_KEY --prod producto-premium --action revoke \
  --org "$ORG" --token "$(gcloud auth print-access-token)"
```

## Rotación de credenciales sin corte

Una app admite **hasta 10 credenciales** simultáneas:

```
1. Crear una credencial nueva en la app
2. Entregarla al cliente
3. El cliente migra su tráfico
4. Verificar en Analytics que la key antigua ya no recibe tráfico
5. Eliminar la credencial antigua
```

```bash
apigeecli apps keys create \
  --name app-movil-produccion --dev dev@cliente.com \
  --prods producto-basico \
  --org "$ORG" --token "$(gcloud auth print-access-token)"
```

> [!TIP]
> El paso 4 no es opcional. Filtra Analytics por `client_id` para confirmar que la key vieja está a cero antes de borrarla. Borrarla "porque ya avisamos" es cómo se rompe producción.

## AppGroups — modelo B2B

Cuando el consumidor no es un desarrollador individual sino una **empresa**:

```
AppGroup: "Cliente SA"
  ├── App: "erp-integracion"
  ├── App: "portal-web"
  └── App: "app-movil"
```

Ventajas sobre developers individuales:

- Las apps pertenecen a la organización, no a una persona. Si el desarrollador se va, no hay que reasignar nada.
- Se pueden gestionar varios miembros con distintos roles sobre el mismo grupo.
- Escala a **30.000 apps por AppGroup** y **1 millón de AppGroups por organización**.

```bash
apigeecli appgroups create --name cliente-sa \
  --org "$ORG" --token "$(gcloud auth print-access-token)"

apigeecli appgroups apps create \
  --name erp-integracion --group cliente-sa --prods producto-premium \
  --org "$ORG" --token "$(gcloud auth print-access-token)"
```

| Usa | Cuándo |
|---|---|
| **Developer + App** | Autoservicio, desarrolladores individuales, portal público |
| **AppGroup + App** | B2B, cuentas empresariales, integraciones contractuales |

## Límites

| Límite | Valor |
|---|---|
| Developers por organización | 1 millón |
| Apps por developer | 100 |
| Apps por organización | 1 millón |
| API keys por app | **10** |
| API products por app | 100 |
| API products por API key | 50 |
| Atributos personalizados | 18 |
| AppGroups por organización | 1 millón |
| Apps por AppGroup | 30.000 |
| Cuentas de developer portal por portal | 800.000 |

## Onboarding automatizado

El flujo típico en producción no pasa por la consola:

```bash
#!/usr/bin/env bash
set -euo pipefail

ORG="${ORG:?falta ORG}"
TOKEN="$(gcloud auth print-access-token)"
EMAIL="$1"
APP="$2"
PRODUCTO="$3"

# 1. Crear developer (idempotente: ignora si ya existe)
apigeecli developers create \
  --email "$EMAIL" --first "$(echo "$EMAIL" | cut -d@ -f1)" --last "-" --user "$EMAIL" \
  --org "$ORG" --token "$TOKEN" 2>/dev/null || echo "developer ya existe"

# 2. Crear app suscrita al producto
apigeecli apps create \
  --name "$APP" --email "$EMAIL" --prods "$PRODUCTO" \
  --org "$ORG" --token "$TOKEN"

# 3. Recuperar la credencial
apigeecli apps get --name "$APP" --org "$ORG" --token "$TOKEN"
```

> [!WARNING]
> Nunca envíes el `consumerSecret` por email o chat. Entrégalo por un canal con caducidad (gestor de secretos, enlace de un solo uso) o deja que el cliente lo recoja él mismo desde el developer portal.

## Developer portal

Apigee ofrece un portal integrado donde los desarrolladores se registran, ven la documentación (desde specs OpenAPI) y obtienen credenciales por autoservicio.

Límites relevantes:

| Límite | Valor |
|---|---|
| Páginas por portal | 1.000 |
| APIs/productos publicados por portal | 1.200 |
| Tamaño de documentación por API | 4 MB |
| Categorías por portal | 200 |
| Archivos por portal / tamaño / total | 500 / 10 MB c.u. / 100 MB |
| Audiencias | 16 |
| Cuentas de developer | 800.000 |

Alternativa habitual: un portal propio que consume la **API de gestión de Apigee** para el registro y la emisión de credenciales. Da control total sobre la experiencia a cambio de mantenerlo tú.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/publish/adding-developers-your-api-product>
- <https://cloud.google.com/apigee/docs/api-platform/publish/creating-apps-surface-your-api>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
