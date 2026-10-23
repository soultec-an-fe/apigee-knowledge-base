---
id: hybrid-cassandra
titulo: Apigee hybrid — Cassandra en producción, escalado y backups
area: hybrid
tags: [hybrid, cassandra, replicacount, storageclass, backup, csi, restore, external-datastore, escalado]
aplica_a: [apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cassandra-production
revisado: 2026-10-23
---

# Apigee hybrid — Cassandra en producción, escalado y backups

> **Fecha de corte: 23 de octubre de 2026.** Versión documentada: hybrid **v1.17**.

**Cassandra es el único componente de hybrid con estado.** Los demás (MART, controller, watcher, Istio, runtime, synchronizer, UDCA, telemetría, cert-manager) **no guardan datos**: para recuperarlos basta con reinstalarlos con el mismo `overrides.yaml`. La guía de backups lista Redis como *datastore* junto a Cassandra, pero después afirma que todos los componentes salvo Cassandra son *stateless* y no describe ningún backup de Redis. Lo que Cassandra guarda está en la [arquitectura](01-arquitectura-y-planificacion.md#componentes-del-plano-de-runtime): KMS, KVM, OAuth, cuotas, caché…

## Configuración de producción

| Ajuste | Recomendación oficial |
|---|---|
| **Zonas de disponibilidad** | **3**. Si cae una zona, las otras dos siguen respondiendo; si caen dos o más, Cassandra deja de dar servicio. |
| `cassandra.replicaCount` | **Múltiplo de 3**, porque el factor de replicación de todos los keyspaces es 3. Se dimensiona con pruebas de carga. Puede variar entre regiones y ampliarse después. |
| `cassandra.storage.storageclass` | **SSD** en producción. **No se puede cambiar** después de crear el cluster. |
| `cassandra.storage.storageSize` | **Al menos 500 Gi** por pod. Se puede ampliar después (*expand persistent volumes*). |
| `cassandra.resources.requests` | Al menos **7 CPU y 15 Gi** por pod, ajustados al tráfico |
| Heap | La guía añade ajustes de heap en el `overrides.yaml` |

Todos los ajustes de almacenamiento del `overrides.yaml` son **por pod**. Se aplican con `helm upgrade datastore apigee-datastore/ …`. Si Helm responde `"datastore" has no deployed releases`, usa `install` en lugar de `upgrade`.

> [!NOTE]
> **Cifras que no coinciden entre páginas oficiales:** la [configuración mínima de cluster](01-arquitectura-y-planificacion.md#dimensionamiento-mínimo) pide nodos de 8 CPU y **32 GB** en producción; la página de escalado de Cassandra recomienda empezar con 8 cores y **30 GB**; la de producción, pods de al menos 7 CPU y **15 Gi**. Las dos primeras hablan del nodo y la tercera del pod, pero la diferencia entre 30 y 32 GB queda sin explicar.

## Escalado

- **Horizontal:** sube `cassandra.replicaCount`, en múltiplos de 3, y asegúrate de que el *node pool* `apigee-data` tiene capacidad.
- **Vertical:** el tamaño de las máquinas de un *node pool* no se puede cambiar.
  1. Crea un *node pool* nuevo, más grande.
  2. Apunta Cassandra a él en el `overrides.yaml`.
  3. Sube `requests.cpu` y `requests.memory`.
  4. Aplica los cambios.

## Modo *external datastore*: Cassandra en otro cluster

Cassandra puede correr en un cluster de Kubernetes **separado** del runtime:

| Componente | Cluster de Cassandra | Cluster de runtime |
|---|---|---|
| cert-manager, CRDs, `apigee-operator` | Sí | Sí |
| `apigee-datastore` | Sí, con los pods | Sí, con **`replicaCount: 0`** |
| Telemetry, redis, ingress-manager, org, env, virtualhost | No | Sí |

En el cluster de runtime, el operator crea un *Service headless* y *Endpoints* que apuntan al anillo de Cassandra. Se recomienda habilitar la **sincronización dinámica de endpoints**.

**Requisitos:**

- Conectividad privada por **TCP/9042**, por ejemplo con Shared VPC.
- **La misma región** para los dos clusters: cada viaje de ida y vuelta entre ellos se suma a la latencia de cada petición.
- **Copiar el secreto `apigee-ca`** del cluster de Cassandra al de runtime **antes** de instalar el operator en el de runtime.
- Las mismas credenciales de Cassandra en los dos clusters.

## Backups

> [!CAUTION]
> **Los backups de Cassandra no están habilitados por defecto.** Habilítalos.
> - Sirven para **recuperación ante desastres**, no para deshacer cambios puntuales.
> - Desde la versión 1.14, los **Guardrails bloquean una actualización** si el backup no está habilitado (`cassandra_backup_enabled`). Con backup por CSI, también la bloquean si no hay un backup de las **últimas 24 horas** (`cassandra_recent_backup_csi`).

| Método | Destino |
|---|---|
| **Cloud Storage** | Un bucket de tu proyecto, con la cuenta `apigee-cassandra` |
| **Servidor remoto** | Un directorio en un servidor que tú indicas |
| **CSI** (*snapshots* de volumen) | Mediante el driver CSI del cluster |

- **Contenido de cada backup:**
  - el esquema, incluidos los keyspaces de Apigee;
  - los *tokens* de partición de cada nodo;
  - un *snapshot* de los datos.
- **Programación:** con un *job* de Kubernetes, según el horario del `overrides.yaml`. Los *timestamps* van en **UTC**.
- **Fuera del alcance de estos backups:**
  - el **`overrides.yaml`**, que debes guardar tú;
  - los Secrets, Certificates y ConfigMaps de Kubernetes, que tienen sus propias herramientas.

La **restauración** es distinta en una sola región y en multirregión: sigue la guía específica, y revisa los logs de restauración.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Configure Cassandra for production (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cassandra-production>, contenido completo.
- Scaling Cassandra (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cassandra-scaling>, contenido completo.
- External datastore (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cassandra-external>, topología y requisitos.
- Cassandra backup overview (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/cassandra-backup-overview>, contenido completo.
- Guardrails (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/guardrails>, comprobaciones de backup.
