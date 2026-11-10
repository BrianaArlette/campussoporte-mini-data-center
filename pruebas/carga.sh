#!/usr/bin/env bash
set -euo pipefail
N=${1:-30}
if ! [[ "$N" =~ ^[0-9]+$ ]] || (( N < 1 || N > 200 )); then echo 'Uso: bash pruebas/carga.sh 30'; exit 2; fi
for ((i=1;i<=N;i++)); do curl -fsS "http://localhost:8080/whoami?prueba=$i"; echo; done
# Para guardar el agregado en MariaDB, usa el botón de prueba del portal o carga.ps1.
