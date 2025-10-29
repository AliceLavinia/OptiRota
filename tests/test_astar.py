"""
Testes unitários para o módulo A*.
"""

import unittest
import sys
import os
import networkx as nx

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from OptiRota.algorithms.a_star import (
    haversine_distance,
    get_node_coordinates,
    calculate_heuristic,
    find_path_a_star,
    get_shortest_distance_a_star,
    validate_graph_for_a_star,
    compare_algorithms_performance
)

class TestHaversineDistance(unittest.TestCase):
    """Testa cálculo de distância Haversine."""
    
    def test_haversine_distance_same_point(self):
        """Testa distância entre o mesmo ponto."""
        distance = haversine_distance(0.0, 0.0, 0.0, 0.0)
        self.assertEqual(distance, 0.0)
    
    def test_haversine_distance_known_distance(self):
        """Testa distância conhecida (São Paulo para Rio de Janeiro)."""
        distance = haversine_distance(-23.5505, -46.6333, -22.9068, -43.1729)
        self.assertAlmostEqual(distance, 358.0, delta=10.0)
    
    def test_haversine_distance_short_distance(self):
        """Testa distância curta (poucos metros)."""
        distance = haversine_distance(0.0, 0.0, 0.0001, 0.0001)
        self.assertGreater(distance, 0.0)
        self.assertLess(distance, 1.0)
    
    def test_haversine_distance_antipodes(self):
        """Testa distância entre pontos antípodas."""
        distance = haversine_distance(0.0, 0.0, 0.0, 180.0)
        self.assertAlmostEqual(distance, 20015.0, delta=100.0)  # ~metade da circunferência da Terra

class TestNodeCoordinates(unittest.TestCase):
    """Testa extração de coordenadas de nós."""
    
    def setUp(self):
        """Configuração inicial."""
        self.graph = nx.DiGraph()
        self.graph.add_node(0, y=-23.5505, x=-46.6333)  # Formato OSMnx
        self.graph.add_node(1, lat=-22.9068, lon=-43.1729)  # Formato alternativo
        self.graph.add_node(2, latitude=0.0, longitude=0.0)  # Formato alternativo
        self.graph.add_node(3) 
    
    def test_get_node_coordinates_osmnx_format(self):
        """Testa formato OSMnx (y, x)."""
        lat, lon = get_node_coordinates(self.graph, 0)
        self.assertAlmostEqual(lat, -23.5505, places=4)
        self.assertAlmostEqual(lon, -46.6333, places=4)
    
    def test_get_node_coordinates_lat_lon_format(self):
        """Testa formato lat/lon."""
        lat, lon = get_node_coordinates(self.graph, 1)
        self.assertAlmostEqual(lat, -22.9068, places=4)
        self.assertAlmostEqual(lon, -43.1729, places=4)
    
    def test_get_node_coordinates_latitude_longitude_format(self):
        """Testa formato latitude/longitude."""
        lat, lon = get_node_coordinates(self.graph, 2)
        self.assertEqual(lat, 0.0)
        self.assertEqual(lon, 0.0)
    
    def test_get_node_coordinates_no_coordinates(self):
        """Testa nó sem coordenadas."""
        lat, lon = get_node_coordinates(self.graph, 3)
        self.assertEqual(lat, 0.0)
        self.assertEqual(lon, 0.0)

class TestAStarAlgorithm(unittest.TestCase):
    """Testa o algoritmo A*."""
    
    def setUp(self):
        """Configuração inicial."""
        # Cria grafo com coordenadas geográficas
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from([
            (0, {'y': -23.5505, 'x': -46.6333}),  # São Paulo
            (1, {'y': -23.5613, 'x': -46.6565}),  # Próximo a SP
            (2, {'y': -23.5489, 'x': -46.6388}),  # Próximo a SP
            (3, {'y': -23.5329, 'x': -46.6399}),  # Próximo a SP
            (4, {'y': -23.5632, 'x': -46.6535})   # Próximo a SP
        ])
        
        # Adiciona arestas com pesos baseados em distância real
        self.graph.add_edges_from([
            (0, 1, {'length': 2.5}),
            (0, 2, {'length': 1.8}),
            (1, 3, {'length': 3.2}),
            (2, 4, {'length': 2.1}),
            (3, 4, {'length': 1.5}),
            (1, 2, {'length': 0.8})
        ])
    
    def test_find_path_a_star_same_node(self):
        """Testa caminho quando origem e destino são iguais."""
        path, distance = find_path_a_star(self.graph, 0, 0)
        self.assertEqual(path, [0])
        self.assertEqual(distance, 0.0)
    
    def test_find_path_a_star_direct_connection(self):
        """Testa caminho direto entre dois nós."""
        path, distance = find_path_a_star(self.graph, 0, 1)
        self.assertEqual(path, [0, 1])
        self.assertEqual(distance, 2.5)
    
    def test_find_path_a_star_multi_hop(self):
        """Testa caminho com múltiplos saltos."""
        path, distance = find_path_a_star(self.graph, 0, 4)
        # Deve encontrar um caminho válido
        self.assertNotEqual(path, [])
        self.assertNotEqual(distance, float('inf'))
        self.assertEqual(path[0], 0)
        self.assertEqual(path[-1], 4)
    
    def test_find_path_a_star_no_path(self):
        """Testa quando não há caminho."""
        self.graph.add_node(5, y=0.0, x=0.0)
        path, distance = find_path_a_star(self.graph, 0, 5)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
    
    def test_calculate_heuristic(self):
        """Testa cálculo de heurística."""
        heuristic = calculate_heuristic(self.graph, 0, 4)
        self.assertGreater(heuristic, 0.0)
        self.assertIsInstance(heuristic, float)
    
    def test_calculate_heuristic_same_node(self):
        """Testa heurística para o mesmo nó."""
        heuristic = calculate_heuristic(self.graph, 0, 0)
        self.assertEqual(heuristic, 0.0)
    
    def test_get_shortest_distance_a_star(self):
        """Testa obtenção apenas da distância."""
        distance = get_shortest_distance_a_star(self.graph, 0, 4)
        self.assertNotEqual(distance, float('inf'))
        self.assertGreater(distance, 0.0)
    
    def test_validate_graph_for_a_star_valid(self):
        """Testa validação de grafo válido."""
        self.assertTrue(validate_graph_for_a_star(self.graph))
    
    def test_validate_graph_for_a_star_invalid_type(self):
        """Testa validação com tipo de grafo incorreto."""
        undirected_graph = nx.Graph()
        self.assertFalse(validate_graph_for_a_star(undirected_graph))
    
    def test_validate_graph_for_a_star_negative_weights(self):
        """Testa validação com pesos negativos."""
        invalid_graph = nx.DiGraph()
        invalid_graph.add_nodes_from([0, 1], y=0.0, x=0.0)
        invalid_graph.add_edge(0, 1, length=-1.0)
        self.assertFalse(validate_graph_for_a_star(invalid_graph))
    
    def test_edge_weight_fallback(self):
        """Testa fallback para atributo 'weight' quando 'length' não existe."""
        graph_no_length = nx.DiGraph()
        graph_no_length.add_nodes_from([
            (0, {'y': 0.0, 'x': 0.0}),
            (1, {'y': 0.001, 'x': 0.001})
        ])
        graph_no_length.add_edge(0, 1, weight=5.0)
        
        path, distance = find_path_a_star(graph_no_length, 0, 1)
        self.assertEqual(path, [0, 1])
        self.assertEqual(distance, 5.0)

class TestAStarPerformance(unittest.TestCase):
    """Testa performance do algoritmo A*."""
    
    def test_compare_algorithms_performance(self):
        """Testa comparação de performance entre Dijkstra e A*."""
        # Cria grafo de teste
        graph = nx.DiGraph()
        size = 5
        
        # Adiciona nós com coordenadas
        for i in range(size):
            for j in range(size):
                node_id = i * size + j
                graph.add_node(node_id, y=i * 0.01, x=j * 0.01)
        
        # Adiciona arestas
        for i in range(size):
            for j in range(size):
                current = i * size + j
                
                if j < size - 1:
                    right = i * size + (j + 1)
                    graph.add_edge(current, right, length=1.0)
                
                if i < size - 1:
                    down = (i + 1) * size + j
                    graph.add_edge(current, down, length=1.0)
        
        # Testa comparação
        start = 0
        end = size * size - 1
        
        comparison = compare_algorithms_performance(graph, start, end)
        
        # Verifica que as métricas estão presentes
        self.assertIn('dijkstra_time', comparison)
        self.assertIn('astar_time', comparison)
        self.assertIn('dijkstra_distance', comparison)
        self.assertIn('astar_distance', comparison)
        
        # Verifica que as distâncias são iguais (ambos encontram o caminho ótimo)
        self.assertAlmostEqual(comparison['dijkstra_distance'], 
                              comparison['astar_distance'], 
                              places=1)
        
        print(f"Performance comparison: Dijkstra={comparison['dijkstra_time']:.4f}s, "
              f"A*={comparison['astar_time']:.4f}s")

class TestAStarEdgeCases(unittest.TestCase):
    """Testa casos extremos do algoritmo A*."""
    
    def test_empty_graph(self):
        """Testa comportamento com grafo vazio."""
        empty_graph = nx.DiGraph()
        path, distance = find_path_a_star(empty_graph, 0, 1)
        self.assertEqual(path, [])
        self.assertEqual(distance, float('inf'))
    
    def test_single_node_graph(self):
        """Testa grafo com um único nó."""
        single_node_graph = nx.DiGraph()
        single_node_graph.add_node(0, y=0.0, x=0.0)
        
        path, distance = find_path_a_star(single_node_graph, 0, 0)
        self.assertEqual(path, [0])
        self.assertEqual(distance, 0.0)
    
    def test_graph_without_coordinates(self):
        """Testa grafo sem coordenadas (A* vira Dijkstra)."""
        graph_no_coords = nx.DiGraph()
        graph_no_coords.add_nodes_from([0, 1, 2])
        graph_no_coords.add_edges_from([
            (0, 1, {'length': 5.0}),
            (1, 2, {'length': 3.0})
        ])
        
        path, distance = find_path_a_star(graph_no_coords, 0, 2)
        self.assertEqual(path, [0, 1, 2])
        self.assertEqual(distance, 8.0)

if __name__ == '__main__':
    unittest.main()
