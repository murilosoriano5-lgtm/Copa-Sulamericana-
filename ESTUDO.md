# Para estudar

## O que é o formato suíço / liga única
- Todos jogam numa **tabela única**, mas cada equipe pega só uma parte dos adversários, definida por **potes** (força).
- Usado na **UEFA Champions League desde 2024/25** (36 equipes, 8 jogos). O nosso torneio segue a mesma ideia, com uma diferença:
  lá cada time enfrenta **2 por pote**, exatamente como aqui.
- Leitura: busque "UEFA Champions League league phase format" e "Swiss-system tournament" (Wikipedia).

## Por que o sorteio é um problema de matemática
1. **Potes e mando** → "cada time tem 1 jogo em casa e 1 fora contra cada pote" vira uma **permutação** (cada time manda em exatamente um adversário do pote).
2. **Rodadas** → dividir os jogos em 8 rodadas onde ninguém repete é uma **coloração de arestas** de um grafo 8-regular (cada rodada = uma cor = um *matching perfeito*).
3. **Busca local (min-conflicts)** → começa com um chute e vai trocando jogos de rodada até zerar conflitos.

Termos para pesquisar: *edge coloring*, *perfect matching*, *round-robin scheduling*, *min-conflicts heuristic*, *constraint satisfaction problem (CSP)*.

## Exercícios
1. Mude `SAME_COUNTRY_BLOCKED` para `False` e rode com várias seeds: o que muda?
2. Altere `MAX_STREAK` para 2 e veja se ainda existe solução.
3. Escreva a função que calcula a tabela de classificação a partir de resultados.
