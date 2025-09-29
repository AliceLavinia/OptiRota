#!/usr/bin/env python3
"""
Testes unitários para o módulo Dijkstra.
"""

import unittest
import sys
import os
import networkx as nx
import numpy as np

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dijkstra import (
    find_path_dijkstra, 
    reconstruct_path, 
    get_shortest_distance,
    get_all_shortest_distances,
    validate_graph_for_dijkstra
)

class TestDijkstra(unittest.TestCase):
    """Testa as funções do módulo Dijkstra."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        # Cria grafo de teste simples
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from([0, 1, 2, 3, 4])
        self.graph.add_edges_from([
            (0, 1, {'length': 10.0}),
            (0, 2, {'length': 15.0}),
            (1, 3, {'length': 8.0}),
            (2, 4, {'length': 12.0}),
            (3, 4, {'length': 5.0}),
            (1, 2, {'length': 3.0})
        ])
        
        # Grafo com pesos negativos (inválido para Dijkstra)
        self.invalid_graph = nx.DiGraph()
        self.invalid_graph.add_nodes_from([0, 1, 2])
        self.invalid_graph.add_edges_from([
            (0, 1, {'length': 10.0}),
            (1, 2, {'length': -5.0})  # Peso negativo
        ])
    
    def test_find_path_dijkstra_same_node(self):
        """Testa caminho quando origem e destino são iguais."""
        path, distance = find_path_dijkstra(self.graph, 0, 0)
        self.assertEqual(path, [0])
        self.assertEqual(distance, 0.0)
    
    def test_find_path_dijkstra_direct_connection(self):
        """Testa caminho direto entre dois nós."""
        path, distance = find_path_dijkstra(self.graph, 0, 1)
        self.assertEqual(path, [0, 1])
        self.assertEqual(distance, 10.0)
    
    def test_find_path_dijkstra_multi_hop(self):
        """Testa caminho com múltiplos saltos."""
        path, distance = find_path_dijkstra(self.graph, 0, 4)
        # Caminho ótimo: 0 -> 1 -> 2 -> 4 (custo: 10 + 3 + 12 = 25)
        # ou 0 -> 1 -> 3 -> 4 (custo: 10 + 8 + 5 = 23)
        self.assertIn(path, [[0, 1, 2, 4], [0, 1, 3, 4]])
        self.assertAlmostEqual(distance, 23.0, places=1)  # Menor custo
    
    def test_find_path_dijkstra_no_path(self):
        """Testa quando não há caminho entre os nós."""
        # Adiciona nó isolado
        self.graph.add_node(5)
        path, distance = find_path_dijkstra(self.graph, 0, 5)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
    
    def test_find_path_dijkstra_invalid_nodes(self):
        """Testa com nós que não existem no grafo."""
        path, distance = find_path_dijkstra(self.graph, 0, 999)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
        
        path, distance = find_path_dijkstra(self.graph, 999, 0)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
    
    def test_reconstruct_path(self):
        """Testa reconstrução de caminho."""
        predecessors = {0: None, 1: 0, 2: 1, 3: 1, 4: 3}
        path = reconstruct_path(predecessors, 0, 4)
        self.assertEqual(path, [0, 1, 3, 4])
    
    def test_reconstruct_path_no_path(self):
        """Testa reconstrução quando não há caminho."""
        predecessors = {0: None, 1: 0, 2: None, 3: 1, 4: 3}
        path = reconstruct_path(predecessors, 0, 2)
        self.assertEqual(path, [])
    
    def test_get_shortest_distance(self):
        """Testa obtenção apenas da distância."""
        distance = get_shortest_distance(self.graph, 0, 4)
        self.assertAlmostEqual(distance, 23.0, places=1)
    
    def test_get_all_shortest_distances(self):
        """Testa cálculo de distâncias para todos os nós."""
        distances = get_all_shortest_distances(self.graph, 0)
        
        self.assertEqual(distances[0], 0.0)
        self.assertEqual(distances[1], 10.0)
        self.assertAlmostEqual(distances[2], 13.0, places=1)  # 0->1->2
        self.assertEqual(distances[3], 18.0)  # 0->1->3
        self.assertAlmostEqual(distances[4], 23.0, places=1)  # 0->1->3->4
    
    def test_validate_graph_for_dijkstra_valid(self):
        """Testa validação de grafo válido."""
        self.assertTrue(validate_graph_for_dijkstra(self.graph))
    
    def test_validate_graph_for_dijkstra_invalid(self):
        """Testa validação de grafo inválido."""
        self.assertFalse(validate_graph_for_dijkstra(self.invalid_graph))
    
    def test_validate_graph_for_dijkstra_wrong_type(self):
        """Testa validação com tipo de grafo incorreto."""
        undirected_graph = nx.Graph()
        self.assertFalse(validate_graph_for_dijkstra(undirected_graph))
    
    def test_edge_weight_fallback(self):
        """Testa fallback para atributo 'weight' quando 'length' não existe."""
        graph_no_length = nx.DiGraph()
        graph_no_length.add_nodes_from([0, 1, 2])
        graph_no_length.add_edges_from([
            (0, 1, {'weight': 5.0}),
            (1, 2, {'weight': 3.0})
        ])
        
        path, distance = find_path_dijkstra(graph_no_length, 0, 2)
        self.assertEqual(path, [0, 1, 2])
        self.assertEqual(distance, 8.0)
    
    def test_empty_graph(self):
        """Testa comportamento com grafo vazio."""
        empty_graph = nx.DiGraph()
        path, distance = find_path_dijkstra(empty_graph, 0, 1)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))

class TestDijkstraPerformance(unittest.TestCase):
    """Testa performance do algoritmo Dijkstra."""
    
    def test_large_graph_performance(self):
        """Testa performance com grafo maior."""
        # Cria grafo em grade 10x10
        graph = nx.DiGraph()
        size = 10
        
        # Adiciona nós
        for i in range(size):
            for j in range(size):
                node_id = i * size + j
                graph.add_node(node_id)
        
        # Adiciona arestas (conecta nós adjacentes)
        for i in range(size):
            for j in range(size):
                current = i * size + j
                
                # Conecta com vizinho da direita
                if j < size - 1:
                    right = i * size + (j + 1)
                    graph.add_edge(current, right, length=1.0)
                
                # Conecta com vizinho de baixo
                if i < size - 1:
                    down = (i + 1) * size + j
                    graph.add_edge(current, down, length=1.0)
        
        # Testa caminho de canto superior esquerdo para canto inferior direito
        start = 0
        end = size * size - 1
        
        import time
        start_time = time.perf_counter()
        path, distance = find_path_dijkstra(graph, start, end)
        end_time = time.perf_counter()
        
        # Verifica que encontrou caminho
        self.assertNotEqual(path, [])
        self.assertNotEqual(distance, float('inf'))
        
        # Verifica que o caminho é válido
        self.assertEqual(path[0], start)
        self.assertEqual(path[-1], end)
        
        # Verifica que o tempo de execução é razoável (< 1 segundo)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 1.0)
        
        print(f"Performance test: {execution_time:.4f}s para grafo {size}x{size}")

if __name__ == '__main__':
    unittest.main()
