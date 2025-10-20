"""
Implementação do algoritmo A* para busca de caminho mínimo.
Utiliza heurística de Haversine para estimar distâncias geográficas.
"""

from typing import List, Dict, Tuple, Optional, Set
import networkx as nx
from datastructures import filaPrioridade, Pilha
import math

from dijkstra import find_path_dijkstra

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calcula a distância em linha reta entre dois pontos geográficos usando a fórmula de Haversine.
    
    Args:
        lat1, lon1: Coordenadas do primeiro ponto (latitude, longitude)
        lat2, lon2: Coordenadas do segundo ponto (latitude, longitude)
        
    Returns:
        Distância em quilômetros
    """
    R = 6371.0
    
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = (math.sin(dlat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))

    return (R * c) * 1000.0

def get_node_coordinates(graph: nx.DiGraph, node: int) -> Tuple[float, float]:
    """
    Extrai coordenadas geográficas de um nó do grafo.
    
    Args:
        graph: Grafo com atributos de coordenadas
        node: ID do nó
        
    Returns:
        Tuple (latitude, longitude)
    """
    node_data = graph.nodes[node]
    
    if 'y' in node_data and 'x' in node_data:
        return node_data['y'], node_data['x'] 
    elif 'lat' in node_data and 'lon' in node_data:
        return node_data['lat'], node_data['lon']
    elif 'latitude' in node_data and 'longitude' in node_data:
        return node_data['latitude'], node_data['longitude']
    else:
        return (0.0, 0.0)  

def calculate_heuristic(graph: nx.DiGraph, current: int, goal: int) -> float:
    """
    Calcula a heurística (distância em linha reta) entre dois nós.
    
    Args:
        graph: Grafo com coordenadas geográficas
        current: Nó atual
        goal: Nó objetivo
        
    Returns:
        Distância heurística em quilômetros
    """
    try:
        lat1, lon1 = get_node_coordinates(graph, current)
        lat2, lon2 = get_node_coordinates(graph, goal)
        return haversine_distance(lat1, lon1, lat2, lon2)
    except (KeyError, TypeError):
        return 0.0


def find_path_a_star(graph: nx.DiGraph,
                     start: int,
                     end: int) -> Tuple[List[int], float]:
    """
    Encontra o caminho mínimo entre dois nós usando o algoritmo A*.

    Args:
        graph: Grafo dirigido e ponderado com coordenadas geográficas
        start: Nó de origem
        end: Nó de destino

    Returns:
        Tuple contendo (caminho, distância_total)
        Se não houver caminho, retorna ([], float('inf'))
    """
    if start == end:
        return [start], 0.0

    if not graph.has_node(start) or not graph.has_node(end):
        return [], float('inf')

    g_score = {node: float('inf') for node in graph.nodes()}
    f_score = {node: float('inf') for node in graph.nodes()}
    predecessors = {node: None for node in graph.nodes()}
    visited = set()

    g_score[start] = 0.0
    f_score[start] = calculate_heuristic(graph, start, end)

    priority_queue = filaPrioridade()
    priority_queue.put(start, f_score[start])

    while not priority_queue.is_empty():
        current = priority_queue.get()

        if current in visited:
            continue

        visited.add(current)

        if current == end:
            break

        # --- INÍCIO DA CORREÇÃO ---
        # Iteramos sobre 'graph.adj' para um MultiDiGraph

        if current not in graph.adj:
            continue

        for neighbor, edges in graph.adj[current].items():
            if neighbor in visited:
                continue

            # 'edges' é um dicionário de todas as arestas (ex: {0: data, 1: data})
            # Vamos encontrar a aresta com o menor 'length'

            best_weight = float('inf')
            for edge_data in edges.values():
                weight = edge_data.get('length', edge_data.get('weight', float('inf')))
                if weight < best_weight:
                    best_weight = weight

            if best_weight == float('inf'):
                continue

            edge_weight = best_weight
            tentative_g_score = g_score[current] + edge_weight

            if tentative_g_score < g_score[neighbor]:
                predecessors[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + calculate_heuristic(graph, neighbor, end)
                priority_queue.put(neighbor, f_score[neighbor])
        # --- FIM DA CORREÇÃO ---

    if g_score[end] == float('inf'):
        return [], float('inf')

    path = reconstruct_path(predecessors, start, end)
    return path, g_score[end]

def reconstruct_path(predecessors: Dict[int, Optional[int]], 
                    start: int, 
                    end: int) -> List[int]:
    """
    Reconstrói o caminho usando uma pilha para inverter a ordem.
    (Reutiliza a função do Dijkstra para consistência)
    
    Args:
        predecessors: Dicionário de predecessores
        start: Nó de origem
        end: Nó de destino
        
    Returns:
        Lista de nós representando o caminho
    """
    if predecessors[end] is None and start != end:
        return []
    
    path_stack = Pilha()
    current = end
    
    while current is not None:
        path_stack.push(current)
        current = predecessors[current]
    
    path = []
    while not path_stack.is_empty():
        path.append(path_stack.pop())
    
    return path

def get_shortest_distance_a_star(graph: nx.DiGraph, 
                                start: int, 
                                end: int) -> float:
    """
    Retorna apenas a distância mínima entre dois nós usando A*.
    Mais eficiente quando não se precisa do caminho completo.
    
    Args:
        graph: Grafo dirigido e ponderado com coordenadas
        start: Nó de origem
        end: Nó de destino
        
    Returns:
        Distância mínima ou float('inf') se não houver caminho
    """
    path, distance = find_path_a_star(graph, start, end)
    return distance

def validate_graph_for_a_star(graph: nx.DiGraph) -> bool:
    """
    Valida se o grafo é adequado para o algoritmo A*.
    
    Args:
        graph: Grafo a ser validado
        
    Returns:
        True se o grafo é válido, False caso contrário
    """
    
    if not isinstance(graph, nx.DiGraph):
        return False
    
    for u, v, data in graph.edges(data=True):
        weight = data.get('length', data.get('weight', 1.0))
        if weight < 0:
            return False
    
    sample_nodes = list(graph.nodes())[:5] 
    for node in sample_nodes:
        try:
            get_node_coordinates(graph, node)
        except (KeyError, TypeError):
            pass
    
    return True

def compare_algorithms_performance(graph: nx.DiGraph, 
                                 start: int, 
                                 end: int) -> Dict[str, any]:
    """
    Compara o desempenho entre Dijkstra e A* para o mesmo problema.
    
    Args:
        graph: Grafo para teste
        start: Nó de origem
        end: Nó de destino
        
    Returns:
        Dicionário com métricas de comparação
    """
    import time
    
    start_time = time.perf_counter()
    dijkstra_path, dijkstra_distance = find_path_dijkstra(graph, start, end)
    dijkstra_time = time.perf_counter() - start_time
    
    start_time = time.perf_counter()
    astar_path, astar_distance = find_path_a_star(graph, start, end)
    astar_time = time.perf_counter() - start_time
    
    return {
        'dijkstra_time': dijkstra_time,
        'astar_time': astar_time,
        'dijkstra_distance': dijkstra_distance,
        'astar_distance': astar_distance,
        'dijkstra_path_length': len(dijkstra_path),
        'astar_path_length': len(astar_path),
        'time_improvement': (dijkstra_time - astar_time) / dijkstra_time if dijkstra_time > 0 else 0
    }
