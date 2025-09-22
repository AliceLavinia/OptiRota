import time
import random
import pandas as pd
from graph_parser import GraphParser
from dijkstra import find_path_dijkstra
from a_star import find_path_a_star

# Lista de locais para testar, do menor para o maior
LOCATIONS_TO_BENCHMARK = {
    "Ponta Verde, Maceió": 50, # Grafo pequeno, 50 rotas aleatórias
    "Jatiúca, Maceió": 100,      # Grafo médio, 100 rotas aleatórias
    "Maceió, Alagoas": 150       # Grafo grande, 150 rotas aleatórias
}

def run_benchmark():
    # Executa o benchmark de desempenho para os algoritmos de busca de caminho.
    results = []

    print("--- INICIANDO BENCHMARK DE DESEMPENHO ---")

    for location, num_samples in LOCATIONS_TO_BENCHMARK.items():
        print(f"\n[+] Processando Local: {location}")
        
        # Construir o grafo
        parser = GraphParser(location)
        graph = parser.build_graph()
        nodes = list(graph.nodes)
        
        stats = parser.get_graph_stats()
        num_nodes = stats['num_nodes']
        num_edges = stats['num_edges']

        print(f"Grafo construído com {num_nodes} nós e {num_edges} arestas.")

        # Executar testes para Dijkstra
        total_time_dijkstra = 0
        for i in range(num_samples):
            # Seleciona dois nós aleatórios para a rota
            start_node, end_node = random.sample(nodes, 2)
            
            start_time = time.perf_counter()
            find_path_dijkstra(graph, start_node, end_node)
            end_time = time.perf_counter()
            
            total_time_dijkstra += (end_time - start_time)
        
        avg_time_dijkstra = (total_time_dijkstra / num_samples) * 1000

        # Executar testes para A*
        total_time_astar = 0
        for i in range(num_samples):
            start_node, end_node = random.sample(nodes, 2)
            
            start_time = time.perf_counter()
            find_path_a_star(graph, start_node, end_node)
            end_time = time.perf_counter()
            
            total_time_astar += (end_time - start_time)

        avg_time_astar = (total_time_astar / num_samples) * 1000
        
        # Salvar resultados
        results.append({
            "Local": location,
            "Nós": num_nodes,
            "Arestas": num_edges,
            "Tempo Médio Dijkstra (ms)": avg_time_dijkstra,
            "Tempo Médio A* (ms)": avg_time_astar
        })

    # Exibir tabela de resultados
    df_results = pd.DataFrame(results)
    print("\n\n--- RESULTADOS DO BENCHMARK ---")
    print(df_results.to_string(index=False))
    
    # Salvar em um arquivo CSV para o relatório
    df_results.to_csv("benchmark_results.csv", index=False)
    print("\nResultados salvos em 'benchmark_results.csv'")


if __name__ == "__main__":
    run_benchmark()