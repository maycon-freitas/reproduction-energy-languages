"""Seção 1.4: Tabela 1.

Saídas, na ordem em que aparecem no relatório:
    tabela01_paralelismo(): Tabela 1, mecanismo de paralelismo no código e núcleos ativos (task-clock)

Uso, na raiz do repositório: python3 relatorio/scripts/1_paralelismo.py
"""
import pandas as pd
from comum import (mecanismo_cpp, mecanismo_py, medianas_vankempen, ORDEM, tex)


def tabela01_paralelismo():
    """Tabela 1: mecanismo de paralelismo no código e núcleos ativos medidos pelo task-clock (Seção 1.4)."""
    med = medianas_vankempen()
    t = pd.DataFrame(index=pd.Index(ORDEM, name="Benchmark"))
    for lang, mecanismo in [("C++", mecanismo_cpp), ("Python", mecanismo_py)]:
        t[(lang, "mecanismo")] = [mecanismo(b) for b in ORDEM]
        # mediana das 21 execuções da configuração padrão, reprodução (máquina com oito núcleos)
        t[(lang, "núcleos")] = med.loc[("reprodução", "padrão", lang), "nucleos"].reindex(ORDEM).values
    t.columns = pd.MultiIndex.from_tuples(t.columns)
    tex(t, "tabela01_paralelismo", na_rep="--", multicolumn_format="c", float_format="%.2f")


if __name__ == "__main__":
    tabela01_paralelismo()
