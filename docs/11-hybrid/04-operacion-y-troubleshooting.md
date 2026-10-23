---
id: hybrid-operacion
titulo: Apigee hybrid — actualización, escalado, guardrails y troubleshooting
area: hybrid
tags: [hybrid, upgrade, escalado, hpa, guardrails, automated-issue-surfacing, apigeeissues, troubleshooting, cassandra, ingress]
aplica_a: [apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/upgrade
revisado: 2026-10-23
---

# Apigee hybrid — actualización, escalado, guardrails y troubleshooting

> **Fecha de corte: 23 de octubre de 2026.** Versión documentada: hybrid **v1.17** (v1.17.1).

## Actualizar

- **Mismo procedimiento** para versiones menores (1.16 → 1.17) y parches (1.17.0 → 1.17.1).
- **Sin saltos:** desde 1.15 o anteriores, **primero a 1.16**.
- **Requisitos:**
  - Helm v3.14.2 o superior;
  - `kubectl` y cert-manager en versiones soportadas (la guía incluye la actualización de cert-manager).
- **Puede haber corte de servicio:** al actualizar el controller, **todos** los despliegues de Apigee hacen un *rolling restart*. Para reducir el impacto, ten **al menos dos clusters** y actualízalos uno tras otro, sin dejar pasar mucho tiempo entre ellos.
- **Durante la actualización:** no hace falta congelar los cambios en el plano de gestión, salvo las pausas puntuales que indica la guía.
- **Antes de empezar:** un backup de Cassandra **reciente**. Los Guardrails lo exigen.

**Novedades de la 1.17:**

- soporte de **MCP** (ver [MCP en Apigee](../07-ai-gateway/02-mcp-en-apigee.md));
- **rotación de la CA raíz** de la comunicación interna;
- **TLS 1.3**;
- *forward proxy* para las políticas de IA (Model Armor, caché semántica);
- endpoints **PSC** para la caché semántica.

## Escalado

| Servicio | Implementado como | Cómo se escala |
|---|---|---|
| Cassandra | CRD `ApigeeDatastore` | Ver [Cassandra](03-cassandra.md#escalado) |
| Ingress | Deployment | HPA de Cloud Service Mesh |
| Logger | DaemonSet | Un pod por nodo: escala con el cluster |
| MART, Apigee Connect, Watcher | CRD `ApigeeOrganization` | `replicaCountMin`, `replicaCountMax` y `targetCPUUtilizationPercentage` en las secciones `mart`, `connectAgent` y `watcher` |
| Runtime, Synchronizer, UDCA | CRD `ApigeeEnvironment` | Las mismas propiedades en `runtime`, `synchronizer` y `udca` |

Los valores del `overrides.yaml` se aplican a **todos los entornos**. Para escalar distinto por entorno o por componente, por ejemplo `maxReplicas` del runtime de un solo entorno, hay que usar `kubectl patch` sobre los recursos.

## Guardrails

Cada `helm install` o `helm upgrade` lanza antes un **pod temporal de Guardrails**, que prueba la configuración contra la instancia. Por ejemplo, comprueba la conectividad con el plano de control.

- **Si pasa**, el pod se elimina y Helm aplica los cambios.
- **Si falla**, el pod se queda en estado de **error** para que lo diagnostiques. Revisa sus logs.

Se puede desactivar con `helm … --no-hooks`, **pero solo de forma temporal**. Necesita la cuenta `apigee-guardrails`, con `roles/serviceusage.serviceUsageViewer`.

## Automated Issue Surfacing (AIS)

Desde la 1.10, el **watcher** revisa cada **60 s** el plano de control y la API de Kubernetes en busca de problemas **conocidos**. Cuando encuentra uno, crea un recurso **`ApigeeIssue`** con un enlace a la guía de solución, y lo borra al resolverse.

```bash
kubectl -n apigee get apigeeissues
kubectl -n apigee describe apigeeissues/NOMBRE
```

- **Intervalo:** se cambia con `watcher.args.issueScanInterval`.
- **Desactivar:** `watcher.args.enableIssueScanning: false`.
- Los dos ajustes se aplican actualizando el chart `apigee-env` de cada entorno.

| Código AIS | Problema |
|---|---|
| `AIS_VIRTUALHOST_MISSING_ENVGROUP` | Un *virtual host* del `overrides.yaml` sin environment group |
| `AIS_VIRTUALHOST_MISSING_SELECTOR` | Falta el *selector* del ingress en el *virtual host*. Con el ingress de Apigee debe ser `app: apigee-ingressgateway`; si falta, el despliegue falla con «*Instance … is not reporting status*». |
| `AIS_INGRESS_CERT_MISMATCH` | El certificado del ingress no corresponde a la clave o al hostname |
| `AIS_INGRESS_CERT_EXPIREY` | El certificado del ingress caduca en **menos de 14 días**, o ya caducó |
| `AIS_INGRESS_MTLS_CA_CERT_EXPIREY` / `…_INVALID` | La CA del mTLS de entrada está a punto de caducar, ha caducado, no está en PEM o está mal formada |

## Playbooks frecuentes

| Síntoma | Causas documentadas |
|---|---|
| **Sin conectividad entre el runtime y el plano de control**: productos y apps vacíos en la UI, despliegues que no terminan | Sin ruta a internet; endpoints de Apigee no permitidos en el firewall; **Private Google Access** sin habilitar en la subred (GKE) |
| **Pod de Cassandra en `CrashLoopBackOff`** | DNS (`UnknownHostException`); URL de imagen incorrecta; sin conexión con el *seed* durante una expansión; **puertos 7000 o 7001 ocupados**; IP duplicada en el anillo |
| **Pod de Cassandra que no arranca** | Cambio de capacidad de almacenamiento; cambios del `overrides.yaml` que no se aplicaron; falta CPU o memoria; volumen no creado; en EKS, **falta el driver CSI de EBS**; un volumen persistente con datos de otro cluster |
| **Disco de Cassandra** | Menos del **50 %** libre |
| **Pods de métricas en `CrashLoopBackOff`** | Falta memoria; o faltan `metrics.app.resources.requests` y `limits.cpu` en el `overrides.yaml` |
| **Message Processor sin configuración** | El Synchronizer no conecta con el plano de gestión (revisa el `contractProvider` si lo sobrescribiste); un MP nuevo (por escalado o reinicio) no llega al Synchronizer |
| **Ingress en el puerto 80** | **No se admite desde la 1.9** |
| **Fallo de despliegue por un webhook** | Ha caducado el certificado de `apigee-webhook-service.apigee-system.svc`; aparece en los logs de `apigee-watcher` |
| **«*No active runtime pods*»**, *Datastore Error* o *Internal Server Error* en la UI | **Pods de Cassandra caídos**: el runtime no puede hablar con la base de datos. O Cassandra con **una sola réplica**, que es un punto único de fallo. |

Los playbooks de runtime y de red comunes con X (504, 503, 502, PSC…) están en [14-troubleshooting](../14-troubleshooting/01-errores-de-runtime.md).

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Upgrading Apigee hybrid to version 1.17: <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/upgrade>, cambios, requisitos y limitaciones.
- Scale and autoscale runtime services (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/scale-and-autoscale>, contenido completo.
- Guardrails (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/guardrails>, contenido completo.
- Automated issue surfacing (v1.17): <https://docs.cloud.google.com/apigee/docs/hybrid/v1.17/automated-issue-surfacing>, contenido completo.
- Playbooks de hybrid (`troubleshoot/playbooks/hybrid/*`, `cassandra/*`, `no-network-connectivity`, `ts-message-processor`, `vh-missing-*`, `ingress-cert-*`, `ca-cert-*`, `deployment/*`): <https://docs.cloud.google.com/apigee/docs/api-platform/troubleshoot/playbooks/introduction>, tablas de causas.
