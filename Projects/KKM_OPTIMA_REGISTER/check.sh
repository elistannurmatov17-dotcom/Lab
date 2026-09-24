#!/usr/bin/env bash
set -euo pipefail
python -m compileall -q backend/app
python -m pytest -q tests
bash -n start.sh stop.sh check.sh
python - <<'PY'
import yaml
with open('docker-compose.yml') as f: yaml.safe_load(f)
print('docker-compose.yml: OK')
PY
echo 'Static checks passed.'
