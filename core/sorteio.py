"""Sorteio do torneio no formato suíço: 36 equipes, 4 potes, 8 rodadas.

Regras:
  * cada equipe enfrenta 2 equipes de CADA pote (inclusive o próprio): 1 em casa e 1 fora;
  * total: 8 jogos por equipe (4 em casa, 4 fora), 144 jogos, 8 rodadas;
  * ninguém enfrenta a mesma equipe duas vezes;
  * não há jogos entre equipes do mesmo país (SAME_COUNTRY_BLOCKED);
  * cada equipe joga exatamente 1 vez por rodada.

Uso: python3 core/sorteio.py <pasta_da_competicao> [seed]
  lê <pasta>/potes.json e grava <pasta>/rodadas.json e <pasta>/JOGOS_POR_RODADA.md (após validar).
"""
import json
import random
import sys
from collections import defaultdict

SAME_COUNTRY_BLOCKED = True
N_ROUNDS = 8
MAX_STREAK = 3  # máximo de jogos seguidos em casa (ou fora) para a mesma equipe

POTS, TEAMS, POT_OF, COUNTRY = {}, [], {}, {}


def load_pots(path):
    """Carrega potes.json (4 potes x 9 equipes) e preenche as tabelas globais."""
    global POTS, TEAMS, POT_OF, COUNTRY
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    POTS = {int(p): [(e["equipe"], e["pais"]) for e in eq] for p, eq in data["potes"].items()}
    assert sorted(POTS) == [1, 2, 3, 4] and all(len(v) == 9 for v in POTS.values()), \
        "são necessários 4 potes com 9 equipes cada"
    TEAMS = [t for p in sorted(POTS) for t, _ in POTS[p]]
    assert len(set(TEAMS)) == 36, "nomes de equipes repetidos"
    POT_OF = {t: p for p in POTS for t, _ in POTS[p]}
    COUNTRY = {t: c for p in POTS for t, c in POTS[p]}
    return data.get("competicao", "")


def ok_pair(a, b):
    return a != b and not (SAME_COUNTRY_BLOCKED and COUNTRY[a] == COUNTRY[b])


def draw_fixtures(rng):
    """Devolve lista de (mandante, visitante) respeitando potes, país e sem repetir confronto."""
    used = set()      # confrontos já definidos (sem mando)
    games = []

    def add(h, a):
        used.add(frozenset((h, a)))
        games.append((h, a))

    names = {p: [t for t, _ in POTS[p]] for p in POTS}
    # 1) pares de potes distintos: duas permutações (P manda em Q, Q manda em P)
    for p in POTS:
        for q in POTS:
            if p >= q:
                continue
            for host_pot, away_pot in ((p, q), (q, p)):
                for _ in range(10_000):
                    perm = names[away_pot][:]
                    rng.shuffle(perm)
                    pairs = list(zip(names[host_pot], perm))
                    if all(ok_pair(h, a) and frozenset((h, a)) not in used for h, a in pairs):
                        for h, a in pairs:
                            add(h, a)
                        break
                else:
                    return None
    # 2) dentro do pote: permutação sem ciclos de tamanho 1 ou 2 (cada um manda 1 e visita 1)
    for p in POTS:
        for _ in range(10_000):
            perm = names[p][:]
            rng.shuffle(perm)
            pairs = list(zip(names[p], perm))
            if all(ok_pair(h, a) for h, a in pairs) and \
               len({frozenset(x) for x in pairs}) == len(pairs):
                for h, a in pairs:
                    add(h, a)
                break
        else:
            return None
    return games


def schedule_rounds(games, rng, max_steps=400_000):
    """Min-conflicts: atribui cada jogo a uma rodada com 1 jogo por equipe por rodada."""
    m = len(games)
    rnd = [rng.randrange(N_ROUNDS) for _ in range(m)]
    occ = defaultdict(set)  # (equipe, rodada) -> jogos
    for i, (h, a) in enumerate(games):
        occ[(h, rnd[i])].add(i)
        occ[(a, rnd[i])].add(i)

    def conflicts(i, r):
        h, a = games[i]
        return len(occ[(h, r)] - {i}) + len(occ[(a, r)] - {i})

    bad = {i for i in range(m) if conflicts(i, rnd[i])}
    for _ in range(max_steps):
        if not bad:
            return rnd
        i = rng.choice(tuple(bad))
        costs = [conflicts(i, r) for r in range(N_ROUNDS)]
        best = min(costs)
        r = rng.choice([x for x, c in enumerate(costs) if c == best]) if rng.random() > 0.05 \
            else rng.randrange(N_ROUNDS)
        h, a = games[i]
        for t in (h, a):
            occ[(t, rnd[i])].discard(i)
        rnd[i] = r
        for t in (h, a):
            occ[(t, r)].add(i)
        for j in {i} | occ[(h, r)] | occ[(a, r)] | occ[(h, rnd[i])] | occ[(a, rnd[i])]:
            (bad.add if conflicts(j, rnd[j]) else bad.discard)(j)
        # recalcula quem saiu da rodada antiga
        for t in (h, a):
            for r0 in range(N_ROUNDS):
                for j in occ[(t, r0)]:
                    (bad.add if conflicts(j, rnd[j]) else bad.discard)(j)
    return None


def max_streak(rounds):
    worst = 0
    for t in TEAMS:
        seq = []
        for r in rounds:
            for h, a in r:
                if t == h:
                    seq.append("H")
                elif t == a:
                    seq.append("A")
        run = 1
        for x, y in zip(seq, seq[1:]):
            run = run + 1 if x == y else 1
            worst = max(worst, run)
    return worst


def validate(rounds):
    assert len(rounds) == N_ROUNDS and all(len(r) == 18 for r in rounds)
    seen = set()
    home, away = defaultdict(int), defaultdict(int)
    per_pot = defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for r in rounds:
        in_round = [t for g in r for t in g]
        assert sorted(in_round) == sorted(TEAMS), "equipe repetida/faltando na rodada"
        for h, a in r:
            assert frozenset((h, a)) not in seen, f"confronto repetido {h} x {a}"
            seen.add(frozenset((h, a)))
            assert ok_pair(h, a), f"jogo proibido {h} x {a}"
            home[h] += 1
            away[a] += 1
            per_pot[h][POT_OF[a]][0] += 1
            per_pot[a][POT_OF[h]][1] += 1
    for t in TEAMS:
        assert home[t] == 4 and away[t] == 4, f"{t}: {home[t]} casa / {away[t]} fora"
        for p in POTS:
            assert per_pot[t][p] == [1, 1], f"{t} vs pote {p}: {per_pot[t][p]}"
    assert len(seen) == 144


def build(seed):
    rng = random.Random(seed)
    for _ in range(2000):
        games = draw_fixtures(rng)
        if not games:
            continue
        rnd = schedule_rounds(games, rng)
        if rnd is None:
            continue
        rounds = [[g for g, r in zip(games, rnd) if r == k] for k in range(N_ROUNDS)]
        for r in rounds:
            r.sort(key=lambda g: (POT_OF[g[0]], TEAMS.index(g[0])))
        if max_streak(rounds) <= MAX_STREAK:
            validate(rounds)
            return rounds
    raise SystemExit("não encontrou sorteio válido")


def write_md(rounds, seed, path):
    out = [f"# Jogos por rodada (sorteio com seed {seed})\n",
           "Formato: **mandante** x visitante `[pote do mandante · pote do visitante]`\n"]
    for i, r in enumerate(rounds, 1):
        out.append(f"\n## Rodada {i}\n")
        out.append("| # | Mandante | | Visitante | Potes |\n|---|---|---|---|---|")
        for n, (h, a) in enumerate(r, 1):
            out.append(f"| {n} | **{h}** | x | {a} | {POT_OF[h]}·{POT_OF[a]} |")
    out.append("\n## Calendário por equipe (C = casa, F = fora)\n")
    out.append("| Equipe | R1 | R2 | R3 | R4 | R5 | R6 | R7 | R8 |\n|---|---|---|---|---|---|---|---|---|")
    for t in TEAMS:
        cells = []
        for r in rounds:
            for h, a in r:
                if t == h:
                    cells.append(f"C {a}")
                elif t == a:
                    cells.append(f"F {h}")
        out.append(f"| {t} | " + " | ".join(cells) + " |")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out) + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit("uso: python3 core/sorteio.py <pasta_da_competicao> [seed]")
    pasta = sys.argv[1].rstrip("/")
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 2026
    nome = load_pots(f"{pasta}/potes.json")
    rounds = build(seed)
    with open(f"{pasta}/rodadas.json", "w", encoding="utf-8") as f:
        json.dump({"competicao": nome, "seed": seed,
                   "rodadas": [[{"mandante": h, "visitante": a} for h, a in r] for r in rounds]},
                  f, ensure_ascii=False, indent=2)
    write_md(rounds, seed, f"{pasta}/JOGOS_POR_RODADA.md")
    print(f"OK - {nome}: sorteio válido. Maior sequência casa/fora:", max_streak(rounds))
