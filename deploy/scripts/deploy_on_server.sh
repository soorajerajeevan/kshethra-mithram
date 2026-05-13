#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/kshethra-mithram"
BRANCH="${BRANCH:-main}"
STATE_DIR="${STATE_DIR:-${APP_DIR}/.deploy-state}"
LOCK_FILE="${LOCK_FILE:-${STATE_DIR}/deploy.lock}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:5000}"
HEALTH_RETRIES="${HEALTH_RETRIES:-8}"
HEALTH_SLEEP_SECONDS="${HEALTH_SLEEP_SECONDS:-5}"

fail() {
  echo "ERROR: $*"
  exit 1
}

assert_writable_path() {
  local path="$1"
  local reason="$2"
  [[ -e "${path}" ]] || fail "Missing path: ${path} (${reason})"
  [[ -w "${path}" ]] || fail "Not writable: ${path} (${reason}). Fix ownership: sudo chown -R templedeploy:templedeploy ${APP_DIR}"
}

preflight_git_permissions() {
  [[ -d .git ]] || fail "Not a git repository: ${APP_DIR}"

  # git fetch writes here; fail early with actionable guidance.
  assert_writable_path ".git" "git metadata root"
  assert_writable_path ".git/objects" "git object storage"
  mkdir -p ".git/objects/pack"
  assert_writable_path ".git/objects/pack" "git pack storage"

  [[ -e ".git/index" ]] && assert_writable_path ".git/index" "git index"
  touch ".git/FETCH_HEAD" 2>/dev/null || fail "Cannot write .git/FETCH_HEAD. Fix ownership: sudo chown -R templedeploy:templedeploy ${APP_DIR}"
}

mkdir -p "${STATE_DIR}"
mkdir -p "$(dirname "${LOCK_FILE}")"

exec 9>"${LOCK_FILE}"
if ! flock -n 9; then
  echo "Another deployment is in progress. Exiting."
  exit 0
fi

echo "Starting pull-based deploy for branch=${BRANCH}"

cd "${APP_DIR}"
preflight_git_permissions()

git fetch --prune origin "${BRANCH}"
TARGET_COMMIT="$(git rev-parse "origin/${BRANCH}")"
CURRENT_COMMIT="$(git rev-parse HEAD)"
LAST_SUCCESSFUL_COMMIT="$(cat "${STATE_DIR}/last_successful_commit" 2>/dev/null || true)"

if [[ "${TARGET_COMMIT}" == "${CURRENT_COMMIT}" ]]; then
  echo "No new commit on ${BRANCH}. Nothing to deploy."
  exit 0
fi

echo "Deploying commit ${TARGET_COMMIT} (current ${CURRENT_COMMIT})"
PREVIOUS_COMMIT="${CURRENT_COMMIT}"

rollback() {
  echo "Deployment failed. Rolling back to ${PREVIOUS_COMMIT}"
  git checkout --force "${PREVIOUS_COMMIT}"
  if [[ -f "${STATE_DIR}/last_successful_version" ]]; then
    export BUILD_VERSION
    BUILD_VERSION="$(cat "${STATE_DIR}/last_successful_version")"
  fi
  docker compose build --build-arg BUILD_VERSION="${BUILD_VERSION:-rollback}"
  docker compose up -d --remove-orphans
}

trap rollback ERR

git checkout --force "${TARGET_COMMIT}"
BUILD_VERSION="$(python3 deploy/scripts/compute_version.py --mode deploy --commit-sha "${TARGET_COMMIT}")"
export BUILD_VERSION

docker compose build --build-arg BUILD_VERSION="${BUILD_VERSION}"
docker compose up -d --remove-orphans

healthy=0
for _ in $(seq 1 "${HEALTH_RETRIES}"); do
  if curl -fsS "${HEALTH_URL}" >/dev/null; then
    healthy=1
    break
  fi
  sleep "${HEALTH_SLEEP_SECONDS}"
done

if [[ "${healthy}" -ne 1 ]]; then
  echo "Health check failed for ${HEALTH_URL}"
  exit 1
fi

echo "${TARGET_COMMIT}" > "${STATE_DIR}/last_successful_commit"
echo "${BUILD_VERSION}" > "${STATE_DIR}/last_successful_version"
echo "${LAST_SUCCESSFUL_COMMIT}" > "${STATE_DIR}/previous_successful_commit"

docker image prune -f
echo "Deployment completed: ${BUILD_VERSION}"
