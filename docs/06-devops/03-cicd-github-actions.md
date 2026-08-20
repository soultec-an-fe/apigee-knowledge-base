---
id: devops-cicd
titulo: CI/CD con GitHub Actions
area: devops
tags: [cicd, github-actions, workload-identity, pipeline, despliegue]
aplica_a: [apigee-x, apigee-hybrid]
fuente: https://github.com/apigee/apigeecli
revisado: 2026-08-20
---

# CI/CD con GitHub Actions

## Principios

1. **Un artefacto, varios entornos.** Empaqueta el bundle una vez y promociona **esa misma revisión**.
2. **Sin claves de service account en el repositorio.** Usa Workload Identity Federation.
3. **La configuración por entorno vive fuera del bundle** (TargetServers, KVMs).
4. **Producción requiere aprobación manual.**
5. **Rollback en un comando**: volver a desplegar la revisión anterior.

## Autenticación: Workload Identity Federation

> [!WARNING]
> **No guardes archivos JSON de service account como secretos de GitHub.** Son credenciales de larga duración que, si se filtran, dan acceso permanente. Workload Identity Federation emite tokens efímeros sin claves persistentes.

Configuración en Google Cloud (una sola vez):

```bash
PROJECT_ID="mi-proyecto"
POOL="github-pool"
PROVIDER="github-provider"
REPO="festem200/mi-plataforma-apis"
SA="apigee-deployer@${PROJECT_ID}.iam.gserviceaccount.com"

# 1. Pool de identidades
gcloud iam workload-identity-pools create "$POOL" \
  --project="$PROJECT_ID" --location=global \
  --display-name="GitHub Actions"

# 2. Proveedor OIDC de GitHub
gcloud iam workload-identity-pools providers create-oidc "$PROVIDER" \
  --project="$PROJECT_ID" --location=global \
  --workload-identity-pool="$POOL" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --attribute-condition="assertion.repository == '${REPO}'"

# 3. Permitir que el repo suplante a la service account
POOL_ID=$(gcloud iam workload-identity-pools describe "$POOL" \
  --project="$PROJECT_ID" --location=global --format='value(name)')

gcloud iam service-accounts add-iam-policy-binding "$SA" \
  --project="$PROJECT_ID" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/${POOL_ID}/attribute.repository/${REPO}"
```

> [!IMPORTANT]
> El `--attribute-condition` es obligatorio en la práctica. Sin él, **cualquier repositorio de GitHub** podría obtener tokens para tu service account.

Roles IAM mínimos para la service account de despliegue:

| Rol | Para qué |
|---|---|
| `roles/apigee.apiAdmin` | Crear y desplegar proxies y shared flows |
| `roles/apigee.environmentAdmin` | Gestionar target servers, KVMs, keystores |
| `roles/apigee.developerAdmin` | Gestionar developers, apps y productos |

## Workflow completo

`.github/workflows/deploy.yml`:

```yaml
name: Desplegar API

on:
  push:
    branches: [main]
    paths: ['apis/**', 'sharedflows/**']
  pull_request:
    paths: ['apis/**', 'sharedflows/**']
  workflow_dispatch:
    inputs:
      proxy:
        description: 'Nombre del proxy'
        required: true

permissions:
  contents: read
  id-token: write        # necesario para Workload Identity Federation

env:
  APIGEE_ORG: mi-proyecto
  PROXY: pedidos-v1

jobs:
  # ---------------------------------------------------------------
  validar:
    name: Validar bundle
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Validar XML de políticas
        run: |
          set -euo pipefail
          fallos=0
          for f in $(find apis -name '*.xml'); do
            if ! xmllint --noout "$f" 2>/dev/null; then
              echo "::error file=$f::XML inválido"
              fallos=1
            fi
          done
          exit $fallos

      - name: Comprobar que name coincide con el nombre de archivo
        run: |
          set -euo pipefail
          fallos=0
          for f in $(find apis -path '*/policies/*.xml'); do
            esperado=$(basename "$f" .xml)
            real=$(xmllint --xpath 'string(/*/@name)' "$f" 2>/dev/null || echo '')
            if [[ "$esperado" != "$real" ]]; then
              echo "::error file=$f::atributo name='$real' no coincide con el archivo '$esperado'"
              fallos=1
            fi
          done
          exit $fallos

      - name: Validar spec OpenAPI
        run: |
          npx --yes @redocly/cli lint apis/${PROXY}/openapi.yaml

  # ---------------------------------------------------------------
  empaquetar:
    name: Empaquetar y subir
    needs: validar
    if: github.event_name != 'pull_request'
    runs-on: ubuntu-latest
    outputs:
      revision: ${{ steps.subir.outputs.revision }}
    steps:
      - uses: actions/checkout@v4

      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}

      - uses: google-github-actions/setup-gcloud@v2

      - name: Instalar apigeecli
        run: |
          curl -L https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | sh -
          echo "$HOME/.apigeecli/bin" >> "$GITHUB_PATH"

      - name: Subir bundle
        id: subir
        run: |
          set -euo pipefail
          TOKEN="$(gcloud auth print-access-token)"
          REV=$(apigeecli apis create bundle \
                  --name "$PROXY" \
                  --proxy-folder "apis/${PROXY}/apiproxy" \
                  --org "$APIGEE_ORG" --token "$TOKEN" \
                | jq -r '.revision')
          echo "Revisión creada: $REV"
          echo "revision=$REV" >> "$GITHUB_OUTPUT"

  # ---------------------------------------------------------------
  desplegar-dev:
    name: Desplegar en dev
    needs: empaquetar
    runs-on: ubuntu-latest
    environment: dev
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - uses: google-github-actions/setup-gcloud@v2
      - name: Instalar apigeecli
        run: |
          curl -L https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | sh -
          echo "$HOME/.apigeecli/bin" >> "$GITHUB_PATH"

      - name: Sincronizar target servers de dev
        run: |
          TOKEN="$(gcloud auth print-access-token)"
          apigeecli targetservers import -f config/dev/targetservers.json \
            --org "$APIGEE_ORG" --env dev --token "$TOKEN"

      - name: Desplegar
        run: |
          TOKEN="$(gcloud auth print-access-token)"
          apigeecli apis deploy --name "$PROXY" \
            --rev "${{ needs.empaquetar.outputs.revision }}" \
            --org "$APIGEE_ORG" --env dev --ovr --wait --token "$TOKEN"

      - name: Tests de integración
        env:
          HOST: ${{ vars.HOST_DEV }}
          API_KEY: ${{ secrets.API_KEY_DEV }}
        run: ./apis/${{ env.PROXY }}/test/integracion.sh

  # ---------------------------------------------------------------
  desplegar-prod:
    name: Desplegar en producción
    needs: [empaquetar, desplegar-dev]
    runs-on: ubuntu-latest
    environment: produccion        # requiere aprobación manual en GitHub
    steps:
      - uses: actions/checkout@v4
      - uses: google-github-actions/auth@v2
        with:
          workload_identity_provider: ${{ secrets.WIF_PROVIDER }}
          service_account: ${{ secrets.WIF_SERVICE_ACCOUNT }}
      - uses: google-github-actions/setup-gcloud@v2
      - name: Instalar apigeecli
        run: |
          curl -L https://raw.githubusercontent.com/apigee/apigeecli/main/downloadLatest.sh | sh -
          echo "$HOME/.apigeecli/bin" >> "$GITHUB_PATH"

      - name: Guardar la revisión actual (para rollback)
        id: anterior
        run: |
          TOKEN="$(gcloud auth print-access-token)"
          REV_ACTUAL=$(apigeecli apis listdeploy --name "$PROXY" \
                        --org "$APIGEE_ORG" --env prod --token "$TOKEN" \
                      | jq -r '.deployments[0].revision // "ninguna"')
          echo "Revisión actual en prod: $REV_ACTUAL"
          echo "revision=$REV_ACTUAL" >> "$GITHUB_OUTPUT"

      - name: Desplegar
        run: |
          TOKEN="$(gcloud auth print-access-token)"
          apigeecli apis deploy --name "$PROXY" \
            --rev "${{ needs.empaquetar.outputs.revision }}" \
            --org "$APIGEE_ORG" --env prod --ovr --wait --token "$TOKEN"

      - name: Smoke test
        env:
          HOST: ${{ vars.HOST_PROD }}
        run: |
          set -euo pipefail
          codigo=$(curl -s -o /dev/null -w '%{http_code}' "https://${HOST}/pedidos/v1/health")
          [[ "$codigo" == "200" ]] || { echo "Health devolvió $codigo"; exit 1; }

      - name: Rollback si el smoke test falla
        if: failure() && steps.anterior.outputs.revision != 'ninguna'
        run: |
          TOKEN="$(gcloud auth print-access-token)"
          echo "::warning::Revirtiendo a la revisión ${{ steps.anterior.outputs.revision }}"
          apigeecli apis deploy --name "$PROXY" \
            --rev "${{ steps.anterior.outputs.revision }}" \
            --org "$APIGEE_ORG" --env prod --ovr --wait --token "$TOKEN"
```

## Selección de entorno por rama

Patrón habitual cuando no se quiere aprobación manual:

```yaml
- name: Determinar entorno
  id: entorno
  run: |
    case "${GITHUB_REF#refs/heads/}" in
      main)     echo "env=prod" >> "$GITHUB_OUTPUT" ;;
      develop)  echo "env=test" >> "$GITHUB_OUTPUT" ;;
      *)        echo "env=dev"  >> "$GITHUB_OUTPUT" ;;
    esac
```

## Validaciones recomendadas en el pipeline

| Validación | Cómo | Detecta |
|---|---|---|
| XML bien formado | `xmllint --noout` | Errores de sintaxis antes del deploy |
| `name` == nombre de archivo | `xmllint --xpath` | Fallo de despliegue garantizado |
| Políticas no referenciadas | Grep de `<Name>` en flujos | Bundle inflado, deploy lento |
| Spec OpenAPI válida | `@redocly/cli lint` | Documentación rota |
| Sin `IgnoreValidationErrors=true` | `grep -r` | Vulnerabilidad TLS |
| Sin secretos en el bundle | `gitleaks` / `trufflehog` | Credenciales filtradas |
| Tamaño del bundle < 15 MB | `du -sh` | Rechazo del despliegue |

Ejemplo de guardia de seguridad:

```yaml
- name: Prohibir IgnoreValidationErrors en producción
  run: |
    if grep -rn 'IgnoreValidationErrors>true' apis/; then
      echo "::error::IgnoreValidationErrors=true desactiva la validación TLS del backend"
      exit 1
    fi
```

## Rollback manual

```bash
# Ver qué revisión está desplegada
apigeecli apis listdeploy --name pedidos-v1 --org "$ORG" --env prod --token "$TOKEN"

# Volver a la anterior
apigeecli apis deploy --name pedidos-v1 --rev 11 \
  --org "$ORG" --env prod --ovr --wait --token "$TOKEN"
```

Como las revisiones son inmutables y se retienen **250**, el rollback es siempre volver a desplegar un número. No requiere reconstruir nada.

## Otros CI

El mismo patrón es directo en cualquier CI:

| CI | Autenticación |
|---|---|
| **GitLab CI** | Workload Identity Federation vía OIDC |
| **Azure Pipelines** | Workload Identity Federation vía OIDC |
| **Cloud Build** | Service account nativa, sin federación |
| **Jenkins** | Service account con clave rotada, o plugin de OIDC |

`apigeecli` también está disponible como contenedor, útil en runners sin instalación:

```yaml
- run: |
    docker run --rm ghcr.io/apigee/apigeecli:latest \
      apis list --org "$APIGEE_ORG" --token "$TOKEN"
```

## Fuentes

- <https://github.com/apigee/apigeecli>
- <https://cloud.google.com/iam/docs/workload-identity-federation>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/api-development-lifecycle>
