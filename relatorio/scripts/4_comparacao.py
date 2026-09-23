"""Seção 4, comparação entre os estudos: Tabelas 11 a 13 e Figura 5.

Saídas, na ordem em que aparecem no relatório:
    tabela11_razoes_tempo(): Tabela 11, razão Python/C++ de tempo nos seis conjuntos
    tabela12_razoes_energia(): Tabela 12, razão Python/C++ de energia nos seis conjuntos
    figura05_razoes(): Figura 5, razões Python/C++ em quatro conjuntos
    tabela13_razoes_resumo(): Tabela 13, médias geométricas e concordância com a referência

Uso, na raiz do repositório: python3 relatorio/scripts/4_comparacao.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch
from scipy import stats
from comum import (CONJUNTOS, fmt_p, media_geometrica, num, PARES, razoes_comparadas, REFERENCIA,
                   salvar_figura, tabela_razoes, tex)


def tabela11_razoes_tempo():
    """Tabela 11: razão Python/C++ de tempo por benchmark nos seis conjuntos (oito benchmarks comuns)."""
    tabela_razoes("Tempo", "tabela11_razoes_tempo")


def tabela12_razoes_energia():
    """Tabela 12: razão Python/C++ de energia por benchmark nos seis conjuntos (oito benchmarks comuns)."""
    tabela_razoes("Energia", "tabela12_razoes_energia")


def figura05_razoes():
    """Figura 5: razões Python/C++ de tempo e de energia, escala logarítmica, em quatro conjuntos:
    restrito e reprodução de Pereira et al. (2021), reprodução de van Kempen et al. (2024) nas duas
    configurações. Os dois conjuntos restritos de van Kempen ficam nas Tabelas 11 e 12."""
    SERIES = {("Pereira", "restrito"): ("#1f77b4", 0.45), ("Pereira", "reprodução"): ("#1f77b4", 1.0),
              ("van Kempen", "reprodução, padrão"): ("#ff7f0e", 0.45), ("van Kempen", "reprodução, mín. freq."): ("#ff7f0e", 1.0)}
    x = np.arange(len(PARES))
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.2), sharey=True)
    for ax, m in zip(axes, ["Tempo", "Energia"]):
        t = razoes_comparadas(m)
        for i, (serie, (cor, alfa)) in enumerate(SERIES.items()):
            v = t[serie].values
            b = ax.bar(x + (i - 1.5) * 0.2, v, 0.19, color=cor, alpha=alfa)
            ax.bar_label(b, labels=[num(k, ".1f") if k < 10 else num(k, ".0f") for k in v], fontsize=6, padding=2, rotation=90)
        ax.set_yscale("log"); ax.set_ylim(0.3, 3000); ax.axhline(1, color="k", lw=0.8, ls="--")
        ax.set_xticks(x); ax.set_xticklabels(PARES, rotation=30, ha="right")
        ax.set_title(f"Python / C++: {m.lower()}", loc="left"); ax.set_ylabel("razão (escala log)")
    fig.legend([Patch(color=c, alpha=a) for c, a in SERIES.values()], [f"{e}, {c}" for e, c in SERIES],
               loc="upper center", ncol=2, frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.92))
    salvar_figura(fig, "figura05_razoes")


def tabela13_razoes_resumo():
    """Tabela 13: média geométrica das razões Python/C++ em cada conjunto e concordância com a
    referência (reprodução de van Kempen et al. na frequência mínima): Spearman entre as ordens e
    Wilcoxon pareado sobre o logaritmo das razões, com a mediana da razão conjunto/referência.
    Com oito pares, o menor p possível no teste de Wilcoxon é 0,008."""
    comp = {m: razoes_comparadas(m) for m in ["Tempo", "Energia"]}
    linhas = []
    for c in CONJUNTOS:
        linha = {("", "Estudo"): c[0], ("", "Conjunto"): c[1]}
        for m, t in comp.items():
            x, r = t[c], t[REFERENCIA]
            linha[(m, "média geom.")] = media_geometrica(x)
            if c != REFERENCIA:
                linha[(m, "rho")] = stats.spearmanr(x, r)[0]
                linha[(m, "mediana")] = np.median(x / r)
                linha[(m, "p")] = stats.wilcoxon(np.log(x), np.log(r)).pvalue
        linhas.append(linha)
    t = pd.DataFrame(linhas).set_index([("", "Estudo"), ("", "Conjunto")])
    t.index.names = ["Estudo", "Conjunto"]
    t.columns = pd.MultiIndex.from_tuples(t.columns)
    for m in comp:
        t[(m, "p")] = t[(m, "p")].map(fmt_p)
    tex(t, "tabela13_razoes_resumo", float_format="%.2f", na_rep="--", multicolumn_format="c")


if __name__ == "__main__":
    tabela11_razoes_tempo()
    tabela12_razoes_energia()
    figura05_razoes()
    tabela13_razoes_resumo()
