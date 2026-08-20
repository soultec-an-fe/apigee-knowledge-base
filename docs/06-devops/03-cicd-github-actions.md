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

## Respaldo de KVMs y recursos con scope de entorno

> [!IMPORTANT]
> El **bundle del proxy** (políticas, recursos empaquetados en `apiproxy/resources/`) ya está versionado si sigues el flujo de este documento: vive en Git y cada despliegue es una revisión inmutable con 250 histórico. **Lo que NO está versionado por defecto** es todo lo que vive únicamente en el runtime de Apigee y se edita fuera del bundle: **entradas de KVM, TargetServers, keystores/truststores y recursos con scope de entorno u organización**. Si alguien borra una entrada de KVM o un TargetServer desde la consola, no hay "deshacer": se ha ido, salvo que tengas tu propio respaldo.

### El punto de partida: los KVM sí se pueden leer de vuelta

Por defecto, `apigeecli kvms entries export` **devuelve los valores en texto plano** — el cifrado de un KVM protege los datos en reposo (Cloud KMS, AES256), no oculta el valor a quien tiene permiso de lectura. Solo se oculta si activas explícitamente el **enmascarado** (`maskedValues`) en ese KVM concreto, y entonces ni siquiera tú puedes recuperar el valor por la API. Ver el detalle en [caching y persistencia](../05-operacion/04-caching-y-persistencia.md).

Esto significa que **sí puedes hacer un respaldo automatizado de tus KVMs**, con dos condiciones:

1. **No actives el enmascarado** en los KVMs que quieras poder respaldar y restaurar tú mismo.
2. **No commitees el respaldo en texto plano a un repo compartido** si contiene secretos reales — cífralo primero (ver más abajo).

### Comandos verificados de `apigeecli` (contra el código fuente)

> [!NOTE]
> Los nombres de archivo de salida de `kvms export` y `targetservers export` están verificados directamente contra el **código fuente** de `apigeecli` (paquetes `internal/cmd/kvm` y `internal/cmd/targetservers`), no solo contra su documentación de flags, porque es exactamente el dato que rompe un script si se asume mal.

```bash
# Exportar TODAS las entradas de TODOS los KVMs de un entorno, de una vez.
# Escribe un archivo por KVM en el directorio ACTUAL, con el patrón:
#   env__<ENTORNO>__<NOMBRE_KVM>__kvmfile__0.json
apigeecli kvms export -o "$ORG" -e prod -t "$(gcloud auth print-access-token)"
# Omitir -e exporta los KVMs con scope de organización (patrón org__<KVM>__kvmfile__0.json)

# Restaurar TODOS los KVMs desde una carpeta con ese patrón de archivos
# (recorre la carpeta de forma recursiva, recrea cada KVM y sus entradas)
apigeecli kvms import -o "$ORG" -f respaldo/prod/kvms -t "$(gcloud auth print-access-token)"

# Exportar/restaurar solo UN KVM concreto
apigeecli kvms entries export -o "$ORG" -e prod -m config-backends \
  -t "$(gcloud auth print-access-token)" > respaldo/kvm-config-backends.json
apigeecli kvms entries import -o "$ORG" -e prod -m config-backends \
  -f respaldo/kvm-config-backends.json -t "$(gcloud auth print-access-token)"

# Exportar todos los TargetServers de un entorno.
# Escribe UN ÚNICO archivo "targetservers.json" en el directorio actual (no una carpeta)
apigeecli targetservers export -o "$ORG" -e prod -t "$(gcloud auth print-access-token)"

# Exportar keystores y key aliases (certificados, sin la clave privada) a una carpeta
apigeecli keystores export -o "$ORG" -e prod -f respaldo/keystores \
  -t "$(gcloud auth print-access-token)"

# Recursos con scope de entorno (properties, jsc, oas, ...): sin export masivo,
# hay que listar y pedir cada archivo. Ajusta el filtro jq a la forma real de tu salida.
apigeecli resources list -o "$ORG" -e prod -t "$(gcloud auth print-access-token)"
apigeecli resources get -o "$ORG" -e prod -n config.properties -p properties \
  -t "$(gcloud auth print-access-token)" > respaldo/recursos/config.properties
```

### Script de respaldo completo, programado

```bash
#!/usr/bin/env bash
# respaldar-entorno.sh — vuelca KVMs, TargetServers y keystores a un directorio versionado en Git
set -euo pipefail

ORG="${ORG:?falta ORG}"
ENV="${ENV:?falta ENV}"
TOKEN="$(gcloud auth print-access-token)"
DEST="respaldo/${ENV}"

mkdir -p "$DEST/kvms"

echo "→ TargetServers (un único targetservers.json)"
( cd "$DEST" && apigeecli targetservers export -o "$ORG" -e "$ENV" -t "$TOKEN" )

echo "→ Keystores"
apigeecli keystores export -o "$ORG" -e "$ENV" -f "$DEST/keystores" -t "$TOKEN"

echo "→ KVMs de entorno (los que NO tienen enmascarado activo)"
( cd "$DEST/kvms" && apigeecli kvms export -o "$ORG" -e "$ENV" -t "$TOKEN" )

echo "Respaldo de $ENV completo en $DEST"
```

> [!TIP]
> Ejecutar `apigeecli kvms export` con el directorio de trabajo (`cd`) ya puesto en la carpeta destino evita tener que mover archivos después — el propio comando escribe ahí. Para restaurar: `apigeecli kvms import -o "$ORG" -f "$DEST/kvms" -t "$TOKEN"`, que reconstruye cada KVM y sus entradas a partir del nombre de archivo.

### GitHub Actions: snapshot nocturno con historial completo en Git

La clave para "si alguien borra algo, recuperarlo" no es solo tener un respaldo: es tener **historial versionado**, para poder volver a cualquier punto anterior, no solo al último snapshot.

```yaml
name: Respaldo nocturno de configuración de Apigee

on:
  schedule:
    - cron: '0 3 * * *'   # cada noche a las 03:00 UTC
  workflow_dispatch:

permissions:
  contents: write
  id-token: write

env:
  APIGEE_ORG: mi-proyecto

jobs:
  respaldar:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        entorno: [dev, test, prod]
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

      - name: Respaldar
        env:
          ORG: ${{ env.APIGEE_ORG }}
          ENV: ${{ matrix.entorno }}
        run: ./scripts/respaldar-entorno.sh

      - name: Commitear solo si hay cambios
        run: |
          git config user.name "apigee-backup-bot"
          git config user.email "actions@github.com"
          git add "respaldo/${{ matrix.entorno }}"
          if ! git diff --cached --quiet; then
            git commit -m "chore: snapshot de ${{ matrix.entorno }} $(date -u +%Y-%m-%dT%H:%M:%SZ)"
            git push
          else
            echo "Sin cambios, nada que commitear"
          fi
```

Con esto, cada noche se crea un commit **solo si algo cambió**. Si alguien borra una entrada de KVM el martes, el commit del lunes por la noche la conserva intacta: `git log -- respaldo/prod/kvms/config-backends.json` te da el historial completo, y `git show <commit>:respaldo/prod/kvms/config-backends.json` recupera cualquier versión pasada sin tocar el entorno real hasta que decidas restaurarla con `kvms entries import`.

### Secretos: no lo comitees en texto plano sin cifrar

> [!CAUTION]
> El script de arriba vuelca los valores de KVM **en texto plano** al repositorio, porque por defecto Apigee los devuelve así. Si algún KVM contiene credenciales reales, **no lo subas así a un repositorio compartido**, aunque sea privado. Tres opciones, de más a menos recomendada:
>
> 1. **Fuente de verdad fuera de Apigee.** Guarda el secreto real en Secret Manager (o el gestor que uses) y trata el KVM como un espejo de solo escritura: un job de CI lo sincroniza *hacia* Apigee, pero el repositorio nunca contiene el valor — solo el nombre de la clave. El respaldo de ese KVM entonces solo registra qué claves existen, no sus valores.
> 2. **Cifra el respaldo antes de commitear.** Usa [`git-crypt`](https://github.com/AGWA/git-crypt) o [`SOPS`](https://github.com/getsops/sops) para que los archivos de `respaldo/*/kvms/*.json` se guarden cifrados en el historial de Git y solo se descifren en checkout local para quien tenga la clave.
> 3. **Excluye del respaldo automatizado los KVMs con secretos**, y respáldalos aparte manualmente en un gestor de secretos con su propio control de versiones. Reserva el script de arriba para KVMs de **configuración no sensible** (URLs de backend, feature flags, mapeos), donde el texto plano en Git no es un riesgo.

Para configuración **no sensible**, el patrón de arriba —snapshot nocturno versionado en Git— es exactamente lo que buscas: da recuperación ante borrado accidental, historial completo de quién cambió qué y cuándo (vía `git blame`), y una fuente auditable independiente de la consola de Apigee.

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
- <https://github.com/apigee/apigeecli/blob/main/internal/cmd/kvm/expkvm.go> (código fuente verificado: patrón de nombre de archivo de `kvms export`)
- <https://github.com/apigee/apigeecli/blob/main/internal/cmd/kvm/impkvms.go> (código fuente verificado: `kvms import` masivo)
- <https://github.com/apigee/apigeecli/blob/main/internal/cmd/targetservers/expts.go> (código fuente verificado: `targetservers export` escribe un único archivo)
- <https://github.com/apigee/apigeecli/blob/main/internal/cmd/utils/utils.go> (constante `DefaultFileSplitter = "__"`)
- <https://cloud.google.com/apigee/docs/api-platform/cache/key-value-maps> (consultada directamente: enmascarado de KVM es opt-in, no por defecto)
- <https://cloud.google.com/iam/docs/workload-identity-federation>
- <https://cloud.google.com/apigee/docs/api-platform/fundamentals/api-development-lifecycle>
