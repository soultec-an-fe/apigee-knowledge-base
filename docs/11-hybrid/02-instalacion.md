---
id: hybrid-instalacion
titulo: Apigee hybrid — instalación con Helm y cuentas de servicio
area: hybrid
tags: [hybrid, instalacion, helm, overrides, service-accounts, workload-identity, vault, cert-manager, crds, synchronizer]
aplica_a: [apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/big-picture
revisado: 2026-10-23
---

# Apigee hybrid — instalación con Helm y cuentas de servicio

> **Fecha de corte: 23 de octubre de 2026.** Versión documentada: hybrid **v1.17**. Los comandos exactos cambian entre versiones: sigue siempre la guía oficial **de tu versión**. Este documento es el mapa, no el sustituto.

## Las tres partes

| Parte | Qué se hace |
|---|---|
| **1. Google Cloud y la UI** | Habilitar las APIs, crear la **organización** hybrid, un **entorno** y un **environment group** |
| **2. Instalar el runtime** | Los 11 pasos de la tabla siguiente |
| **3. Probar** | Exponer el ingress y desplegar un proxy de prueba |

## Parte 2, paso a paso

| Paso | Qué se hace | Notas |
|---|---|---|
| 1. Crear el cluster | GKE, Google Distributed Cloud (VMware o bare metal), AKS, EKS u OpenShift, en una versión soportada para tu versión de hybrid | Con los *node pools* `apigee-data` y `apigee-runtime` (ver [dimensionamiento](01-arquitectura-y-planificacion.md#dimensionamiento-mínimo)) |
| 2. Descargar los charts de Helm | **Helm v3.14.2 o superior** | Carpeta `$APIGEE_HELM_CHARTS_HOME` |
| 3. Crear el namespace `apigee` | — | — |
| 4. Crear las **cuentas de servicio** | Con la herramienta `create-service-account` (recomendada), la consola o `gcloud` | Ver abajo |
| 5. Autenticación de las cuentas de servicio | Secretos de Kubernetes, archivos JSON, Vault o **Workload Identity Federation** | Ver abajo |
| 6. Certificados TLS del ingress | Uno por environment group: `keystore_{ENV_GROUP}.pem` y `.key` en `apigee-virtualhost/certs` | La guía genera certificados autofirmados; en producción usa los de una CA |
| 7. Crear `overrides.yaml` | La configuración de toda la instalación: proyecto, organización, entornos, environment groups (`virtualhosts`), cuentas de servicio, Cassandra, ingress… | Es el archivo central: **versiónalo**, sin secretos |
| 8. Acceso al plano de control | Llamada `updateControlPlaneAccess` para autorizar la cuenta del **Synchronizer** (`apigee-synchronizer`, o `apigee-non-prod`) | Con residencia de datos, indica `CONTROL_PLANE_LOCATION` |
| 9. Instalar **cert-manager** | La guía de v1.17 usa **cert-manager v1.19.2** | — |
| 10. Instalar los **CRDs** de Apigee | `kubectl apply -k apigee-operator/etc/crds/default/ --server-side --force-conflicts --validate=false`, primero con `--dry-run=server` | — |
| 11. Instalar los charts | **En este orden:** ver la tabla de charts | Cada uno con `--dry-run` antes |

**Charts de Helm, en orden de instalación:**

| # | Release | Chart |
|---|---|---|
| 1 | `operator` | `apigee-operator/` |
| 2 | `datastore` | `apigee-datastore/` (Cassandra) |
| 3 | `telemetry` | `apigee-telemetry/` (métricas y logs) |
| 4 | `redis` | `apigee-redis/` |
| 5 | `ingress-manager` | `apigee-ingress-manager/` |
| 6 | `$ORG_NAME` | `apigee-org/` |
| 7 | Uno **por entorno** | `apigee-env/` (con `--set env=…`) |
| 8 | Uno **por environment group** | `apigee-virtualhost/` (con `--set envgroup=…`) |

> [!IMPORTANT]
> Los entornos y los environment groups se instalan **de uno en uno**. Los nombres de release de Helm deben ser **únicos** en todo el namespace. Si tienes un entorno y un environment group llamados `prod`, el release del grupo debe llamarse distinto (por ejemplo `prod-envgroup`).

## Cuentas de servicio

Cuentas de la tabla oficial de v1.17 (en esa versión no figura una cuenta propia para UDCA):

| Cuenta | Rol | Para qué |
|---|---|---|
| `apigee-cassandra` | `roles/storage.objectAdmin` | Backups de Cassandra en Cloud Storage |
| `apigee-guardrails` | `roles/serviceusage.serviceUsageViewer` | El pod de *guardrails* del chart `apigee-operator` comprueba que las APIs necesarias estén habilitadas |
| `apigee-logger` | `roles/logging.logWriter` | Logs. **Solo fuera de GKE.** |
| `apigee-mart` | `roles/apigeeconnect.Agent` | MART y Apigee Connect |
| `apigee-metrics` | `roles/monitoring.metricWriter` | Métricas |
| `apigee-mint-task-scheduler` | Ninguno | Cuotas recurrentes de monetización |
| `apigee-runtime` | Ninguno | Identidad del runtime ante servicios de Google (autenticación de Google, Cloud Trace, Jaeger) |
| `apigee-synchronizer` | `roles/apigee.synchronizerManager` | Descargar el contrato; también hace funcionar el *trace* |
| `apigee-watcher` | `roles/apigee.runtimeAgent` | Cambios de *virtual hosts* |

**Para demo o pruebas** se puede usar una sola cuenta, **`apigee-non-prod`**, con todos los roles: Connect Agent, Runtime Agent, Synchronizer Manager, Logs Writer, Monitoring Metric Writer, Service Usage Viewer y Storage Object Admin. **No en producción.**

> [!WARNING]
> **No reutilices el nombre de una cuenta de servicio borrada**: puede causar comportamientos inesperados. Si borras una, créala de nuevo con **otro** nombre.

### Métodos de autenticación

| Método | Dónde están las claves | Plataformas | Gestión |
|---|---|---|---|
| **Secretos de Kubernetes** | Secretos del cluster | Cualquiera | Rotación manual |
| **Archivos JSON** | Sistema de archivos local | Cualquiera | Rotación y distribución manuales |
| **HashiCorp Vault** | Vault | Cualquiera | Vault gestiona los secretos; la rotación sigue siendo manual |
| **Workload Identity Federation for GKE** | IAM de Google Cloud | **GKE** | **Sin archivos de clave** |
| **Workload Identity Federation (otras plataformas)** | IAM de Google Cloud | AKS, EKS, OpenShift y otras | **Sin archivos de clave** |

> [!TIP]
> Siempre que la plataforma lo permita, **usa Workload Identity Federation**: elimina las claves JSON de larga duración, que son el secreto más sensible de una instalación hybrid. Si no es posible, mejor Vault o secretos de Kubernetes que archivos sueltos. Esta recomendación es de este repositorio a partir de la tabla oficial.

## Parte 3: probar

1. **Exponer el ingress gateway** de Apigee: un *Service* de tipo LoadBalancer, o tu propio balanceador delante.
2. **Desplegar un proxy de prueba** y llamarlo con el hostname del environment group.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- The big picture (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/big-picture>.
- Pasos de instalación 1 a 11 (v1.17), `install-create-cluster` … `install-helm-charts`: <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/install-before-begin>, títulos, comandos clave y orden de los charts.
- Service accounts and roles (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/sa-about>, tabla completa.
- Service account authentication methods (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/sa-authentication-methods>, tabla completa.
- Enable control plane access (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/install-enable-control-plane-access>.
