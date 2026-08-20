---
id: devops-ciclo-de-vida
titulo: Ciclo de vida de la API
area: devops
tags: [ciclo-de-vida, promocion, entornos, revisiones, source-control]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/fundamentals/api-development-lifecycle
revisado: 2026-08-20
---

# Ciclo de vida de la API

## Fases

```
Diseñar  →  Desarrollar  →  Probar  →  Desplegar  →  Publicar  →  Monitorizar  →  Retirar
```

> [!NOTE]
> Estas siete fases son una organización propia de este documento, pensada para un flujo de trabajo completo con control de versiones. La documentación oficial de Google estructura el ciclo de vida de forma más simple: **Developing** (desarrollo en la nube vía Apigee UI, o desarrollo local con Apigee en VS Code), **Deploying** (como tipo `Proxy` o como tipo `Archive`), **Adding policies**, **Promoting to production**, **Scripting deployment** vía la API de Apigee, y **Managing environment resources**. Los datos verificados de esa estructura oficial están incorporados en las secciones de abajo.

## 1. Diseñar

El contrato primero. La spec **OpenAPI es la fuente de verdad**, no el código del proxy:

- Se usa para generar la documentación del developer portal.
- Se usa en `OASValidation` para validar peticiones en runtime.
- Permite trabajar en paralelo a los equipos de frontend y backend.

```
apis/
└── pedidos/
    ├── openapi.yaml          ← el contrato
    └── apiproxy/             ← la implementación
```

## 2. Desarrollar

> [!IMPORTANT]
> **Antipatrón documentado: gestionar recursos de Apigee sin control de versiones.**
> Editar proxies directamente en la consola de Google Cloud es aceptable para explorar. Como forma de trabajo es insostenible: no hay historial, ni revisión por pares, ni forma de reproducir un despliegue, ni de saber quién cambió qué.

### Estructura de repositorio recomendada

```
mi-plataforma-apis/
├── apis/
│   ├── pedidos-v1/
│   │   ├── apiproxy/
│   │   ├── openapi.yaml
│   │   └── test/
│   └── clientes-v1/
├── sharedflows/
│   ├── sf-seguridad/
│   └── sf-logging/
├── config/
│   ├── dev/
│   │   ├── targetservers.json
│   │   ├── kvms.json
│   │   └── products.json
│   ├── test/
│   └── prod/
├── .github/workflows/
│   └── deploy.yml
└── README.md
```

Clave del diseño: **el bundle es idéntico en los tres entornos**. Lo que cambia son los `TargetServers` y los KVM, que se resuelven por entorno. Ver [TargetEndpoints](../01-proxies/05-target-endpoints-y-servidores.md).

### Framework-style coding

Recomendación de Google: guarda los recursos del proxy en tu propio sistema de control de versiones para poder reutilizarlos entre entornos de desarrollo locales. Implementa funciones especializadas y reutilizables (DRY):

```
policies/
├── EV-ExtraerParametrosPeticion.xml    ← una responsabilidad, reutilizable
├── AM-ConstruirRespuestaError.xml
└── JS-NormalizarPayload.xml
```

> [!TIP]
> **Elimina políticas y recursos sin usar.** Google señala explícitamente que ralentizan el despliegue. Un bundle con 40 políticas de las que 12 no se referencian en ningún flujo es deuda que se paga en cada deploy.

## 3. Probar

| Nivel | Qué prueba | Herramienta |
|---|---|---|
| Unitario | Lógica JavaScript aislada | Jest / Mocha en CI |
| Contrato | Que la respuesta cumple la spec | Comparación contra OpenAPI |
| Integración | Proxy desplegado en `dev` | `curl`, Newman/Postman, `apickli` |
| Carga | Latencia y cuotas bajo carga | k6, JMeter |
| Seguridad | Threat protection y auth | Casos de ataque en CI |

Ejemplo mínimo de test de integración:

```bash
#!/usr/bin/env bash
set -euo pipefail

BASE="https://${HOST}/pedidos/v1"

# 1. Sin API key → 401
codigo=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/pedidos")
[[ "$codigo" == "401" ]] || { echo "FALLO: esperaba 401, recibí $codigo"; exit 1; }

# 2. Con API key válida → 200
codigo=$(curl -s -o /dev/null -w '%{http_code}' -H "x-api-key: $API_KEY" "$BASE/pedidos")
[[ "$codigo" == "200" ]] || { echo "FALLO: esperaba 200, recibí $codigo"; exit 1; }

# 3. Health sin auth → 200
codigo=$(curl -s -o /dev/null -w '%{http_code}' "$BASE/health")
[[ "$codigo" == "200" ]] || { echo "FALLO: health devolvió $codigo"; exit 1; }

echo "Todos los tests pasan"
```

## 4. Desplegar

Cada guardado crea una **revisión** numerada e inmutable. Se retienen **250 revisiones** por proxy.

```
Revisión 12 desplegada en dev
Revisión  9 desplegada en prod   ← coexisten sin problema
```

### Promoción entre entornos

> [!IMPORTANT]
> **Promociona el mismo artefacto, no el mismo código.**
> Empaqueta el bundle una vez, súbelo, y despliega **esa misma revisión** en dev, luego test, luego prod. Si reconstruyes el bundle en cada etapa, lo que llega a producción no es exactamente lo que probaste.

```bash
# 1. Subir una vez → devuelve el número de revisión
REV=$(apigeecli apis create bundle --name pedidos-v1 --proxy-folder ./apiproxy \
        --org "$ORG" --token "$TOKEN" | jq -r '.revision')

# 2. Desplegar esa revisión en cada entorno
for ENV in dev test prod; do
  apigeecli apis deploy --name pedidos-v1 --rev "$REV" \
    --org "$ORG" --env "$ENV" --ovr --wait --token "$TOKEN"
done
```

El flag `--ovr` fuerza un despliegue *seamless*: reemplaza la revisión activa sin ventana de indisponibilidad.

### Versionado de la API

El versionado va en el **basepath**, no en revisiones de Apigee:

```
/pedidos/v1   →  proxy "pedidos-v1"
/pedidos/v2   →  proxy "pedidos-v2"
```

Las revisiones son un detalle de despliegue interno; `v1`/`v2` es el contrato público. Nunca cambies el comportamiento de `v1`: crea `v2`.

### Gestionar recursos entre entornos

> [!IMPORTANT]
> Confirmado en la documentación oficial: **las API keys emitidas en un entorno de test no son válidas en producción, y viceversa.** No es solo buena práctica — es una separación real de datos entre entornos. No esperes que una key probada en `test` funcione en `prod` sin volver a provisionarla.

Recomendación oficial de Google para mantener las configuraciones de proxy **independientes del entorno** al promocionar:

| Recurso | Cómo desacoplarlo |
|---|---|
| **KVMs con scope de entorno** | Usa convenciones de nombres consistentes para que el proxy lea datos sin cambios de configuración entre entornos |
| **URLs de backend** | Usa `TargetServer` para tener TargetEndpoints independientes del entorno — ver [targets](../01-proxies/05-target-endpoints-y-servidores.md) |
| **Targets de ServiceCallout** | Pueden variar por entorno (p. ej. un ServiceCallout en test que consume un servicio de demostración) |
| **Condicionales con `environment.name`** | Para lógica que debe variar por entorno sin tocar recursos externos: `<Condition>environment.name = "test"</Condition>` |

Recomendación adicional de Google: **itera solo en el entorno de test**, y haz el mínimo de cambios necesarios en los proxies ya desplegados en producción.

## 5. Publicar

1. Crear o actualizar los **API products** que empaquetan el proxy.
2. Publicar en el **developer portal** con la spec OpenAPI.
3. Comunicar el cambio a los consumidores.

> [!TIP]
> **Versiona también los API products en Git.** Son configuración de negocio con impacto en facturación y acceso: merecen PR y trazabilidad. Ver [API products](../04-publicacion/01-api-products.md).

## 6. Monitorizar

Ver [analytics y monitoreo](../05-operacion/03-analytics-monitoreo.md). Lo mínimo tras cada despliegue:

- Error rate por proxy y revisión.
- Latencia p50/p95/p99.
- Overhead de Apigee (total − backend).
- Que la revisión desplegada es la esperada (endpoint `/health` que la devuelve).

## 7. Retirar

```
1. Anunciar la deprecación con fecha
2. Añadir cabeceras de deprecación en la respuesta
3. Monitorizar el tráfico residual por client_id
4. Contactar a los consumidores que quedan
5. Despublicar del portal
6. Despublicar el proxy del entorno
7. Eliminar (o conservar por auditoría)
```

Cabeceras de deprecación:

```xml
<AssignMessage name="AM-Deprecacion">
    <Add>
        <Headers>
            <Header name="Deprecation">true</Header>
            <Header name="Sunset">Wed, 31 Dec 2026 23:59:59 GMT</Header>
            <Header name="Link">&lt;https://api.empresa.com/pedidos/v2&gt;; rel="successor-version"</Header>
        </Headers>
    </Add>
    <IgnoreUnresolvedVariables>true</IgnoreUnresolvedVariables>
    <AssignTo createNew="false" transport="http" type="response"/>
</AssignMessage>
```

> [!WARNING]
> El paso 3 no es opcional. Despublicar un proxy con tráfico residual porque "ya avisamos por email hace seis meses" es la forma más común de romper la integración de un cliente. Filtra Analytics por `client_id` y confirma que está a cero.

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/api-development-lifecycle> (consultada directamente, contenido completo)
- <https://docs.apigee.com/api-platform/fundamentals/best-practices-api-proxy-design-and-development>
- <https://docs.apigee.com/api-platform/antipatterns/no-scm>
