---
id: fundamentos-arquitectura
titulo: Arquitectura de Apigee
area: fundamentos
tags: [arquitectura, runtime, control-plane, networking, psc, cassandra]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://cloud.google.com/apigee/docs/api-platform/architecture/overview
revisado: 2026-08-20
---

# Arquitectura de Apigee

Apigee se divide en dos planos. Entender la frontera entre ambos explica casi todos los comportamientos de latencia, despliegue y disponibilidad.

## Plano de control (control plane)

Gestionado por Google. Contiene:

- **API de gestión** (`apigee.googleapis.com`): CRUD de proxies, productos, developers, apps, KVMs, keystores.
- **Consola de Google Cloud**: la UI de Apigee.
- **Almacén de configuración**: revisiones de proxies y shared flows.
- **Pipeline de analytics**: agrega los datos que emiten los runtimes.
- **Sincronizador**: distribuye la configuración desplegada hacia el plano de runtime.

Una caída del plano de control **no tumba el tráfico**: los proxies ya desplegados siguen sirviendo. Lo que se ve afectado son despliegues, cambios de configuración y consultas de analytics.

## Plano de runtime (runtime plane)

Donde vive el tráfico real.

| Componente | Función |
|---|---|
| **Message Processor (MP)** | Ejecuta el pipeline del proxy: flujos, políticas, llamada al target. Es el que consume CPU y memoria. |
| **Cassandra** | Almacén de runtime: KVMs, tokens OAuth, contadores de cuota, credenciales de apps, caché. |
| **Ingress / Envoy** | Termina TLS y enruta por hostname hacia el environment correcto según el environment group. |
| **Synchronizer** | Descarga del plano de control la configuración desplegada. |
| **UDCA** (hybrid) | Universal Data Collection Agent: envía analytics y debug al plano de control. |

En **Apigee X** todo esto lo opera Google. En **hybrid**, los MP, Cassandra, el ingress y el UDCA corren en tu clúster de Kubernetes.

## Instancias y regiones

- Una **instancia** es un despliegue del runtime en una región concreta.
- Límite: **10 instancias por organización** (11 en hybrid) y **10 regiones por organización**.
- Multi-región da alta disponibilidad y menor latencia. Cassandra replica entre regiones.

> [!NOTE]
> Los **contadores de cuota distribuida** se sincronizan de forma asíncrona entre MPs y regiones. Con el intervalo de sincronización por defecto puede haber sobreconsumo transitorio. Ver [Quota](../02-politicas/01-traffic-management.md).

## Networking en Apigee X

Apigee X se despliega en una red gestionada por Google que se conecta a tu VPC. Dos modelos:

### 1. VPC Peering
Se reserva un rango CIDR (`/22` + `/28`) en tu VPC y se hace peering con la red de Apigee. Es el modelo clásico.

### 2. Private Service Connect (PSC) — recomendado
Sin peering ni consumo de rango CIDR. Se crean **endpoint attachments**:

- **Northbound (entrada)**: un Cloud Load Balancer externo apunta a un **NEG de Private Service Connect** que llega a la instancia de Apigee.
- **Southbound (salida)**: Apigee alcanza backends privados a través de un **service attachment** en tu VPC.

Límites relevantes: hasta **100 NEGs de PSC por proyecto** y **1.000 endpoint attachments por organización**.

## Camino de una petición

```
1. DNS  ─────────────► IP del Cloud Load Balancer
2. LB   ─────────────► termina TLS, reenvía al NEG/PSC de Apigee
3. Ingress Apigee ───► resuelve el hostname en el environment group
                       └─► elige el environment
4. Message Processor ► empareja el basepath con un ProxyEndpoint desplegado
5. ProxyEndpoint ────► PreFlow → Conditional Flows → PostFlow  (request)
6. RouteRule ────────► selecciona el TargetEndpoint
7. TargetEndpoint ───► PreFlow → Flows → PostFlow  (request) → backend
8. Backend ──────────► responde
9. TargetEndpoint ───► PreFlow → Flows → PostFlow  (response)
10. ProxyEndpoint ───► PreFlow → Flows → PostFlow  (response)
11. Respuesta al cliente
12. PostClientFlow ──► solo MessageLogging / DataCapture (asíncrono)
```

El detalle del pipeline está en [flujos y pipeline](../01-proxies/02-flujos-y-pipeline.md).

## Implicaciones prácticas

- **El basepath es la clave de enrutamiento.** Google recomienda no superar **3.000 basepaths por environment o environment group**; por encima aumenta la latencia de *todos* los despliegues, nuevos y existentes.
- **Cassandra es el cuello de botella de las políticas con estado.** KVM, cachés y cuotas pegan contra Cassandra: úsalas con moderación y con TTL adecuados.
- **Un despliegue no es atómico entre regiones.** Durante un rollout pueden coexistir revisiones distintas en instancias distintas.
- **Los límites de payload son del MP.** Buffered 30 MB, streamed 10 MB. Ver [límites](../10-referencia/01-limites.md).

## Fuentes

- <https://cloud.google.com/apigee/docs/api-platform/architecture/overview>
- <https://cloud.google.com/apigee/docs/api-platform/reference/limits>
