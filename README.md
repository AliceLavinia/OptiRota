# OptiRota

> Um sistema acadêmico-profissional de **otimização de rotas** para logística de última milha, projetado para consolidar **Estruturas de Dados**, **Algoritmos de Caminho Mínimo** e **Heurísticas de VRP** em um projeto completo.


## ✨ Sumário Executivo

O **OptiRota** é um projeto universitário avançado que resolve um problema real de **last-mile delivery**. A aplicação lê dados **OpenStreetMap (OSM)** para construir um **grafo navegável** e oferece dois níveis de solução:

1. **Caminho mínimo** entre pares de pontos (Dijkstra e A\*) com análise de complexidade *Big-O* e uso de **fila de prioridade (heap binário)**.
2. **Roteamento com múltiplas paradas (VRP)** com **capacidade (CVRP)** e **janelas de tempo (VRPTW)**, via heurística construtiva (**Vizinho Mais Próximo + Inserção**) apoiada pelos tempos/distâncias pré-computados com A\*.

O projeto enfatiza **engenharia de dados** (parsing/filtragem OSM), **arquitetura modular**, **qualidade** (testes unitários/integrados e benchmarking) e **gestão ágil** (sprints, papéis claros e critérios de aceite).

---

## 🧭 Arquitetura (Visão Geral)

A arquitetura do sistema conecta os dados reais do OSM a um grafo dirigido e ponderado. Esse grafo alimenta os algoritmos de busca de caminho (Dijkstra e A\*), que por sua vez são usados pelo módulo de VRP para gerar rotas com múltiplas paradas sob restrições. Um módulo de QA garante a validade e o desempenho com testes e benchmarks.

---

## 🔧 Tecnologias e Conceitos-chave

* **OpenStreetMap (OSM)** para dados viários (nodes/ways/relations + tags).
* **Parsing** com biblioteca (ex.: `pyroutelib3`) ou parser próprio.
* **Grafo dirigido e ponderado**: vértices = cruzamentos; arestas = segmentos (respeitando `oneway`, `access`, etc.). Pesos: distância (Haversine/UTM) e/ou tempo.
* **Estruturas de Dados**: *Priority Queue* (heap binário), *Queue* (FIFO), *Stack* (LIFO).
* **Algoritmos**: Dijkstra (baseline) e A\* (informado, heurística admissível: distância em linha reta).
* **VRP (CVRP + VRPTW)** por heurística construtiva (Vizinho Mais Próximo + Inserção).
* **QA**: testes de correção.
* **Tkinter**: Biblioteca responsável pela interface gráfica.




