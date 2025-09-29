import osmnx as ox
import networkx as nx
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

class GraphParser:
  """Responsável por adquirir os dados do OSM e construir um grafo navegável.
  """

  def __init__(self, location_query: str):
    self.location_query = location_query
    self.graph = None
    print(f"Parser do Grafo inicializado para '{location_query}'")

  def build_graph(self):
    """Baixa os dados do OSM e os converte em um grafo ponderado e direcionado."""
    print(f"Baixando dados do OSM para '{self.location_query}'...")
    self.graph = ox.graph_from_place(self.location_query, network_type='drive')
    
    self._add_edge_weights()
    print("Grafo construído com sucesso.")
    return self.graph
  
  def _add_edge_weights(self):
    """Adiciona pesos às arestas baseados na distância e tempo de viagem."""
    if self.graph is None:
      return
    
    if 'length' not in self.graph.edges():
      self.graph = ox.add_edge_lengths(self.graph)
    
    for u, v, data in self.graph.edges(data=True):
      if 'length' in data:
        data['weight'] = data['length']
      else:
        data['weight'] = 1.0  # peso padrão
  
  def get_graph(self):
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    return self.graph
  
  def get_closest_node(self, lat: float, long: float) -> int:
    """Encontra o nó mais próximo em um par de coordenadas (latitude, longitude)."""
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    return ox.distance.nearest_nodes(self.graph, long, lat)
  
  def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
    """Retorna as coordenadas (lat, lon) de um nó."""
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    
    node_data = self.graph.nodes[node_id]
    return node_data['y'], node_data['x']  # lat, lon
  
  def get_edge_weight(self, u: int, v: int) -> float:
    """Retorna o peso de uma aresta entre dois nós."""
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    
    if self.graph.has_edge(u, v):
      return self.graph[u][v][0].get('weight', 1.0)
    return float('inf')
  
  def get_neighbors(self, node_id: int) -> List[int]:
    """Retorna os vizinhos de um nó."""
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    
    return list(self.graph.neighbors(node_id))
  
  def validate_graph(self) -> bool:
    """Valida se o grafo está bem formado para algoritmos de roteamento."""
    if self.graph is None:
      return False
    
    if not nx.is_weakly_connected(self.graph):
      print("Aviso: O grafo não é fracamente conectado")
      return False
    
    for u, v, data in self.graph.edges(data=True):
      if 'weight' not in data or data['weight'] <= 0:
        print(f"Aviso: Aresta ({u}, {v}) não tem peso válido")
        return False
    
    print("Grafo validado com sucesso")
    return True
  
  def get_graph_stats(self) -> Dict[str, Any]:
    """Retorna estatísticas do grafo."""
    if self.graph is None:
      return {}
    
    return {
      'num_nodes': self.graph.number_of_nodes(),
      'num_edges': self.graph.number_of_edges(),
      'is_connected': nx.is_weakly_connected(self.graph),
      'density': nx.density(self.graph)
    }
  