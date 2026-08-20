---
id: devops-herramientas-cli
titulo: apigeecli y herramientas
area: devops
tags: [apigeecli, gcloud, maven, terraform, cli, automatizacion]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://github.com/apigee/apigeecli
revisado: 2026-08-20
---

# apigeecli y herramientas

## Panorama

| Herramienta | Ámbito | Cuándo |
|---|---|---|
| **apigeecli** | Todos los recursos de Apigee | **Recomendada** para CI/CD y automatización |
| **gcloud apigee** | Subconjunto de operaciones | Cuando ya usas gcloud y basta con lo básico |
| **Plugin de Maven** | Build y deploy de proxies | Proyectos Java con pipeline Maven |
| **Terraform** | Provisión de infraestructura | Crear orgs, entornos, instancias, environment groups |
| **API de gestión** (`apigee.googleapis.com`) | Todo | Integraciones propias y portales |

> [!WARNING]
> ⚠️ **`apigeetool` es de Apigee Edge y no sirve para Apigee X.** Si encuentras documentación o tutoriales que lo usan, son de la plataforma legacy.

---

## apigeecli

Herramienta oficial de Apigee para interactuar con las APIs de la plataforma. Gestiona entornos, proxies, productos, developers, apps, KVMs, keystores, target servers y más.

### Instalación

```bash
curl -L https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | sh -
export PATH="$PATH:$HOME/.apigeecli/bin"
apigeecli -v
```

### Autenticación

La autenticación contra las APIs de gestión de Apigee X e hybrid se hace con una **service account de Google Cloud**.

```bash
# Opción A: token efímero del usuario/SA activo
export TOKEN="$(gcloud auth print-access-token)"
apigeecli apis list --org "$ORG" --token "$TOKEN"

# Opción B: archivo de service account
apigeecli token cache --account ./sa-apigee.json
```

> [!NOTE]
> `apigeecli` **cachea el access token OAuth** para llamadas sucesivas, en `$HOME/.apigeecli`.

### Comandos por recurso

**Proxies:**

```bash
# Empaquetar y subir desde una carpeta apiproxy/
apigeecli apis create bundle --name pedidos-v1 --proxy-folder ./apiproxy \
  --org "$ORG" --token "$TOKEN"

# Desplegar una revisión
apigeecli apis deploy --name pedidos-v1 --rev 12 \
  --org "$ORG" --env prod --ovr --wait --token "$TOKEN"

# Listar, exportar, despublicar, borrar
apigeecli apis list        --org "$ORG" --token "$TOKEN"
apigeecli apis export      --org "$ORG" --token "$TOKEN"
apigeecli apis undeploy    --name pedidos-v1 --rev 12 --org "$ORG" --env prod --token "$TOKEN"
apigeecli apis delete      --name pedidos-v1 --org "$ORG" --token "$TOKEN"

# Sesión de depuración
apigeecli apis debug --name pedidos-v1 --rev 12 \
  --filter 'request.header.x-debug == "si"' \
  --org "$ORG" --env prod --token "$TOKEN"
```

**Shared flows:**

```bash
apigeecli sharedflows create bundle --name sf-seguridad --sf-folder ./sharedflowbundle \
  --org "$ORG" --token "$TOKEN"
apigeecli sharedflows deploy --name sf-seguridad --rev 1 \
  --org "$ORG" --env prod --ovr --wait --token "$TOKEN"
```

**Flow hooks:**

```bash
apigeecli flowhooks attach --name PreProxy --sharedflow sf-seguridad \
  --org "$ORG" --env prod --token "$TOKEN"
apigeecli flowhooks list --org "$ORG" --env prod --token "$TOKEN"
```

**Target servers:**

```bash
apigeecli targetservers create --name pedidos-svc \
  --host pedidos.interno.example.com --port 443 --enable \
  --org "$ORG" --env prod --token "$TOKEN"
apigeecli targetservers export --org "$ORG" --env prod --token "$TOKEN"
```

**KVMs:**

```bash
apigeecli kvms create --name config-backends --org "$ORG" --env prod --token "$TOKEN"
apigeecli kvms entries create --map config-backends \
  --key backend_api_key --value "$SECRETO" \
  --org "$ORG" --env prod --token "$TOKEN"
```

**API products, developers y apps:**

```bash
apigeecli products create -f ./producto-basico.json --org "$ORG" --token "$TOKEN"
apigeecli products export --org "$ORG" --token "$TOKEN"

apigeecli developers create --email dev@cliente.com --first Ana --last García \
  --user anagarcia --org "$ORG" --token "$TOKEN"

apigeecli apps create --name mi-app --email dev@cliente.com --prods producto-basico \
  --org "$ORG" --token "$TOKEN"
apigeecli apps keys create --name mi-app --dev dev@cliente.com --prods producto-basico \
  --org "$ORG" --token "$TOKEN"
```

**Keystores:**

```bash
apigeecli keystores create --name keystore-cliente --org "$ORG" --env prod --token "$TOKEN"
apigeecli keyaliases create --keystore keystore-cliente --name cert-2026 \
  --format keycertfile --cert-file ./c.crt --key-file ./c.key \
  --org "$ORG" --env prod --token "$TOKEN"
```

### Backup y restauración completos

```bash
# Exportar toda la configuración de la organización
apigeecli organizations export --org "$ORG" --token "$TOKEN"

# Importar en otra organización
apigeecli organizations import -f ./export --org "$ORG_DESTINO" --token "$TOKEN"
```

> [!TIP]
> Ejecuta `organizations export` periódicamente y guarda el resultado en Git o Cloud Storage. Es el backup más completo y sencillo de la configuración de Apigee.

### Como contenedor

Para pipelines sin instalación:

```bash
docker run --rm ghcr.io/apigee/apigeecli:latest apis list --org "$ORG" --token "$TOKEN"
```

---

## gcloud apigee

Subconjunto de operaciones integrado en el SDK de Google Cloud.

```bash
gcloud apigee organizations list
gcloud apigee environments list --organization="$ORG"
gcloud apigee apis list --organization="$ORG"
gcloud apigee apis deploy 12 --api=pedidos-v1 --environment=prod --organization="$ORG"
gcloud apigee archives deploy --environment=prod --organization="$ORG"
```

Más limitado que `apigeecli`, pero cómodo si ya tienes `gcloud` autenticado y solo necesitas operaciones básicas.

---

## Plugin de Maven

Para proyectos Java donde el proxy convive con `JavaCallout`.

```xml
<plugin>
    <groupId>com.google.cloud.apigee</groupId>
    <artifactId>apigee-edge-maven-plugin</artifactId>
    <version>VERSION</version>
    <executions>
        <execution>
            <id>configure-bundle</id>
            <phase>package</phase>
            <goals><goal>configure</goal></goals>
        </execution>
        <execution>
            <id>deploy-bundle</id>
            <phase>install</phase>
            <goals><goal>deploy</goal></goals>
        </execution>
    </executions>
</plugin>
```

```bash
mvn install -Papigee -Dapigee.profile=prod -Dapigee.config.options=update
```

Ventaja real: el plugin soporta **sustitución de configuración por perfil**, lo que permite gestionar target servers y KVMs por entorno desde el mismo build.

---

## Terraform

Para **provisionar la infraestructura**: organizaciones, entornos, environment groups, instancias, PSC.

```hcl
resource "google_apigee_organization" "org" {
  analytics_region   = "europe-west1"
  project_id         = var.project_id
  authorized_network = google_compute_network.apigee.id
  billing_type       = "PAYG"
}

resource "google_apigee_environment" "prod" {
  org_id    = google_apigee_organization.org.id
  name      = "prod"
  type      = "COMPREHENSIVE"
  api_proxy_type = "PROGRAMMABLE"
}

resource "google_apigee_envgroup" "externo" {
  org_id   = google_apigee_organization.org.id
  name     = "externo"
  hostnames = ["api.empresa.com"]
}

resource "google_apigee_envgroup_attachment" "prod_externo" {
  envgroup_id = google_apigee_envgroup.externo.id
  environment = google_apigee_environment.prod.name
}
```

> [!IMPORTANT]
> **Separa infraestructura de artefactos.** Terraform provisiona orgs, entornos y grupos (cambian raramente). `apigeecli` despliega proxies y productos (cambian a diario). Meter proxies en Terraform hace que cada despliegue de API sea un `terraform apply`, lo cual es lento y frágil.

---

## API de gestión directa

Para integraciones propias, portales personalizados y onboarding automatizado:

```bash
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  "https://apigee.googleapis.com/v1/organizations/$ORG/apis"

curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json" \
  -d '{"email":"dev@cliente.com","firstName":"Ana","lastName":"García","userName":"anagarcia"}' \
  "https://apigee.googleapis.com/v1/organizations/$ORG/developers"
```

> [!CAUTION]
> **Antipatrón documentado: invocar la API de gestión desde un API proxy.**
> Nunca llames a `apigee.googleapis.com` desde un `ServiceCallout` en el camino del tráfico. Es lenta, tiene cuotas propias y acopla el plano de datos al plano de control. Si un proxy necesita datos de configuración, cárgalos en un KVM o PropertySet.

## Fuentes

- <https://github.com/apigee/apigeecli>
- <https://cloud.google.com/sdk/gcloud/reference/apigee>
- <https://cloud.google.com/apigee/docs/api-platform/local-development/overview>
- <https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/apigee_organization>
