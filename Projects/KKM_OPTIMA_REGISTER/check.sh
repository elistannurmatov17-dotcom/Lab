#!/usr/bin/env bash
set -euo pipefail
python -m compileall -q backend/app
python -m pytest -q tests
bash -n start.sh stop.sh check.sh start-prod.sh backup.sh backup-documents.sh backup-all.sh restore.sh restore-documents.sh
python - <<'PY'
import yaml
for name in ('docker-compose.yml','docker-compose.prod.yml'):
    with open(name) as f:
        yaml.safe_load(f)
    print(name + ': OK')
PY
echo 'Static checks passed.'
