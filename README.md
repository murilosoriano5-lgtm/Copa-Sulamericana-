# Copa Sul-Americana em Formato Suíço (e Libertadores)

Repositório único com o motor de sorteio compartilhado e uma pasta por competição.

```
core/sorteio.py        motor: sorteio, validação e geração dos jogos
libertadores/          potes.json + JOGOS_POR_RODADA.md + rodadas.json (pronto)
sula/                  potes.json, jogos, resultados e classificação da Sul-Americana
ESTUDO.md              material de estudo
```
Jogos prontos: [`libertadores/JOGOS_POR_RODADA.md`](libertadores/JOGOS_POR_RODADA.md). Material de estudo: [`ESTUDO.md`](ESTUDO.md).

## Formato
- 36 equipes divididas em **4 potes de 9** (composição em `<competição>/potes.json`).
- **Fase de liga única** (formato suíço): não há grupos, todas as equipes entram numa mesma tabela.
- Cada equipe enfrenta **2 equipes de cada pote** (incluindo o próprio): **1 jogo em casa e 1 fora** contra cada pote.
- Resultado: **8 jogos por equipe (4 em casa, 4 fora)**, **144 jogos** no total, **8 rodadas de 18 jogos**.

## Regras aplicadas no sorteio
1. Nenhum confronto se repete (mesmos dois times não se enfrentam duas vezes).
2. Cada equipe joga exatamente uma vez por rodada.
3. **Não há jogos entre equipes do mesmo país** (ex.: os 4 mexicanos Monterrey, Tigres, Chivas e Pumas não se enfrentam;
   idem os 4 times dos EUA). Para desligar, use `SAME_COUNTRY_BLOCKED = False` em `core/sorteio.py`.
4. Nenhuma equipe joga mais de 3 vezes seguidas em casa ou fora.
5. Sorteio reprodutível: a mesma *seed* gera sempre o mesmo resultado.

## Como funciona o código (`core/sorteio.py`)
| Etapa | O que faz |
|---|---|
| `draw_fixtures` | Define **quem enfrenta quem e quem manda o jogo**. Para cada par de potes sorteia duas permutações (pote A recebe pote B e vice-versa); dentro do pote usa uma permutação sem ciclos de 1 ou 2 elementos. |
| `schedule_rounds` | Distribui os 144 jogos em 8 rodadas (**coloração de arestas**) por busca local *min-conflicts*. |
| `max_streak` | Mede a maior sequência de mandos iguais (limite = 3). |
| `validate` | Confere todas as regras acima; o script só grava arquivos se tudo passar. |

## Como rodar
```bash
python3 core/sorteio.py libertadores        # seed padrão 2026
python3 core/sorteio.py sula 123            # outra seed = outro sorteio
```
Gera `rodadas.json` e `JOGOS_POR_RODADA.md` dentro da pasta da competição (rodadas + calendário de cada equipe). Requer apenas Python 3.

## Como preencher a Sul-Americana
Edite `sula/potes.json`: 4 potes (`"1"` a `"4"`) com 9 objetos `{"equipe": "...", "pais": "XXX"}` cada. O país é usado na regra de não enfrentar equipes do mesmo país. O script avisa se faltar equipe.

## Observações sobre a lista de equipes (Libertadores)
- Os potes têm 9 equipes cada (36). A lista de vagas por país tem pequenas diferenças (ex.: México e EUA listam 4 clubes para "3 vagas"); foram usados os clubes dos **potes**.
- Nomes: `Olímpia` (Paraguai) e `Olímpia (HON)` (Honduras); `Alianza Lima` (Peru) e `Alianza (SLV)` (El Salvador).

## Resultados e classificação
- `core/classificacao.py <pasta>`: lê `resultados/liga.txt`, confere se os jogos são os do sorteio e calcula a tabela.
- `core/mata_mata.py <pasta>`: confere chaveamento (top 16), agregados e pênaltis até o campeão.
- Sul-Americana concluída: veja [`sula/RESULTADOS.md`](sula/RESULTADOS.md).

## Próximos passos sugeridos
- Tabela de classificação (3 pts vitória, 1 empate) e critérios de desempate.
- Definir quem se classifica (ex.: top 8 direto, 9º–24º em playoff) e o mata-mata.
