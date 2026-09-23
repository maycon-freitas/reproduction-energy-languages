"""Funções e constantes compartilhadas pelos scripts numerados deste diretório.

Cada script numerado gera as saídas de uma seção do relatório (tabelas, figuras e
estatísticas citadas no texto) e pode ser executado isoladamente, na raiz do repositório:

    python3 relatorio/scripts/2_pereira.py

Estrutura esperada do repositório (RAIZ):
    pereira/dados/originais/{C++,Python}.csv   dados publicados por Pereira et al. (2021)
    pereira/dados/reproducao/{C++,Python}.csv  campanha de reprodução
    pereira/{C++,Python}/<benchmark>/          fontes e Makefiles dos benchmarks
    vankempen/data/osmium/                     dados publicados por van Kempen et al. (2024)
    vankempen/data/tesla/                      campanha de reprodução
Saídas:
    relatorio/tabelas/tabelaNN_*.tex e .csv
    relatorio/figuras/figuraNN_*.png
    relatorio/estatisticas/*.txt
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import optimize, stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

RAIZ = Path(__file__).resolve().parents[2]
TABELAS = RAIZ / "relatorio/tabelas"
FIGURAS = RAIZ / "relatorio/figuras"
ESTATISTICAS = RAIZ / "relatorio/estatisticas"
for _d in (TABELAS, FIGURAS, ESTATISTICAS):
    _d.mkdir(parents=True, exist_ok=True)

# pidigits fica fora de todas as tabelas e figuras: a versão Python executa com saída incorreta
# com gmpy2 >= 2.1, nos dados publicados e nas reproduções. fasta não tem versão C++ no
# repositório de van Kempen et al. (2024).
ORDEM = ["binary-trees", "fannkuch-redux", "fasta", "k-nucleotide", "mandelbrot",
         "n-body", "regex-redux", "reverse-complement", "spectral-norm"]
PARES = [b for b in ORDEM if b != "fasta"]  # benchmarks com as duas linguagens nos dois estudos
LANGS = ["C++", "Python"]
ORIGENS = ["restrito", "reprodução"]  # restrito: dados publicados pelos autores, só C++ e Python
COR = {"restrito": "#1f77b4", "reprodução": "#ff7f0e"}
COR_LANG = {"C++": "#1f77b4", "Python": "#ff7f0e"}

# valores impressos nos artigos
ARTIGO_PEREIRA = {
    "tabela4": {"C++": [77.5, 3155, 1.0, 1.0], "Python": [4390, 145178, 75.88 / 1.34, 71.90 / 1.56]},  # base C -> base C++
    "tabela5": {"C++": 0.966667, "Python": 0.933333},   # Spearman energia x tempo, dez benchmarks
    "tabela6": {"C++": [8.54, 88.94], "Python": [358.75, 87.98]},  # DRAM média (J), CPU (%)
}
ARTIGO_VK = {
    "potencia": (189.8, 0.5),                  # seção VI-A: frequência mínima, um núcleo
    "nucleos": (31.0, 246.0, 0.72),            # Fig. 8a: a*log2(x) + b, R2
    "dram": (1.68e-8, 12.0, 0.93, 2.0, 8.0),   # Fig. 8b: a*x + b, R2, faixa DRAM/PKG (%)
}

# ---------------------------------------------------------------- utilidades


def num(v, fmt):
    """Número com vírgula decimal."""
    return format(v, fmt).replace(".", ",")


VIRGULA = matplotlib.ticker.FuncFormatter(lambda v, _: num(v, "g"))


def tex(df, nome, **kw):
    """Grava a tabela em CSV (valores completos) e em LaTeX (booktabs, vírgula decimal)."""
    df.round(4).to_csv(TABELAS / f"{nome}.csv")
    corpo = df.to_latex(escape=True, **kw)
    corpo = re.sub(r"(\d)\.(\d)", r"\1,\2", corpo)
    corpo = corpo.replace("R²", "$R^2$")
    (TABELAS / f"{nome}.tex").write_text(corpo)
    print(f"tabela gravada: relatorio/tabelas/{nome}.tex")


def salvar_figura(fig, nome):
    fig.savefig(FIGURAS / f"{nome}.png", dpi=150)
    plt.close(fig)
    print(f"figura gravada: relatorio/figuras/{nome}.png")


def salvar_estatisticas(nome, linhas):
    texto = "\n".join(linhas) + "\n"
    (ESTATISTICAS / f"{nome}.txt").write_text(texto)
    print(texto)
    print(f"estatísticas gravadas: relatorio/estatisticas/{nome}.txt")


def cv(x):
    return 100 * np.std(x, ddof=1) / np.mean(x)


def media_aparada(x):
    """Descarta os 20% mais baixos e os 20% mais altos (seção 5 de Pereira et al., 2021)."""
    x = np.sort(np.asarray(x))
    k = int(0.2 * len(x))
    return x[k:len(x) - k].mean()


def rea_parker(r):
    """Classificação de Rea e Parker, adotada por Pereira et al. (2021) na Tabela 5."""
    r = abs(r)
    for lim, nome in [(0.1, "desprezível"), (0.2, "fraca"), (0.4, "moderada"),
                      (0.6, "relativamente forte"), (0.8, "forte")]:
        if r < lim:
            return nome
    return "muito forte"


plt.rcParams.update({"font.size": 9})

# ---------------------------------------------------------------- Pereira et al. (2021)

COLUNAS_PEREIRA = ["bench", "PACKAGE", "CORE", "GPU", "DRAM", "tempo"]
VOLTA = 2**32 / 16384  # capacidade do contador RAPL de 32 bits na unidade de energia (262 144 J)


def ler_csv_pereira(caminho, corrigir=True):
    d = pd.read_csv(caminho, sep=r"\s*[;,]\s*", engine="python", header=None, names=COLUNAS_PEREIRA)
    d["bench"] = d["bench"].str.strip()
    d["campanha"] = d.groupby("bench").cumcount() // 10
    if corrigir:  # leitura negativa = estouro do contador; soma a capacidade em vez de descartar
        for c in ["PACKAGE", "CORE", "DRAM"]:
            d.loc[d[c] < 0, c] += VOLTA
    return d


def campanha_do_artigo(d):
    """O arquivo C++ publicado tem duas campanhas; a Tabela 3 do artigo usa a segunda,
    exceto em fannkuch-redux, cuja segunda campanha tem execuções inválidas."""
    if d["campanha"].max() == 0:
        return d
    return d[((d["campanha"] == 1) & (d["bench"] != "fannkuch-redux")) |
             ((d["campanha"] == 0) & (d["bench"] == "fannkuch-redux"))]


def caminho_pereira(origem, lang):
    pasta = "originais" if origem == "restrito" else "reproducao"
    return RAIZ / "pereira/dados" / pasta / f"{lang}.csv"


@lru_cache(maxsize=None)
def execucoes_pereira():
    """Todas as execuções válidas, com energia CORE + DRAM (composição que reproduz a Tabela 3 do artigo)."""
    partes = []
    for origem in ORIGENS:
        for lang in LANGS:
            d = ler_csv_pereira(caminho_pereira(origem, lang))
            if origem == "restrito":
                d = campanha_do_artigo(d)
            d = d[(d["tempo"] > 10) & (d["bench"].isin(ORDEM))].copy()
            d["origem"], d["lang"] = origem, lang
            partes.append(d)
    todos = pd.concat(partes, ignore_index=True)
    todos["E"] = todos["CORE"] + todos["DRAM"]
    return todos


@lru_cache(maxsize=None)
def resultados_pereira():
    """Média aparada a 20% por origem, linguagem e benchmark."""
    res = execucoes_pereira().groupby(["origem", "lang", "bench"])[["E", "CORE", "DRAM", "PACKAGE", "tempo"]].agg(media_aparada)
    res = res.reindex(pd.MultiIndex.from_product([ORIGENS, LANGS, ORDEM], names=res.index.names))
    res["ratio"] = res["E"] / res["tempo"]        # J/ms, isto é, potência média em kW
    res["CPU_pct"] = 100 * res["CORE"] / res["E"]  # fração da energia atribuída à CPU
    return res


def razoes_pereira():
    """Razão Python/C++ por benchmark, colunas (origem, métrica)."""
    w = resultados_pereira().unstack("lang")
    raz = pd.DataFrame({"Energia": w[("E", "Python")] / w[("E", "C++")],
                        "Tempo": w[("tempo", "Python")] / w[("tempo", "C++")]}).unstack("origem")
    return raz.reorder_levels([1, 0], axis=1).loc[ORDEM]


def tabela_energia_tempo(origem, nome):
    """Formato da Tabela 3 do artigo: energia, tempo e razão por benchmark, uma origem."""
    t = resultados_pereira().loc[origem, ["E", "tempo", "ratio"]].rename(
        columns={"E": "Energy (J)", "tempo": "Time (ms)", "ratio": "Ratio (J/ms)"})
    t = t.unstack("lang").swaplevel(axis=1)
    t = t.reindex(columns=pd.MultiIndex.from_product([LANGS, ["Energy (J)", "Time (ms)", "Ratio (J/ms)"]])).loc[ORDEM]
    t.index.name = "Benchmark"
    tex(t, nome, float_format=lambda v: f"{v:.3f}" if v < 1 else f"{v:.2f}", multicolumn_format="c")


def figura_energia_tempo(lang, nome):
    """Formato das Figuras 7 a 9 do artigo: CPU e DRAM empilhados, tempo em linha e razão
    energia/tempo em pontos, num eixo próprio sem escala visível, para não coincidir com a linha."""
    res = resultados_pereira()
    x = np.arange(len(ORDEM))
    e_max = res.loc[(slice(None), lang), "E"].max()
    t_max = res.loc[(slice(None), lang), "tempo"].max()
    r_max = res.loc[(slice(None), lang), "ratio"].max()
    fig, axes = plt.subplots(2, 1, figsize=(8, 6.2), sharex=True)
    for ax, org in zip(axes, ORIGENS):
        r = res.loc[(org, lang)].loc[ORDEM]
        ax.bar(x, r["CORE"], color=COR[org], alpha=0.45)
        ax.bar(x, r["DRAM"], bottom=r["CORE"], color=COR[org])
        ax.set_ylim(0, e_max * 1.12)
        ax.set_ylabel("Joules")
        ax2 = ax.twinx()
        ax2.plot(x, r["tempo"], "k-", lw=1, label="Tempo")
        ax2.set_ylim(0, t_max * 1.12)
        ax2.set_ylabel("ms")
        ax3 = ax.twinx()
        ax3.set_axis_off()
        ax3.scatter(x, r["ratio"], color="green", s=26, edgecolor="white", linewidth=0.8, zorder=4, label="Razão")
        ax3.set_ylim(-0.9 * r_max, r_max * 1.15)  # pontos na metade superior do painel
        for i, v in enumerate(r["ratio"]):
            ax3.annotate(num(v, ".3f"), (i, v), fontsize=7, xytext=(5, 0), textcoords="offset points",
                         va="center", bbox=dict(fc="white", ec="none", alpha=0.75, pad=0.3))
        ax.set_xticks(x)
        ax.set_xticklabels(ORDEM, rotation=30, ha="right")
        ax.set_title(f"{lang}: {org}", loc="left")
    h = [Patch(color=COR[o], alpha=a) for o in ORIGENS for a in (0.45, 1.0)]
    l = [f"{m} ({o})" for o in ORIGENS for m in ("CPU", "DRAM")]
    h += [plt.Line2D([], [], color="k", lw=1), plt.Line2D([], [], color="green", marker="o", ls="")]
    l += ["Tempo", "Razão"]
    fig.legend(h, l, loc="upper center", ncol=6, frameon=False, fontsize=8)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    salvar_figura(fig, nome)


def mecanismo_cpp(bench):
    d = RAIZ / "pereira/C++" / bench
    if not d.exists():
        return "--"
    mk = (d / "Makefile").read_text(errors="ignore") if (d / "Makefile").exists() else ""
    src = "".join(f.read_text(errors="ignore") for f in d.iterdir() if f.is_file() and f.name != "Makefile")
    achados = []
    if "#pragma omp" in src:
        achados.append("OpenMP")
    if re.search(r"std::thread|std::async|pthread_create", src):
        achados.append("threads")
    if not achados and re.search(r"-fopenmp|-l?pthread", mk):
        return "só flag"
    return ", ".join(achados) or "nenhum"


def mecanismo_py(bench):
    d = RAIZ / "pereira/Python" / bench
    if not d.exists():
        return "--"
    src = "".join(f.read_text(errors="ignore") for f in d.iterdir() if f.is_file() and f.name != "Makefile")
    return "multiprocessing" if "multiprocessing" in src else "nenhum"


# ---------------------------------------------------------------- van Kempen et al. (2024)

CONFIGS = {"padrão": "docker-default", "mín. freq.": "docker-min-freq-cpuset"}
MAQUINA = {"restrito": "osmium", "reprodução": "tesla"}


def ler_vankempen(origem, config, benchmarks=tuple(ORDEM)):
    """Uma linha por execução. O medidor grava um JSON por linha; o aquecimento não é gravado.
    O servidor dos autores (osmium) tem dois soquetes: PKG e DRAM são somados entre eles."""
    pasta = next((RAIZ / "vankempen/data" / MAQUINA[origem]).glob(CONFIGS[config] + "*"))
    linhas = []
    for arq in sorted(pasta.glob("*/*.json")):
        if arq.parent.name not in LANGS or arq.stem not in benchmarks:
            continue
        for i, l in enumerate(arq.read_text().splitlines()):
            r = json.loads(l)
            t = r["runtime_ms"] / 1000
            amostras = [e for s in r["energy_samples"] for e in s["energy"]]
            linhas.append({"origem": origem, "config": config, "lang": arq.parent.name, "bench": arq.stem,
                           "exec": i, "tempo": t,
                           "PKG": sum(e["pkg"] for e in amostras), "DRAM": sum(e["dram"] for e in amostras),
                           "PP0": sum(e.get("pp0", 0) for e in amostras),
                           "nucleos": r["counters"]["PERF_COUNT_SW_TASK_CLOCK"] / 1e9 / t,  # núcleos ativos médios
                           "llc": r["counters"]["PERF_COUNT_HW_CACHE_MISSES"] / t})         # faltas de LLC por segundo
    return pd.DataFrame(linhas)


@lru_cache(maxsize=None)
def execucoes_vankempen():
    todos = pd.concat([ler_vankempen(o, c) for o in ORIGENS for c in CONFIGS], ignore_index=True)
    todos["E"] = todos["PKG"] + todos["DRAM"]              # fixed_time.py dos autores
    todos["W"] = todos["E"] / todos["tempo"]
    todos["W_pkg"] = todos["PKG"] / todos["tempo"]          # normalize_cores.py
    todos["W_dram"] = todos["DRAM"] / todos["tempo"]        # dram.py
    todos["fracao"] = 100 * todos["DRAM"] / todos["PKG"]    # dram.py: DRAM/PKG por execução
    return todos


@lru_cache(maxsize=None)
def medianas_vankempen():
    """Mediana das execuções, método dos scripts dos autores."""
    return execucoes_vankempen().groupby(["origem", "config", "lang", "bench"])[
        ["tempo", "E", "PKG", "DRAM", "W", "W_pkg", "nucleos", "llc", "fracao"]].median()


def log_fit(x, a, b):
    return a * np.log2(x) + b


def ajustes_nucleos():
    """Ajuste a*log2(x) + b da potência PKG ao número de núcleos, configuração padrão (Fig. 8a)."""
    pad = execucoes_vankempen().query("config == 'padrão'")
    out = {"artigo": ARTIGO_VK["nucleos"]}
    for org, g in pad.groupby("origem"):
        (a, b), _ = optimize.curve_fit(log_fit, g["nucleos"], g["W_pkg"])
        res = g["W_pkg"] - log_fit(g["nucleos"], a, b)
        out[org] = (a, b, 1 - (res ** 2).sum() / ((g["W_pkg"] - g["W_pkg"].mean()) ** 2).sum())
    return out


def ajustes_dram():
    """Ajuste linear da potência de DRAM à taxa de faltas de LLC, configuração padrão (Fig. 8b)."""
    pad = execucoes_vankempen().query("config == 'padrão'")
    out = {"artigo": ARTIGO_VK["dram"][:3]}
    for org, g in pad.groupby("origem"):
        lr = stats.linregress(g["llc"], g["W_dram"])
        out[org] = (lr.slope, lr.intercept, lr.rvalue ** 2)
    return out


def legenda_ajuste(fig):
    h = [Patch(color=COR_LANG[l]) for l in LANGS]
    h += [plt.Line2D([], [], color="red", lw=1), plt.Line2D([], [], color="red", lw=1, ls="--")]
    fig.legend(h, LANGS + ["ajuste restrito / reprodução", "ajuste do artigo"],
               loc="upper center", ncol=4, frameon=False)


def razoes_vankempen():
    """Razão Python/C++ por benchmark, colunas (origem, configuração, métrica)."""
    w = medianas_vankempen().unstack("lang")
    raz = pd.DataFrame({"Tempo": w[("tempo", "Python")] / w[("tempo", "C++")],
                        "Energia": w[("E", "Python")] / w[("E", "C++")]}).dropna()
    raz = raz.unstack(["origem", "config"]).reorder_levels([1, 2, 0], axis=1)
    return raz.reindex(columns=pd.MultiIndex.from_product([ORIGENS, list(CONFIGS), ["Tempo", "Energia"]])).loc[PARES]


# ---------------------------------------------------------------- comparação entre os estudos

CONJUNTOS = [("Pereira", "restrito"), ("Pereira", "reprodução"),
             ("van Kempen", "restrito, padrão"), ("van Kempen", "restrito, mín. freq."),
             ("van Kempen", "reprodução, padrão"), ("van Kempen", "reprodução, mín. freq.")]


def razoes_comparadas(metrica):
    """Razão Python/C++ nos oito benchmarks comuns, uma coluna por conjunto."""
    per, vk = razoes_pereira(), razoes_vankempen()
    t = pd.DataFrame(index=pd.Index(PARES, name="Benchmark"))
    for org in ORIGENS:
        t[("Pereira", org)] = per[(org, metrica)].reindex(PARES).values
    for org in ORIGENS:
        for cfg in CONFIGS:
            t[("van Kempen", f"{org}, {cfg}")] = vk[(org, cfg, metrica)].reindex(PARES).values
    t.columns = pd.MultiIndex.from_tuples(t.columns)
    return t[CONJUNTOS]


def tabela_razoes(metrica, nome):
    t = razoes_comparadas(metrica)
    # configuração num terceiro nível de cabeçalho, para caber na largura do texto
    t.columns = pd.MultiIndex.from_tuples([(e, c.split(", ")[0], c.split(", ")[1] if ", " in c else "")
                                           for e, c in t.columns])
    tex(t, nome, float_format="%.2f", multicolumn_format="c")
