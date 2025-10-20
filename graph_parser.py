import osmnx as ox
import networkx as nx
from typing import Dict, List, Tuple, Any


class GraphParser:
    """
    Responsável por adquirir dados do OpenStreetMap (OSM), processá-los e
    construir um grafo navegável e otimizado para algoritmos de roteamento.
    """

    def __init__(self, location_query: str):
        # Inicializa o parser com uma localização geográfica.
        self.location_query = location_query
        self.graph = None
        print(f"Parser do Grafo inicializado para '{location_query}'")

    def build_graph(self) -> nx.MultiDiGraph:
        # Orquestra o processo completo de construção e refino do grafo.
        print(f"Iniciando construção do grafo para '{self.location_query}'...")

        # Baixar o grafo da rua usando OSMnx
        initial_graph = ox.graph_from_place(self.location_query, network_type='drive')
        print(
            f"Grafo inicial baixado com {initial_graph.number_of_nodes()} nós e {initial_graph.number_of_edges()} arestas.")

        # Isso garante que o grafo é totalmente navegável de qualquer ponto a outro.
        largest_component = max(nx.weakly_connected_components(initial_graph), key=len)
        self.graph = initial_graph.subgraph(largest_component).copy()
        print(f"Grafo refinado para {self.graph.number_of_nodes()} nós e {self.graph.number_of_edges()} arestas.")

        # OSMnx estima a velocidade com base no tipo de via (highway tag).
        self.graph = ox.add_edge_speeds(self.graph)
        # Calcula o tempo de viagem (em segundos) usando a distância e a velocidade.
        self.graph = ox.add_edge_travel_times(self.graph)

        print("Métricas de distância ('length') e tempo ('travel_time') adicionadas.")

        self.validate_graph()
        return self.graph

    # --- Métodos de Consulta e Utilitários ---

    def get_graph(self) -> nx.MultiDiGraph:
        """Retorna o objeto do grafo construído."""
        if self.graph is None:
            raise ValueError("Grafo não construído. Chame o método build_graph() primeiro.")
        return self.graph

    # --- INÍCIO DA CORREÇÃO ---
    def get_closest_node(self, lat: float, lon: float) -> int:
        # Encontra o nó do grafo mais próximo de um par de coordenadas geográficas.
        if self.graph is None:
            raise ValueError("Grafo não construído.")

        # 1. Usa 'nearest_nodes' (plural), que é a função correta da API.
        node_or_array = ox.distance.nearest_nodes(self.graph, X=lon, Y=lat)

        # 2. Verifica se o resultado já é um 'int' (comportamento de versões novas)
        if isinstance(node_or_array, int):
            # Isso corrige o erro "'int' object is not subscriptable"
            return node_or_array

        # 3. Se não for 'int', trata como array (comportamento de versões antigas)
        try:
            # Extrai o primeiro elemento como 'int'.
            # Isso corrige o erro "The truth value of an array..."
            return int(node_or_array[0])
        except (TypeError, IndexError):
            # Se falhar, algo está muito errado.
            raise ValueError(f"Não foi possível extrair o ID do nó do resultado: {node_or_array}")

    # --- FIM DA CORREÇÃO ---

    def get_node_attributes(self, node_id: int) -> Dict[str, Any]:
        # Retorna um dicionário com todos os atributos de um nó específico.
        if self.graph is None or node_id not in self.graph.nodes:
            raise ValueError(f"Nó {node_id} não encontrado no grafo.")
        return self.graph.nodes[node_id]

    def get_edge_attributes(self, u_node: int, v_node: int) -> Dict[str, Any]:
        # Retorna os atributos da aresta que conecta dois nós.
        if self.graph is None or not self.graph.has_edge(u_node, v_node):
            raise ValueError(f"Aresta entre {u_node} e {v_node} não encontrada.")
        # O [0] acessa a primeira aresta, pois OSMnx pode criar multigrafos (múltiplas arestas entre 2 nós).
        return self.graph.get_edge_data(u_node, v_node)[0]

    def get_path_total_attribute(self, path: List[int], attribute: str) -> float:
        # Calcula a soma de um atributo específico ao longo de um caminho.
        if self.graph is None:
            raise ValueError("Grafo não construído.")
        return sum(ox.utils_graph.get_route_edge_attributes(self.graph, path, attribute))

    # --- Métodos de Validação e Estatísticas ---

    def validate_graph(self) -> bool:
        # Verifica se o grafo está bem-formado e pronto para os algoritmos de roteamento.
        if self.graph is None:
            print("Erro de validação: Grafo é nulo.")
            return False

        if not nx.is_weakly_connected(self.graph):
            print("Aviso de validação: O grafo não é conectado.")
            # Não retornamos False aqui, pois o refino já deve ter tratado isso.

        for u, v, data in self.graph.edges(data=True):
            if 'length' not in data or 'travel_time' not in data or data['length'] <= 0 or data['travel_time'] < 0:
                print(f"Aviso de validação: Aresta ({u}, {v}) não possui atributos de peso/tempo válidos.")
                return False

        print("Grafo validado com sucesso.")
        return True

    def get_graph_stats(self) -> Dict[str, Any]:
        # Retorna um dicionário com estatísticas sobre o grafo construído.
        if self.graph is None:
            return {}

        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'is_connected': nx.is_weakly_connected(self.graph),
            'density': nx.density(self.graph)
        }