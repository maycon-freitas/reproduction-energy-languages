"""Seção 2, reprodução de Pereira et al. (2021): Tabelas 2 a 7, Figuras 1 e 2 e as estatísticas citadas nas Seções 2.1 e 2.2.

Saídas, na ordem em que aparecem no relatório:
    estatisticas_validacao_pereira(): estatísticas da Seção 2.1 (composição da energia, fração CORE/PACKAGE, leituras negativas)
    tabela02_pereira_restrito(): Tabela 2, energia, tempo e razão por benchmark, dados restritos
    tabela03_pereira_reproducao(): Tabela 3, energia, tempo e razão por benchmark, reprodução
    figura01_pereira_cpp(): Figura 1, energia, tempo e razão em C++
    figura02_pereira_python(): Figura 2, energia, tempo e razão em Python
    estatisticas_cv_pereira(): estatísticas da Seção 2.2 (coeficiente de variação das dez execuções)
    tabela04_pereira_dram(): Tabela 4, energia de DRAM por benchmark
    tabela05_pereira_fracao_cpu(): Tabela 5, DRAM média e fração da energia atribuída à CPU
    tabela06_pereira_agregados(): Tabela 6, médias dos nove benchmarks normalizadas por C++
    tabela07_pereira_spearman(): Tabela 7, correlação de Spearman entre energia e tempo

Uso, na raiz do repositório: python3 relatorio/scripts/2_pereira.py
"""
import pandas as pd
from comum import (ARTIGO_PEREIRA, caminho_pereira, cv, execucoes_pereira, figura_energia_tempo,
                   LANGS, ler_csv_pereira, num, ORDEM, ORIGENS, rea_parker, resultados_pereira,
                   salvar_estatisticas, tabela_energia_tempo, tex)


def estatisticas_validacao_pereira():
    """Estatísticas da Seção 2.1: composição da energia (CORE + DRAM contra PACKAGE + DRAM),
    fração CORE/PACKAGE em cada processador e leituras negativas de energia nos dados."""
    res = resultados_pereira()
    L = ["Validação do método de Pereira et al. (2021) com os dados restritos", ""]
    L.append("Composição da energia, C++ restrito (média aparada): CORE+DRAM contra PACKAGE+DRAM")
    for b in ORDEM:
        r = res.loc[("restrito", "C++", b)]
        core, pkg = r["CORE"] + r["DRAM"], r["PACKAGE"] + r["DRAM"]
        L.append(f"  {b:20s} CORE+DRAM {num(core, '.2f'):>9s} J   PACKAGE+DRAM {num(pkg, '.2f'):>9s} J   (+{num(100 * (pkg / core - 1), '.0f')}%)")
    L += ["", "CORE como fração de PACKAGE, por benchmark (mín. e máx.)"]
    for org in ORIGENS:
        f = 100 * res.loc[org, "CORE"] / res.loc[org, "PACKAGE"]
        L.append(f"  {org:10s} {num(f.min(), '.0f')}% a {num(f.max(), '.0f')}%")
    L += ["", "Leituras negativas (estouro do contador de 32 bits), antes da correção"]
    for org in ORIGENS:
        n = 0
        for lang in LANGS:
            d = ler_csv_pereira(caminho_pereira(org, lang), corrigir=False)
            n += int((d[["PACKAGE", "CORE", "DRAM"]] < 0).any(axis=1).sum())
        L.append(f"  {org:10s} {n}")
    salvar_estatisticas("validacao_pereira", L)


def tabela02_pereira_restrito():
    """Tabela 2: energia, tempo e razão por benchmark, dados restritos de Pereira et al. (2021)."""
    tabela_energia_tempo("restrito", "tabela02_pereira_restrito")


def tabela03_pereira_reproducao():
    """Tabela 3: energia, tempo e razão por benchmark, reprodução de Pereira et al. (2021)."""
    tabela_energia_tempo("reprodução", "tabela03_pereira_reproducao")


def figura01_pereira_cpp():
    """Figura 1: energia de CPU e DRAM, tempo e razão por benchmark em C++, restrito e reprodução."""
    figura_energia_tempo("C++", "figura01_pereira_cpp")


def figura02_pereira_python():
    """Figura 2: energia de CPU e DRAM, tempo e razão por benchmark em Python, restrito e reprodução."""
    figura_energia_tempo("Python", "figura02_pereira_python")


def estatisticas_cv_pereira():
    """Estatísticas da Seção 2.2: coeficiente de variação das dez execuções por benchmark e linguagem."""
    c = execucoes_pereira().groupby(["origem", "lang", "bench"])[["E", "tempo"]].agg(cv)
    L = ["Coeficiente de variação (%) das dez execuções, Pereira et al. (2021)", ""]
    for org in ORIGENS:
        d = c.loc[org]
        for m, nome in [("E", "energia"), ("tempo", "tempo")]:
            mx = d[m].idxmax()
            L.append(f"{org:10s} {nome:8s}: abaixo de 2% em {int((d[m] < 2).sum())} de {len(d)}; "
                     f"máximo {num(d[m].max(), '.1f')}% ({mx[1]}, {mx[0]})")
    L += ["", "Valores por benchmark"]
    t = c.unstack(["origem", "lang"]).round(2)
    L.append(t.to_string())
    salvar_estatisticas("cv_pereira", L)


def tabela04_pereira_dram():
    """Tabela 4: energia de DRAM por benchmark, restrito e reprodução, com a média dos nove."""
    d = resultados_pereira()["DRAM"].unstack(["origem", "lang"]).loc[ORDEM]
    d = d.reindex(columns=pd.MultiIndex.from_product([ORIGENS, LANGS]))
    d.loc["média"] = d.mean()
    d.index.name = "Benchmark"
    tex(d, "tabela04_pereira_dram", float_format=lambda v: f"{v:.0f}" if v >= 100 else f"{v:.1f}", multicolumn_format="c")


def tabela05_pereira_fracao_cpu():
    """Tabela 5: energia média de DRAM e fração da energia atribuída à CPU, CPU/(CPU+DRAM),
    calculada por benchmark e depois tirada a média (formato da Tabela 6 do artigo)."""
    r = resultados_pereira().loc[("reprodução", slice(None), ORDEM)]
    t = r.groupby("lang").agg(**{"DRAM média (J)": ("DRAM", "mean"), "CPU (%)": ("CPU_pct", "mean")})
    artigo = pd.DataFrame(ARTIGO_PEREIRA["tabela6"], index=t.columns).T
    t = pd.concat({"reprodução": t, "artigo": artigo}, names=["Origem", "Linguagem"])
    tex(t, "tabela05_pereira_fracao_cpu", float_format="%.2f")


def tabela06_pereira_agregados():
    """Tabela 6: médias dos nove benchmarks, absolutas e normalizadas por C++ (critério da Tabela 4
    do artigo; os valores do artigo são convertidos da base C para a base C++)."""
    m = resultados_pereira().loc[("reprodução", slice(None), ORDEM), ["E", "tempo"]].groupby("lang").mean()
    t = m.rename(columns={"E": "Energy média (J)", "tempo": "Time médio (ms)"})
    t["Energy normalizada"] = m["E"] / m.loc["C++", "E"]
    t["Time normalizado"] = m["tempo"] / m.loc["C++", "tempo"]
    artigo = pd.DataFrame(ARTIGO_PEREIRA["tabela4"], index=t.columns).T
    t = pd.concat({"reprodução": t, "artigo": artigo}, names=["Origem", "Linguagem"])
    tex(t, "tabela06_pereira_agregados", float_format="%.2f")


def tabela07_pereira_spearman():
    """Tabela 7: correlação de Spearman entre energia e tempo por linguagem (Tabela 5 do artigo).
    O artigo calcula sobre dez benchmarks; reprodução e restrito, sobre os nove desta análise."""
    res = resultados_pereira()
    linhas = [{"Origem": org, "Linguagem": l,
               "Spearman E x T": res.loc[(org, l), "E"].corr(res.loc[(org, l), "tempo"], method="spearman")}
              for org in ["reprodução", "restrito"] for l in LANGS]
    linhas += [{"Origem": "artigo", "Linguagem": l, "Spearman E x T": ARTIGO_PEREIRA["tabela5"][l]} for l in LANGS]
    t = pd.DataFrame(linhas)
    t["Classificação"] = t["Spearman E x T"].map(rea_parker)
    tex(t.set_index(["Origem", "Linguagem"]), "tabela07_pereira_spearman", float_format="%.2f")


if __name__ == "__main__":
    estatisticas_validacao_pereira()
    tabela02_pereira_restrito()
    tabela03_pereira_reproducao()
    figura01_pereira_cpp()
    figura02_pereira_python()
    estatisticas_cv_pereira()
    tabela04_pereira_dram()
    tabela05_pereira_fracao_cpu()
    tabela06_pereira_agregados()
    tabela07_pereira_spearman()
