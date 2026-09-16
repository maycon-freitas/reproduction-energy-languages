#!/usr/bin/env bash
# uso: scripts/campanha.sh <nome-da-campanha> [linguagem]
set -uo pipefail

CAMPANHA="${1:?informe o nome da campanha}"
LINGUAGENS=("${2:-C++}" "${2:-Python}")
[ $# -ge 2 ] && LINGUAGENS=("$2")

NTIMES="${NTIMES:-10}"
REST="${REST:-120}"

BENCHMARKS=(binary-trees fannkuch-redux fasta k-nucleotide mandelbrot
            n-body pidigits regex-redux reverse-complement spectral-norm)

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SAIDA="$RAIZ/dados/$CAMPANHA"
mkdir -p "$SAIDA"
LOG="$SAIDA/campanha.log"

registrar() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

registrar "campanha '$CAMPANHA' | linguagens: ${LINGUAGENS[*]} | $NTIMES execucoes | descanso $REST s"
registrar "maquina: $(uname -sr) | $(grep -m1 'model name' /proc/cpuinfo | cut -d: -f2- | sed 's/^ //')"
registrar "medidor: RAPL-powercap | clang: $(clang++-19 --version | head -1) | python: $(python3 --version)"

for lang in "${LINGUAGENS[@]}"; do
  for bench in "${BENCHMARKS[@]}"; do
    dir="$RAIZ/$lang/$bench"
    csv="$SAIDA/$lang.csv"
    marca="$SAIDA/.feito-$lang-$bench"

    if [ -f "$marca" ]; then
      registrar "PULANDO $lang/$bench (ja concluido nesta campanha)"
      continue
    fi
    if [ ! -d "$dir" ]; then
      registrar "AUSENTE $lang/$bench"
      continue
    fi

    registrar "INICIO $lang/$bench"
    ini=$(date +%s)
    if ( cd "$dir" && RAPL_NTIMES="$NTIMES" RAPL_REST_SECONDS="$REST" RAPL_CSV="$csv" \
         make measure >/dev/null 2>>"$LOG" ); then
      touch "$marca"
      registrar "FIM    $lang/$bench em $(( $(date +%s) - ini )) s"
    else
      registrar "ERRO   $lang/$bench (veja o log acima)"
    fi
  done
done

registrar "campanha '$CAMPANHA' encerrada"
registrar "CSVs em $SAIDA"
for f in "$SAIDA"/*.csv; do
  [ -f "$f" ] && registrar "  $(basename "$f"): $(wc -l < "$f") linhas"
done
