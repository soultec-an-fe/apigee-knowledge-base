---
id: fundamentos-org-entornos
titulo: Organizaciones, entornos y grupos de entorno
area: fundamentos
tags: [organizacion, environment, environment-group, hostname, routing, deployment]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview
revisado: 2026-08-20
---

# Organizaciones, entornos y grupos de entorno

## Jerarquía

```
Google Cloud Project  (1:1)
└── Organization (org)                    ← el contenedor raíz de Apigee
    ├── Environment: dev
    ├── Environment: test
    ├── Environment: prod
    │   ├── API proxies desplegados
    │   ├── Shared flows desplegados
    │   ├── KeyValueMaps (scope environment)
    │   ├── TargetServers
    │   ├── Keystores / Truststores
    │   └── Caches
    ├── Environment group: externo  ──► hostnames: api.empresa.com
    │   └── contiene: prod
    ├── Environment group: interno  ──► hostnames: api-int.empresa.com
    │   └── contiene: prod, test
    └── Recursos con scope de organización
        ├── API products
        ├── Developers y developer apps
        ├── AppGroups
        └── KeyValueMaps (scope organization)
```

## Organización

- Mapea a **exactamente un proyecto de Google Cloud** y comparte su nombre.
- Es el límite de aislamiento principal: developers, apps y API products **no se comparten entre orgs**.
- Dos tipos: **paid** (producción) y **evaluación** (temporal, self-service).

Patrón habitual: **una org por etapa** (`empresa-dev`, `empresa-prod`) cuando se necesita aislamiento fuerte de credenciales y datos de developer; o **una org con varios environments** cuando se quiere compartir el catálogo de products.

## Environment

Un environment es el espacio donde se **despliega** un API proxy. Un proxy no es alcanzable hasta que se despliega en al menos un environment.

Recursos con scope de environment:

| Recurso | Notas |
|---|---|
| API proxies desplegados | Hasta **6.000 por environment** en Apigee X |
| Shared flows | Hasta **75 por environment** |
| TargetServers | Hasta **8.000 por environment** |
| KeyValueMaps | Hasta **900 con scope environment** |
| Caches | Hasta **100 por environment** |
| Keystores | **100**; Truststores: **1.000** |
| Flow hooks | 4 puntos: PreProxy, PostProxy, PreTarget, PostTarget |
| Debug sessions | Máx. **100 sesiones/minuto** |

Límite: hasta **85 environments por organización**.

### Tipos de environment (Apigee X)

> [!IMPORTANT]
> Confirmado en la documentación oficial: existen los tipos **Base**, **Intermediate** y **Comprehensive**, y el tipo determina **qué políticas puedes usar**, no solo qué analytics tienes:
>
> - **Solo los entornos Intermediate y Comprehensive admiten políticas Extensible.** Un entorno Base solo puede ejecutar proxies **Standard** — lo que en la práctica excluye `VerifyAPIKey`, `OAuthV2` y `Quota`. Ver [Standard vs. Extensible](../02-politicas/00-catalogo-de-politicas.md#standard-vs-extensible-no-es-solo-una-etiqueta-de-calidad).
> - Usar una política Extensible en un proxy convierte automáticamente ese proxy en **Extensible**, con implicaciones de coste según tu modelo de licencia (Pay-as-you-go o Subscription).
> - En **Pay-as-you-go**, un API product debe incluir proxies extensibles (con flow hooks) o políticas extensibles (`VerifyAPIKey`, `OAuthV2`) — un proxy puramente Standard no se puede empaquetar en un producto.
>
> Verifica el catálogo de entitlements vigente para tu modelo de facturación antes de elegir el tipo de entorno, porque condiciona directamente el coste.

## Environment group

> [!IMPORTANT]
> Los hostnames se definen en el **environment group**, nunca en el environment individual. Este es el reemplazo de los *virtual hosts* de Apigee Edge.

- Un environment group tiene una lista de **hostnames** (hasta **100 por grupo**).
- Contiene uno o más environments (hasta **100 attachments**).
- Apigee enruta la petición entrante al environment del grupo cuyo hostname coincide con el `Host` de la petición.
- Límite: **85 environment groups por organización**.

### Regla de enrutamiento

```
Host: api.empresa.com
   │
   ├─ ¿Qué environment group declara ese hostname?  →  grupo "externo"
   │
   ├─ ¿Qué environments están adjuntos al grupo?     →  [prod]
   │
   └─ ¿Qué proxy desplegado en prod tiene un basepath que empareja
      con la ruta de la petición?                    →  ProxyEndpoint
```

Un mismo environment puede pertenecer a varios grupos. Eso permite exponer el mismo despliegue por un hostname público y otro interno, con TLS y políticas de red distintas.

> [!WARNING]
> Si dos proxies desplegados en el mismo environment declaran basepaths que se solapan (por ejemplo `/v1/` y `/v1/pedidos`), el emparejamiento es por el **basepath más específico**. Evita solapamientos ambiguos: son una fuente clásica de bugs difíciles de diagnosticar.

## Despliegue y revisiones

- Cada guardado de un proxy crea una **revisión** numerada.
- Se retienen hasta **250 revisiones** por proxy y por shared flow.
- Se despliega **una revisión concreta en un environment concreto**.
- Un proxy puede estar en la revisión 12 en `dev` y en la 9 en `prod` simultáneamente.

```bash
# Desplegar la revisión 12 del proxy "pedidos-v1" en el entorno "prod"
apigeecli apis deploy \
  --name pedidos-v1 --rev 12 \
  --org "$ORG" --env prod \
  --ovr --wait \
  --token "$(gcloud auth print-access-token)"
```

El flag `--ovr` (override) fuerza un despliegue *seamless* que reemplaza la revisión activa sin ventana de indisponibilidad.

## Estrategia recomendada

| Necesidad | Diseño |
|---|---|
| Etapas dev/test/prod con el mismo catálogo de products | 1 org, 3 environments, 1 environment group por etapa |
| Aislamiento total de credenciales entre etapas | 1 org por etapa |
| Exponer prod interna y externamente | 1 environment `prod` en 2 environment groups |
| Multi-tenant por unidad de negocio | Environments separados + prefijos de basepath por unidad |

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/environments-overview>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/organization-structure>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
