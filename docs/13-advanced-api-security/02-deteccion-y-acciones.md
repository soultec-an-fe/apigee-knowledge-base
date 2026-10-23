---
id: aas-deteccion-y-acciones
titulo: Detección de abuso y security actions
area: seguridad-avanzada
tags: [abuse-detection, detection-rules, incidents, security-actions, allow, deny, flag, anomaly-detection, machine-learning]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://docs.cloud.google.com/apigee/docs/api-security/abuse-detection
revisado: 2026-10-23
---

# Detección de abuso y security actions

> **Fecha de corte: 23 de octubre de 2026.** Requiere el add-on [Advanced API Security](01-vision-general.md).

## Reglas de detección

Un **incidente** es un grupo de eventos de seguridad relacionados entre sí. Lo que dispara un evento son las reglas de detección:

| Regla | Qué detecta |
|---|---|
| **Advanced API Scraper** (Preview, ML) | *Scraping* de APIs: extracción dirigida de información con fines maliciosos |
| **Advanced Anomaly Detection** (Preview, ML) | Cambios bruscos en volumen, errores, latencia, tamaño o geolocalización del tráfico |
| **Brute Guessor** | Proporción alta de respuestas de error (4xx y 5xx) en las últimas 24 h |
| **Flooder** | Proporción alta del tráfico desde una IP en una ventana de 5 minutos |
| **OAuth Abuser** | Muchas sesiones OAuth con pocos *user agents* en las últimas 24 h |
| **Robot Abuser** | Muchos 403 en las últimas 24 h |
| **Static Content Scraper** | Proporción alta del tamaño de respuesta servido a una IP en 5 minutos |
| **TorListRule** | Tráfico procedente de nodos de salida de Tor |

### Advanced Anomaly Detection

- **Nivel de detección:** el **entorno**. No hay detección por proxy individual.
- **Historial necesario:**
  - Empieza a mostrar anomalías **6 horas después del opt-in**, siempre que haya al menos **2 semanas** de historial.
  - Google recomienda **12 semanas** antes de actuar con confianza sobre lo que detecta.
- **Estacionalidad:** reconoce patrones estacionales (como festivos) si el historial los incluye.
- **Datos de entrenamiento:** los modelos se entrenan con metadatos (IP, geografía, algunas cabeceras). Según Google, el modelo no recibe los valores reales de esos metadatos.
- **Funcionamiento interno:** Google no publica cómo decide el modelo, para que no se pueda burlar.

### Ventanas de la UI

- La UI de *Abuse detection* muestra incidentes cuyo último evento ocurrió en los **últimos 14 días**.
- Los datos crudos de cada IP o API key se limitan a una **muestra de 1000 filas**.

### Listas de exclusión

- Sirven para excluir IPs o rangos CIDR de la detección: **hasta 30** por lista.
- El efecto en los incidentes nuevos puede tardar **hasta 3 días**.
- Los informes anteriores conservan ese tráfico, marcado como excluido.

## Security actions

Las *security actions* (**Preview**; en hybrid, desde 1.11) aplican una decisión **antes de que el proxy procese la petición**.

| Acción | Efecto | Precedencia |
|---|---|---|
| **Allow** | Deja pasar peticiones que otra acción Deny bloquearía (por ejemplo, IPs internas de confianza) | **1** (gana) |
| **Deny** | Bloquea y responde con el código que elijas | 2 |
| **Flag** | Deja pasar y añade **hasta 5 cabeceras** definidas por ti, para que el backend decida | 3 |

> [!IMPORTANT]
> - **Las peticiones bloqueadas o marcadas cuentan en tu volumen de llamadas facturable.**
> - Si usas *security actions* y la política [AccessControl](../02-politicas/referencia/access-control.md) para filtrar por IP, **la security action se ejecuta siempre antes**, y después ninguna de las dos influye en la otra.

### Condiciones

| Tipo de condición | Notas |
|---|---|
| Detection rules | Las reglas de la tabla anterior. Máximo 2 condiciones de este tipo. |
| IP addresses / rangos CIDR (IPv4) | Máximo 2 condiciones de este tipo. |
| API keys, API products, access tokens, developers, developer apps | **Requieren** [VerifyAPIKey](../02-politicas/referencia/verify-api-key.md) u [OAuthV2](../02-politicas/referencia/oauthv2.md) en el proxy. En hybrid, desde 1.12. |
| User agents | En hybrid, desde 1.12. |
| HTTP methods | — |
| Region codes (ISO 3166-1 alpha-2) | — |
| ASN (sistemas autónomos) | — |

Del resto de tipos se admite **una condición** de cada uno.

### Límites y latencias

| Aspecto | Valor |
|---|---|
| Ámbito de aplicación | **Entorno**: todos los proxies, o una lista concreta |
| Acciones habilitadas por entorno | **1000** (las caducadas cuentan si siguen habilitadas) |
| Proxies en una acción específica | 100; **no soportado en hybrid** |
| Cabeceras de una acción Flag | 5 |
| Propagación de un cambio | Hasta **10 minutos** |
| Sobrecoste en el tiempo de respuesta | Menos del **2 %** |

- **Estados:** *Enabled*, *Disabled* y *Paused*. Las acciones de **entornos creados antes de abril de 2024 están en pausa por defecto**: hay que reanudarlas.
- **Inmutables:** el nombre y el entorno de una acción no se pueden cambiar.
- **Nombres duplicados:** no se admiten. Si se crean dos acciones con el mismo nombre en rápida sucesión, solo la más reciente es efectiva.
- **Gestión:** desde la UI, con la Security actions API o con Terraform.

### Patrón recomendado

1. Revisa los incidentes en *Abuse detection* y confirma que no son falsos positivos (clientes legítimos, *scrapers* autorizados).
2. Crea primero una acción **Flag** y observa el comportamiento en el backend.
3. Pasa a **Deny** con **caducidad**, para no acumular bloqueos permanentes sin revisar.
4. Mantén una acción **Allow** con las IPs de monitorización y de socios críticos.

Este patrón es de este repositorio, no una recomendación literal de Google.

## Fuentes

Todas consultadas directamente el 2026-10-23:

- Detection rules: <https://docs.cloud.google.com/apigee/docs/api-security/detection-rules>, contenido completo.
- Abuse detection: <https://docs.cloud.google.com/apigee/docs/api-security/abuse-detection>, secciones de incidentes, tráfico detectado y exclusiones.
- Security actions: <https://docs.cloud.google.com/apigee/docs/api-security/security-actions>, contenido completo.
