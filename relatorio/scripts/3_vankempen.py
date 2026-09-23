"""Seção 3, reprodução de van Kempen et al. (2024): Tabelas 8 a 10, Figuras 3 e 4 e as estatísticas citadas na Seção 3.1.

Saídas, na ordem em que aparecem no relatório:
    estatisticas_validacao_vankempen(): estatísticas da Seção 3.1 (potência PKG e PKG + DRAM, fração PP0/PKG, pidigits)
    tabela08_vankempen_potencia_fixa(): Tabela 8, potência na frequência mínima em um núcleo
    figura03_vankempen_nucleos(): Figura 3, potência PKG contra núcleos ativos
    tabela09_vankempen_ajuste_nucleos(): Tabela 9, ajuste logarítmico da potência aos núcleos
    figura04_vankempen_dram(): Figura 4, potência de DRAM contra faltas de LLC
    tabela10_vankempen_dram(): Tabela 10, ajuste linear da DRAM e fração DRAM/PKG

Uso, na raiz do repositório: python3 relatorio/scripts/3_vankempen.py
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from comum import (ajustes_dram, ajustes_nucleos, ARTIGO_VK, CONFIGS, COR_LANG, cv,
                   execucoes_vankempen, LANGS, legenda_ajuste, ler_vankempen, log_fit, num,
                   ORIGENS, salvar_estatisticas, salvar_figura, tex, VIRGULA)


def estatisticas_validacao_vankempen():
    """Estatísticas da Seção 3.1: composição da potência, fração PP0/PKG e o defeito de pidigits."""
    todos = execucoes_vankempen()
    L = ["Validação do método de van Kempen et al. (2024) com os dados restritos", ""]
    mf = todos.query("origem == 'restrito' and config == 'mín. freq.'")
    L.append("Potência na frequência mínima, dados restritos (média ± desvio sobre as execuções)")
    L.append(f"  PKG + DRAM: {num(mf['W'].mean(), '.2f')} ± {num(mf['W'].std(ddof=1), '.2f')} W ({len(mf)} execuções)")
    L.append(f"  só PKG:     {num(mf['W_pkg'].mean(), '.2f')} W")
    L += ["", "PP0 como fração de PKG, reprodução (o Xeon dos autores não expõe PP0)"]
    rep = todos.query("origem == 'reprodução'")
    for cfg in CONFIGS:
        g = rep[rep["config"] == cfg]
        f = 100 * g["PP0"] / g["PKG"]
        L.append(f"  {cfg:10s} {num(f.min(), '.0f')}% a {num(f.max(), '.0f')}% (entre execuções)")
    L += ["", "pidigits, configuração padrão: mediana do tempo (s) e razão Python/C++"]
    for org in ORIGENS:
        d = ler_vankempen(org, "padrão", benchmarks=("pidigits",))
        t = d.groupby("lang")["tempo"].median()
        if set(LANGS) <= set(t.index):
            L.append(f"  {org:10s} C++ {num(t['C++'], '.2f')} s, Python {num(t['Python'], '.0f')} s, razão {num(t['Python'] / t['C++'], '.0f')}")
    salvar_estatisticas("validacao_vankempen", L)


def tabela08_vankempen_potencia_fixa():
    """Tabela 8: potência (PKG + DRAM) na frequência mínima em um núcleo, sobre todas as execuções:
    valor do artigo, dados restritos a C++ e Python, e reprodução."""
    mf = execucoes_vankempen().query("config == 'mín. freq.'")
    m, s = ARTIGO_VK["potencia"]
    linhas = [{"Origem": "artigo", "Média (W)": m, "Desvio (W)": s, "CV (%)": 100 * s / m,
               "Mínimo (W)": np.nan, "Máximo (W)": np.nan, "Execuções": np.nan}]
    for org, g in mf.groupby("origem"):
        linhas.append({"Origem": org, "Média (W)": g["W"].mean(), "Desvio (W)": g["W"].std(ddof=1), "CV (%)": cv(g["W"]),
                       "Mínimo (W)": g["W"].min(), "Máximo (W)": g["W"].max(), "Execuções": len(g)})
    t = pd.DataFrame(linhas).set_index("Origem").loc[["artigo", "restrito", "reprodução"]]
    tex(t, "tabela08_vankempen_potencia_fixa", na_rep="--",
        float_format=lambda v: f"{v:.0f}" if v >= 10 and float(v).is_integer() else f"{v:.2f}")


def figura03_vankempen_nucleos():
    """Figura 3: potência PKG de cada execução contra o número médio de núcleos ativos, configuração
    padrão, no formato da Figura 8a do artigo. Painel superior: dados restritos com o ajuste a esses
    pontos e a curva do artigo (tracejada); painel inferior: reprodução com o ajuste próprio."""
    pad = execucoes_vankempen().query("config == 'padrão'")
    aj = ajustes_nucleos()
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.2))
    for ax, org in zip(axes, ORIGENS):
        g = pad[pad["origem"] == org]
        for lang in LANGS:
            gl = g[g["lang"] == lang]
            ax.scatter(gl["nucleos"], gl["W_pkg"], color=COR_LANG[lang], s=8, alpha=0.7)
        xs = np.linspace(g["nucleos"].min(), g["nucleos"].max(), 200)
        a, b, r2 = aj[org]
        ax.plot(xs, log_fit(xs, a, b), color="red", lw=1)
        titulo = f"{org}: {num(a, '.4g')}·log₂(x) + {num(b, '.4g')}, R² = {num(r2, '.2f')}"
        if org == "restrito":
            a2, b2, r22 = aj["artigo"]
            ax.plot(xs, log_fit(xs, a2, b2), color="red", lw=1, ls="--")
            titulo += f"; artigo: {num(a2, '.4g')}·log₂(x) + {num(b2, '.4g')}, R² = {num(r22, '.2f')}"
        ax.set_ylim(0, g["W_pkg"].max() * 1.15)
        ax.set_ylabel("potência PKG (W)"); ax.set_xlabel("número médio de núcleos ativos")
        ax.yaxis.set_major_formatter(VIRGULA); ax.xaxis.set_major_formatter(VIRGULA)
        ax.set_title(titulo, loc="left", fontsize=8.5)
    legenda_ajuste(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    salvar_figura(fig, "figura03_vankempen_nucleos")


def tabela09_vankempen_ajuste_nucleos():
    """Tabela 9: coeficientes do ajuste a*log2(x) + b da potência PKG aos núcleos ativos, com a razão
    entre a potência a dois núcleos e a um núcleo, (a + b)/b, que é o ganho mínimo de vazão para que
    paralelizar compense em energia (seção VI-B do artigo)."""
    aj = ajustes_nucleos()
    t = pd.DataFrame([{"Origem": org, "a (W)": a, "b (W)": b, "R²": r2, "Potência(2)/Potência(1)": (a + b) / b}
                      for org, (a, b, r2) in aj.items()]).set_index("Origem").loc[["artigo", "restrito", "reprodução"]]
    tex(t, "tabela09_vankempen_ajuste_nucleos", float_format="%.2f")


def figura04_vankempen_dram():
    """Figura 4: potência de DRAM de cada execução contra a taxa de faltas de LLC, configuração padrão,
    no formato da Figura 8b do artigo, com o ajuste linear e a reta do artigo (tracejada)."""
    pad = execucoes_vankempen().query("config == 'padrão'")
    aj = ajustes_dram()
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.2))
    for ax, org in zip(axes, ORIGENS):
        g = pad[pad["origem"] == org]
        for lang in LANGS:
            gl = g[g["lang"] == lang]
            ax.scatter(gl["llc"] / 1e6, gl["W_dram"], color=COR_LANG[lang], s=8, alpha=0.7)
        xs = np.array([g["llc"].min(), g["llc"].max()])
        a, b, r2 = aj[org]
        ax.plot(xs / 1e6, a * xs + b, color="red", lw=1)
        titulo = f"{org}: {num(a * 1e8, '.2f')}·10⁻⁸·x + {num(b, '.2f')}, R² = {num(r2, '.2f')}"
        if org == "restrito":
            a2, b2, r22 = aj["artigo"]
            ax.plot(xs / 1e6, a2 * xs + b2, color="red", lw=1, ls="--")
            titulo += f"; artigo: {num(a2 * 1e8, '.2f')}·10⁻⁸·x + {num(b2, '.2f')}, R² = {num(r22, '.2f')}"
        ax.set_ylim(0, g["W_dram"].max() * 1.15)
        ax.set_ylabel("potência DRAM (W)"); ax.set_xlabel("faltas de LLC por segundo (milhões)")
        ax.yaxis.set_major_formatter(VIRGULA); ax.xaxis.set_major_formatter(VIRGULA)
        ax.set_title(titulo, loc="left", fontsize=8.5)
    legenda_ajuste(fig)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    salvar_figura(fig, "figura04_vankempen_dram")


def tabela10_vankempen_dram():
    """Tabela 10: coeficientes do ajuste linear da potência de DRAM às faltas de LLC (a em W por 10^8
    faltas por segundo) e faixa da razão DRAM/PKG entre execuções, nas duas configurações."""
    aj = ajustes_dram()
    fr = execucoes_vankempen().groupby(["config", "origem"])["fracao"].agg(["min", "max"])
    _, _, _, lo, hi = ARTIGO_VK["dram"]
    a, b, r2 = aj["artigo"]
    linhas = [{"Configuração": "padrão", "Origem": "artigo", "a": a * 1e8, "b (W)": b, "R²": r2,
               "DRAM/PKG mín. (%)": lo, "DRAM/PKG máx. (%)": hi}]
    for org in ORIGENS:
        a, b, r2 = aj[org]
        linhas.append({"Configuração": "padrão", "Origem": org, "a": a * 1e8, "b (W)": b, "R²": r2,
                       "DRAM/PKG mín. (%)": fr.loc[("padrão", org), "min"], "DRAM/PKG máx. (%)": fr.loc[("padrão", org), "max"]})
    for org in ORIGENS:  # o artigo não publica a fração na frequência mínima
        linhas.append({"Configuração": "mín. freq.", "Origem": org,
                       "DRAM/PKG mín. (%)": fr.loc[("mín. freq.", org), "min"], "DRAM/PKG máx. (%)": fr.loc[("mín. freq.", org), "max"]})
    t = pd.DataFrame(linhas).set_index(["Configuração", "Origem"])
    tex(t, "tabela10_vankempen_dram", float_format="%.2f", na_rep="--")


if __name__ == "__main__":
    estatisticas_validacao_vankempen()
    tabela08_vankempen_potencia_fixa()
    figura03_vankempen_nucleos()
    tabela09_vankempen_ajuste_nucleos()
    figura04_vankempen_dram()
    tabela10_vankempen_dram()
