"""Lê <pasta>/resultados/liga.txt, confere com o sorteio e calcula a classificação.

Uso: python3 core/classificacao.py <pasta_da_competicao>
Pontos: vitória 3, empate 1. Desempate: pontos, saldo de gols, gols marcados.
"""
import json
import re
import sys
from collections import defaultdict

LINHA = re.compile(r"^\s+(.+?) (\d+)x(\d+) (.+?)\s*$")


def ler_resultados(path):
    rodadas, atual = [], None
    for linha in open(path, encoding="utf-8"):
        if linha.startswith("RODADA"):
            atual = []
            rodadas.append(atual)
        elif (m := LINHA.match(linha)):
            atual.append((m[1], int(m[2]), int(m[3]), m[4]))
    return rodadas


def conferir_com_sorteio(rodadas, sorteio):
    for i, (res, sor) in enumerate(zip(rodadas, sorteio["rodadas"]), 1):
        a = sorted((h, v) for h, _, _, v in res)
        b = sorted((g["mandante"], g["visitante"]) for g in sor)
        assert a == b, f"rodada {i}: jogos diferentes do sorteio: {set(a) ^ set(b)}"


def classificar(rodadas):
    t = defaultdict(lambda: dict(p=0, j=0, v=0, e=0, d=0, gp=0, gc=0))
    for r in rodadas:
        for h, gh, ga, a in r:
            for eq, gf, gs in ((h, gh, ga), (a, ga, gh)):
                x = t[eq]
                x["j"] += 1; x["gp"] += gf; x["gc"] += gs
                if gf > gs: x["v"] += 1; x["p"] += 3
                elif gf == gs: x["e"] += 1; x["p"] += 1
                else: x["d"] += 1
    return sorted(t.items(), key=lambda kv: (-kv[1]["p"], -(kv[1]["gp"] - kv[1]["gc"]), -kv[1]["gp"]))


if __name__ == "__main__":
    pasta = sys.argv[1].rstrip("/")
    rodadas = ler_resultados(f"{pasta}/resultados/liga.txt")
    conferir_com_sorteio(rodadas, json.load(open(f"{pasta}/rodadas.json", encoding="utf-8")))
    linhas = ["| # | Equipe | Pts | J | V | E | D | GP | GC | SG |", "|---|---|---|---|---|---|---|---|---|---|"]
    for i, (eq, x) in enumerate(classificar(rodadas), 1):
        linhas.append(f"| {i} | {eq} | {x['p']} | {x['j']} | {x['v']} | {x['e']} | {x['d']} | {x['gp']} | {x['gc']} | {x['gp']-x['gc']:+d} |")
    print("\n".join(linhas))
