import osmnx as ox

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
    print("Grafo construído com sucesso.")
    return self.graph
  
  def get_graph(self):
    if self.graph is None:
      raise ValueError("Grafo não construído. Chame build_graph() primeiro.")
    return self.graph
  
  def get_closest_node(self, lat, long):
    """Encontra o nó mais próximo em um par de coordenadas (latitude, longitude)."""
    return ox.distance.nearest_nodes(self.graph, long, lat)
  