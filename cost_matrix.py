"""
Módulo para computação de matrizes de custo usando algoritmos de caminho mínimo.
Utiliza A* para eficiência na construção de matrizes de distância entre múltiplos nós.
"""

from typing import List, Dict
import networkx as nx
import numpy as np
from a_star import find_path_a_star, get_shortest_distance_a_star
from dijkstra import find_path_dijkstra, get_shortest_distance

def compute_cost_matrix(graph: nx.DiGraph, 
                       nodes: List[int], 
                       algorithm: str = 'a_star',
                       use_paths: bool = False) -> Dict:
    """
    Computa uma matriz de custo entre múltiplos nós do grafo.
    
    Args:
        graph: Grafo dirigido e ponderado
        nodes: Lista de nós para incluir na matriz
        algorithm: 'a_star' ou 'dijkstra' para escolher o algoritmo
        use_paths: Se True, também retorna os caminhos completos
        
    Returns:
        Dicionário com:
        - 'matrix': Matriz numpy de distâncias
        - 'node_index': Mapeamento de nó para índice na matriz
        - 'paths': (opcional) Dicionário de caminhos completos
    """
    if not nodes:
        return {'matrix': np.array([]), 'node_index': {}, 'paths': {}}
    
    unique_nodes = list(dict.fromkeys(nodes))
    n = len(unique_nodes)
    
    node_index = {node: i for i, node in enumerate(unique_nodes)}
    
    cost_matrix = np.full((n, n), np.inf)
    np.fill_diagonal(cost_matrix, 0.0) 
    
    paths = {}
    
    if algorithm.lower() == 'a_star':
        search_func = find_path_a_star if use_paths else get_shortest_distance_a_star
    elif algorithm.lower() == 'dijkstra':
        search_func = find_path_dijkstra if use_paths else get_shortest_distance
    else:
        raise ValueError(f"Algoritmo '{algorithm}' não suportado. Use 'a_star' ou 'dijkstra'")
    
    print(f"Computando matriz de custo {n}x{n} usando {algorithm.upper()}...")
    
    for i, source in enumerate(unique_nodes):
        for j, target in enumerate(unique_nodes):
            if i == j:
                continue
                
            try:
                if use_paths:
                    path, distance = search_func(graph, source, target)
                    if path:  
                        cost_matrix[i, j] = distance
                        paths[(source, target)] = path
                else:
                    distance = search_func(graph, source, target)
                    if distance != float('inf'):
                        cost_matrix[i, j] = distance
                        
            except Exception as e:
                print(f"Aviso: Erro ao calcular distância de {source} para {target}: {e}")
                continue
    
    result = {
        'matrix': cost_matrix,
        'node_index': node_index,
        'nodes': unique_nodes
    }
    
    if use_paths:
        result['paths'] = paths
    
    return result

def compute_cost_matrix_symmetric(graph: nx.DiGraph, 
                                 nodes: List[int], 
                                 algorithm: str = 'a_star') -> Dict:
    """
    Computa uma matriz de custo simétrica (assume que distância A->B = B->A).
    Mais eficiente que a versão completa, mas pode não ser precisa para grafos dirigidos.
    
    Args:
        graph: Grafo dirigido e ponderado
        nodes: Lista de nós para incluir na matriz
        algorithm: 'a_star' ou 'dijkstra'
        
    Returns:
        Dicionário com matriz simétrica e mapeamentos
    """
    if not nodes:
        return {'matrix': np.array([]), 'node_index': {}, 'nodes': []}
    
    unique_nodes = list(dict.fromkeys(nodes))
    n = len(unique_nodes)
    node_index = {node: i for i, node in enumerate(unique_nodes)}
    
    cost_matrix = np.full((n, n), np.inf)
    np.fill_diagonal(cost_matrix, 0.0)
    
    if algorithm.lower() == 'a_star':
        search_func = get_shortest_distance_a_star
    elif algorithm.lower() == 'dijkstra':
        search_func = get_shortest_distance
    else:
        raise ValueError(f"Algoritmo '{algorithm}' não suportado")
    
    print(f"Computando matriz simétrica {n}x{n} usando {algorithm.upper()}...")
    
    for i in range(n):
        for j in range(i + 1, n):
            source = unique_nodes[i]
            target = unique_nodes[j]
            
            try:
                distance = search_func(graph, source, target)
                if distance != float('inf'):
                    cost_matrix[i, j] = distance
                    cost_matrix[j, i] = distance
                    
            except Exception as e:
                print(f"Aviso: Erro ao calcular distância de {source} para {target}: {e}")
                continue
    
    return {
        'matrix': cost_matrix,
        'node_index': node_index,
        'nodes': unique_nodes
    }

def get_cost_between_nodes(cost_matrix: np.ndarray, 
                          node_index: Dict[int, int],
                          source: int, 
                          target: int) -> float:
    """
    Obtém o custo entre dois nós usando a matriz pré-computada.
    
    Args:
        cost_matrix: Matriz de custo
        node_index: Mapeamento de nó para índice
        source: Nó de origem
        target: Nó de destino
        
    Returns:
        Custo entre os nós ou float('inf') se não houver caminho
    """
    if source not in node_index or target not in node_index:
        return float('inf')
    
    i = node_index[source]
    j = node_index[target]
    
    return cost_matrix[i, j]

def validate_cost_matrix(cost_matrix: np.ndarray, 
                        node_index: Dict[int, int]) -> bool:
    """
    Valida se a matriz de custo está bem formada.
    
    Args:
        cost_matrix: Matriz de custo
        node_index: Mapeamento de nó para índice
        
    Returns:
        True se a matriz é válida, False caso contrário
    """
    if cost_matrix is None or len(cost_matrix) == 0:
        return False
    
    n = len(cost_matrix)
    
    if cost_matrix.shape != (n, n):
        return False
    
    if not np.allclose(np.diag(cost_matrix), 0.0):
        return False
    
    if np.any(cost_matrix < 0):
        return False
    
    if len(node_index) != n:
        return False
    
    return True

def print_cost_matrix(cost_matrix: np.ndarray, 
                     node_index: Dict[int, int],
                     precision: int = 2) -> None:
    """
    Imprime a matriz de custo de forma legível.
    
    Args:
        cost_matrix: Matriz de custo
        node_index: Mapeamento de nó para índice
        precision: Número de casas decimais
    """
    if cost_matrix is None or len(cost_matrix) == 0:
        print("Matriz de custo vazia")
        return
    
    n = len(cost_matrix)
    nodes = [node for node, _ in sorted(node_index.items(), key=lambda x: x[1])]
    
    print("Matriz de Custo:")
    print("     ", end="")
    for node in nodes:
        print(f"{node:8}", end="")
    print()
    
    for i, source in enumerate(nodes):
        print(f"{source:4}: ", end="")
        for j, target in enumerate(nodes):
            if cost_matrix[i, j] == float('inf'):
                print("     inf", end="")
            else:
                print(f"{cost_matrix[i, j]:8.{precision}f}", end="")
        print()

def export_cost_matrix(cost_matrix: np.ndarray, 
                      node_index: Dict[int, int],
                      filename: str) -> None:
    """
    Exporta a matriz de custo para um arquivo CSV.
    
    Args:
        cost_matrix: Matriz de custo
        node_index: Mapeamento de nó para índice
        filename: Nome do arquivo de saída
    """
    import pandas as pd
    
    if cost_matrix is None or len(cost_matrix) == 0:
        print("Matriz de custo vazia, não é possível exportar")
        return
    
    nodes = [node for node, _ in sorted(node_index.items(), key=lambda x: x[1])]
    
    df = pd.DataFrame(cost_matrix, index=nodes, columns=nodes)
    
    df = df.replace([np.inf, -np.inf], '')
    
    df.to_csv(filename)
    print(f"Matriz de custo exportada para '{filename}'")
