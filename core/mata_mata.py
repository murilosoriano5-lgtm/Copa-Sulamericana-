"""Confere o mata-mata: chaveamento pela liga, agregados e pênaltis.

Uso: python3 core/mata_mata.py <pasta_da_competicao>
"""
import json
import sys

from classificacao import classificar, ler_resultados


def agregado(t):
    if "jogo_unico" in t:
        h, gh, ga, a = t["jogo_unico"]
        return {h: gh, a: ga}
    (h1, g1, g2, a1), (h2, g3, g4, a2) = t["ida"], t["volta"]
    assert h1 == a2 and a1 == h2, f"ida/volta com times trocados: {t}"
    return {h1: g1 + g4, a1: g2 + g3}


def vencedor(t, avisos):
    ag = agregado(t)
    (a, ga), (b, gb) = ag.items()
    if ga != gb:
        if t.get("penaltis"):
            avisos.append(f"{a} x {b}: pênaltis informados {t['penaltis']}, mas o agregado {ga}-{gb} não empatou")
        return a if ga > gb else b
    pa, pb = t["penaltis"]
    assert pa != pb, f"{a} x {b}: agregado empatado sem decisão"
    return a if pa > pb else b


if __name__ == "__main__":
    pasta = sys.argv[1].rstrip("/")
    tabela = [eq for eq, _ in classificar(ler_resultados(f"{pasta}/resultados/liga.txt"))]
    dados = json.load(open(f"{pasta}/resultados/mata_mata.json", encoding="utf-8"))["fases"]
    avisos, esperados = [], {tuple(sorted((tabela[i], tabela[15 - i]))) for i in range(8)}
    vivos = None
    for fase, confrontos in dados.items():
        pares = {tuple(sorted(agregado(t))) for t in confrontos}
        if fase == "Oitavas":
            assert pares == esperados, f"chaveamento diferente da tabela: {pares ^ esperados}"
        else:
            jogando = {e for p in pares for e in p}
            assert jogando == vivos, f"{fase}: times diferentes dos classificados: {jogando ^ vivos}"
        vivos = {vencedor(t, avisos) for t in confrontos}
        print(f"{fase}: classificados -> {sorted(vivos)}")
    print("CAMPEÃO:", *vivos)
    for a in avisos:
        print("ATENÇÃO:", a)
