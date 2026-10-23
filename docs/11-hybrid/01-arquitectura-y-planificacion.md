---
id: hybrid-arquitectura
titulo: Apigee hybrid — arquitectura, datos, puertos y dimensionamiento
area: hybrid
tags: [hybrid, arquitectura, runtime-plane, management-plane, synchronizer, mart, cassandra, apigee-connect, puertos, node-pools, versiones]
aplica_a: [apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/what-is-hybrid
revisado: 2026-10-23
---

# Apigee hybrid — arquitectura, datos, puertos y dimensionamiento

> **Fecha de corte: 23 de octubre de 2026.** Versión documentada: **hybrid v1.17**, la más reciente. Versiones con soporte en la fecha de corte: **1.14, 1.15, 1.16 y 1.17**. Las 1.13 y anteriores ya no tienen soporte.

**Apigee hybrid** divide Apigee en dos planos:

- un **plano de gestión** en Google Cloud, mantenido por Google: la UI, la API de gestión y Analytics;
- un **plano de runtime** que **tú** instalas y operas en un **cluster de Kubernetes** soportado (GKE, Google Distributed Cloud sobre VMware o bare metal, AKS, EKS, OpenShift), on-premises o en otra nube.

**Todo el tráfico de las APIs se procesa dentro de tu red.** Se elige hybrid sobre todo por cumplimiento (el runtime on-premises), por estrategia multinube o para estar cerca de los backends. Ver la [comparativa de ediciones](../00-fundamentos/02-ediciones-y-comparativa.md).

## Componentes del plano de runtime

| Componente | Función |
|---|---|
| **Message Processor** (`apigee-runtime`) | Ejecuta los proxies: procesa cada petición |
| **Synchronizer** | Consulta periódicamente el plano de gestión, descarga el **contrato** (la configuración del entorno) y lo guarda en local como JSON para que lo usen los MP |
| **Cassandra** | Almacén de datos de runtime, desplegado como *StatefulSet* |
| **MART** (*Management API for Runtime data*) | Atiende las llamadas de la API de gestión sobre datos de runtime: productos, apps, KVM, KMS, caché. Es *stateless*: lee y escribe en Cassandra. |
| **Apigee Connect** | Canal seguro entre el plano de gestión y MART. **Lo inicia el runtime**, por lo que no hay que abrir puertos entrantes. |
| **UDCA** | Recoge Analytics y Debug y los envía al plano de gestión |
| **Watcher** | Aplica los cambios de *virtual hosts* (environment groups) al ingress |
| **Ingress gateway** (`apigee-ingressgateway`) | Recibe las peticiones de los clientes |
| **Telemetría** (métricas y fluentd) | Métricas y logs hacia Cloud Monitoring y Cloud Logging |

**El contrato incluye:**

- despliegues de proxies y shared flows;
- flow hooks;
- información del entorno y recursos compartidos;
- target servers;
- configuración TLS;
- **nombres** de KVM;
- máscaras de datos.

Con el contrato en local, **el runtime sigue funcionando aunque se corte la conexión con el plano de gestión**, con la última configuración descargada.

**Cassandra guarda:**

- KMS: apps, keys y tokens;
- KVM;
- OAuth;
- datos de MART;
- datos de monetización;
- **contadores de Quota**;
- caché de respuestas.

### Cómo llega una llamada de gestión al runtime

1. Llamas a `apigee.googleapis.com`. El **Management Server** autentica y autoriza la llamada.
2. El Management Server la reenvía a MART **a través de Apigee Connect**, con un token generado con una cuenta de servicio.
3. MART valida la petición, lee o escribe en Cassandra y responde.

**Nunca se llama a MART directamente, y MART no recibe tráfico de APIs.**

## Qué dato vive dónde

| Dónde | Datos |
|---|---|
| **Plano de gestión** (replicado al runtime por el Synchronizer) | API proxies, TargetServers, truststores y keystores |
| **Solo en el plano de gestión** | Logs de auditoría, RBAC, usuarios |
| **Del runtime al plano de gestión** (asíncrono) | Analytics, eventos de estado de despliegue, datos de Debug |
| **Del runtime a Cloud Operations** (tu proyecto) | Logs y métricas |
| **Runtime (Cassandra)** | Lo de la sección anterior |

Con **residencia de datos**, puedes elegir la región de los datos del plano de gestión.

## Puertos

**Internos al cluster:**

| Origen → destino | Puerto | Seguridad |
|---|---|---|
| MART, MP, Synchronizer → Cassandra | TCP/9042 | TLS |
| Cassandra ↔ Cassandra | **TCP/7001** | mTLS (también **entre regiones**) |
| Apigee Connect → MART | TCP/8443 | TLS |
| Ingress → Message Processor | TCP/8443 | TLS (certificado autofirmado generado por Apigee) |
| MP → fluentd (datos de Analytics y logs) | TCP/20001 | mTLS |
| Prometheus → servicios | TCP/7070, TCP/8843 | TLS |
| Watcher → pods de ingress | TCP/8843 | TLS |

**Salientes, todos por TCP/443 hacia Google:**

| Componente | Destino |
|---|---|
| Synchronizer | `apigee.googleapis.com` |
| UDCA | `apigee.googleapis.com` y `storage.googleapis.com` |
| Apigee Connect | `apigeeconnect.googleapis.com` (canal bidireccional) |
| Prometheus | `monitoring.googleapis.com` |
| fluentd | `logging.googleapis.com` |
| MART y otros | `iamcredentials.googleapis.com` |

**Entrante:** clientes → ingress, en el puerto que configures (Google recomienda 443). Si usas *forward proxy* o firewall de salida, permite esos dominios. Ver [*Allow Google Cloud URLs*](https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/allow-gcp-urls).

## Dimensionamiento mínimo

Dos *node pools* dedicados:

| | `apigee-data` (Cassandra, *stateful*) | `apigee-runtime` (MP y demás, *stateless*) |
|---|---|---|
| Nodos | 1 por zona (3 por región) | 1 por zona (3 por región) |
| CPU | 8 en prod, 4 en no prod | 8 en prod, 4 en no prod |
| RAM (GB) | 32 en prod, 16 en no prod | 32 en prod, 16 en no prod |
| Disco | Dinámico; **mínimo 2000 IOPS** con SAN o disco local. **NFS no recomendado.** | — |
| Red | 1 Gbps por máquina | 1 Gbps por máquina |

**Requisitos de Cassandra:**

- **Latencia:** p99 por debajo de **100 ms**.
- **Ancho de banda:** al menos **1 Gbps** por instancia; más en producción. Cassandra usa *gossip* y habla con varios nodos en cada lectura o escritura.
- **NTP sincronizado en todos los pods y regiones.** Cassandra resuelve conflictos por *timestamp*: un desfase de reloj produce **inconsistencias de datos**.
- **Multirregión:**
  - conectividad privada (VPN o VPC);
  - subredes que no se solapen;
  - firewall abierto entre nodos, **solo en el puerto 7001**.

> [!TIP]
> Para producción, Google recomienda **al menos dos clusters**.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- What is Apigee hybrid? (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/what-is-hybrid>, contenido completo.
- Where is your data stored? (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/where-data>, contenido completo.
- Secure ports usage (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/ports>, tablas completas.
- Minimum cluster configurations (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cluster-overview>, contenido completo.
- The big picture (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/big-picture>, contenido completo.
