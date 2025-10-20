"""
Implementação do algoritmo de Dijkstra para busca de caminho mínimo.
Utiliza heap (fila de prioridade) para eficiência O((V + E) log V).
"""

from typing import List, Dict, Tuple, Optional, Set
import networkx as nx
from datastructures import filaPrioridade, Pilha


def find_path_dijkstra(graph: nx.DiGraph,
                       start: int,
                       end: int) -> Tuple[List[int], float]:
    """
    Encontra o caminho mínimo entre dois nós usando o algoritmo de Dijkstra.
    """
    if start == end:
        return [start], 0.0

    if not graph.has_node(start) or not graph.has_node(end):
        return [], float('inf')

    distances = {node: float('inf') for node in graph.nodes()}
    predecessors = {node: None for node in graph.nodes()}
    visited = set()

    distances[start] = 0.0
    priority_queue = filaPrioridade()
    priority_queue.put(start, 0.0)

    while not priority_queue.is_empty():
        current = priority_queue.get()

        if current in visited:
            continue

        visited.add(current)

        if current == end:
            break

        if current not in graph.adj:
            continue

        # --- INÍCIO DA CORREÇÃO ---
        # Verifica se o grafo é um MultiGraph (do osmnx) ou um DiGraph (dos testes)

        if graph.is_multigraph():
            # Lógica para MultiDiGraph (usado pelo app)
            for neighbor, edges in graph.adj[current].items():
                if neighbor in visited:
                    continue

                # Encontra a aresta com menor 'length' entre os dois nós
                best_weight = float('inf')
                for edge_data in edges.values():
                    weight = edge_data.get('length', edge_data.get('weight', float('inf')))
                    if weight < best_weight:
                        best_weight = weight

                if best_weight == float('inf'):
                    continue

                edge_weight = best_weight
                new_distance = distances[current] + edge_weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current
                    priority_queue.put(neighbor, new_distance)
        else:
            # Lógica para DiGraph simples (usado pelos testes unitários)
            for neighbor, edge_data in graph.adj[current].items():
                if neighbor in visited:
                    continue

                edge_weight = edge_data.get('length', edge_data.get('weight', 1.0))
                if edge_weight == float('inf'):
                    continue

                new_distance = distances[current] + edge_weight

                if new_distance < distances[neighbor]:
                    distances[neighbor] = new_distance
                    predecessors[neighbor] = current
                    priority_queue.put(neighbor, new_distance)
        # --- FIM DA CORREÇÃO ---

    if distances[end] == float('inf'):
        return [], float('inf')

    path = reconstruct_path(predecessors, start, end)
    return path, distances[end]

def reconstruct_path(predecessors: Dict[int, Optional[int]], 
                    start: int, 
                    end: int) -> List[int]:
    """
    Reconstrói o caminho usando uma pilha para inverter a ordem.
    
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

def get_shortest_distance(graph: nx.DiGraph, 
                         start: int, 
                         end: int) -> float:
    """
    Retorna apenas a distância mínima entre dois nós.
    Mais eficiente quando não se precisa do caminho completo.
    
    Args:
        graph: Grafo dirigido e ponderado
        start: Nó de origem
        end: Nó de destino
        
    Returns:
        Distância mínima ou float('inf') se não houver caminho
    """
    path, distance = find_path_dijkstra(graph, start, end)
    return distance

def get_all_shortest_distances(graph: nx.DiGraph, 
                              start: int) -> Dict[int, float]:
    """
    Calcula distâncias mínimas de um nó para todos os outros.
    Útil para construção de matrizes de custo.
    
    Args:
        graph: Grafo dirigido e ponderado
        start: Nó de origem
        
    Returns:
        Dicionário {nó: distância_mínima}
    """
    if not graph.has_node(start):
        return {}
    
    distances = {node: float('inf') for node in graph.nodes()}
    visited = set()
    
    distances[start] = 0.0
    priority_queue = filaPrioridade()
    priority_queue.put(start, 0.0)
    
    while not priority_queue.is_empty():
        current = priority_queue.get()
        
        if current in visited:
            continue
            
        visited.add(current)
        
        for neighbor in graph.neighbors(current):
            if neighbor in visited:
                continue
                
            edge_data = graph.get_edge_data(current, neighbor)
            if not edge_data:
                continue
                
            edge_weight = edge_data.get('length', edge_data.get('weight', 1.0))
            new_distance = distances[current] + edge_weight
            
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                priority_queue.put(neighbor, new_distance)
    
    return distances

def validate_graph_for_dijkstra(graph: nx.DiGraph) -> bool:
    """
    Valida se o grafo é adequado para o algoritmo de Dijkstra.
    
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
    
    return True
