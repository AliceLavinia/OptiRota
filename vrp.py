from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datastructures import filaPrioridade, Fila, Pilha
import networkx as nx
from abc import ABC, abstractmethod
from dijkstra import find_path_dijkstra
from a_star import find_path_a_star

@dataclass
class DeliveryRequest:
    """Representa uma solicitação de entrega."""
    id: int
    pickup_location: Tuple[float, float]
    delivery_location: Tuple[float, float] 
    pickup_node: Optional[int] = None 
    delivery_node: Optional[int] = None 
    weight: float = 1.0  
    time_window_start: Optional[float] = None  
    time_window_end: Optional[float] = None  
    priority: int = 1  

@dataclass
class Vehicle:
    """Representa um veículo da frota."""
    id: int
    capacity: float 
    current_load: float = 0.0  
    current_location: Tuple[float, float] = (0.0, 0.0) 
    current_node: Optional[int] = None
    max_distance: Optional[float] = None 
    fuel_level: float = 100.0 

@dataclass
class Route:
    """Representa uma rota de um veículo."""
    vehicle_id: int
    deliveries: List[DeliveryRequest]
    total_distance: float = 0.0
    total_time: float = 0.0
    is_feasible: bool = True

class VRPAlgorithm(ABC):
    """Classe abstrata para algoritmos de VRP."""
    
    @abstractmethod
    def solve(self, 
              graph: nx.DiGraph,
              vehicles: List[Vehicle],
              deliveries: List[DeliveryRequest],
              depot_location: Tuple[float, float]) -> List[Route]:
        """Resolve o problema VRP."""
        pass

class NearestNeighborVRP(VRPAlgorithm):
    """Implementa o algoritmo Nearest Neighbor para VRP."""
    
    def __init__(self):
        self.graph = None
        self.depot_node = None
    
    def solve(self, 
              graph: nx.DiGraph,
              vehicles: List[Vehicle],
              deliveries: List[DeliveryRequest],
              depot_location: Tuple[float, float],
              depot_node: int = None) -> List[Route]:
        """Resolve o VRP usando Nearest Neighbor."""
        self.graph = graph
        self.depot_node = depot_node if depot_node is not None else self._find_depot_node(depot_location)
        
        routes = []
        remaining_deliveries = deliveries.copy()
        
        for vehicle in vehicles:
            if not remaining_deliveries:
                break
                
            route = self._build_route_nearest_neighbor(vehicle, remaining_deliveries)
            if route.deliveries:
                routes.append(route)
                for delivery in route.deliveries:
                    if delivery in remaining_deliveries:
                        remaining_deliveries.remove(delivery)
        
        return routes
    
    def _find_depot_node(self, depot_location: Tuple[float, float]) -> int:
        """Encontra o nó do depósito mais próximo."""
        from graph_parser import GraphParser

        if self.graph is None:
            return 0
        
        import osmnx as ox
        return ox.distance.nearest_nodes(self.graph, X=depot_location[1], Y=depot_location[0])  
    
    def _build_route_nearest_neighbor(self, 
                                    vehicle: Vehicle, 
                                    deliveries: List[DeliveryRequest]) -> Route:
        """Constrói uma rota usando nearest neighbor."""
        route_deliveries = []
        current_node = self.depot_node
        current_load = 0.0
        total_distance = 0.0
        
        available_deliveries = deliveries.copy()
        
        while available_deliveries and current_load < vehicle.capacity:
            nearest_delivery = self._find_nearest_delivery(
                current_node, available_deliveries, vehicle.capacity - current_load
            )
            
            if nearest_delivery is None:
                break
            
            if current_load + nearest_delivery.weight <= vehicle.capacity:
                try:
                    path_to_pickup = nx.shortest_path(self.graph, current_node, nearest_delivery.pickup_node, weight='length')
                    distance_to_pickup = nx.shortest_path_length(self.graph, current_node, nearest_delivery.pickup_node, weight='length') / 1000.0  
                    
                    path_to_delivery = nx.shortest_path(self.graph, nearest_delivery.pickup_node, nearest_delivery.delivery_node, weight='length')
                    distance_to_delivery = nx.shortest_path_length(self.graph, nearest_delivery.pickup_node, nearest_delivery.delivery_node, weight='length') / 1000.0  
                    
                    route_deliveries.append(nearest_delivery)
                    current_load += nearest_delivery.weight
                    total_distance += distance_to_pickup + distance_to_delivery
                    current_node = nearest_delivery.delivery_node
                    available_deliveries.remove(nearest_delivery)
                except Exception:
                    available_deliveries.remove(nearest_delivery)
                    continue
        
        if route_deliveries and current_node != self.depot_node:
            try:
                return_path = nx.shortest_path(self.graph, current_node, self.depot_node, weight='length')
                return_distance = nx.shortest_path_length(self.graph, current_node, self.depot_node, weight='length') / 1000.0  
                total_distance += return_distance
            except Exception:
                pass
        
        return Route(
            vehicle_id=vehicle.id,
            deliveries=route_deliveries,
            total_distance=total_distance,
            is_feasible=len(route_deliveries) > 0
        )
    
    def _find_nearest_delivery(self, 
                             current_node: int, 
                             deliveries: List[DeliveryRequest],
                             remaining_capacity: float) -> Optional[DeliveryRequest]:
        """Encontra a entrega mais próxima que cabe no veículo."""
        valid_deliveries = [d for d in deliveries if d.weight <= remaining_capacity]
        
        if not valid_deliveries:
            return None
        
        nearest_delivery = None
        min_distance = float('inf')
        
        for delivery in valid_deliveries:
            try:
                if not self.graph.has_node(current_node) or not self.graph.has_node(delivery.delivery_node):
                    print(f"Debug: Nó não encontrado. Atual: {current_node}, delivery: {delivery.delivery_node}")
                    continue
               
                try:
                    path = nx.shortest_path(self.graph, current_node, delivery.delivery_node, weight='length')
                    distance = nx.shortest_path_length(self.graph, current_node, delivery.delivery_node, weight='length') / 1000.0 
                except nx.NetworkXNoPath:
                    path, distance = find_path_dijkstra(self.graph, current_node, delivery.delivery_node)
                    distance = distance / 1000.0 
                if distance < min_distance and distance != float('inf'):
                    min_distance = distance
                    nearest_delivery = delivery
                    print(f"Debug: Delivery {delivery.id} distancia: {distance:.2f}km")
            except Exception as e:
                print(f"Debug: Pathfinding falhou no delivery {delivery.id}: {e}")
                continue
        
        if nearest_delivery:
            print(f"Debug: Dellivery mais proximo encontrado {nearest_delivery.id} em {min_distance:.2f}km")
        else:
            print("Debug: Sem deliveries validos")
        
        return nearest_delivery

class GeneticAlgorithmVRP(VRPAlgorithm):
    """Implementa algoritmo genético para VRP."""
    
    def __init__(self, 
                 population_size: int = 50,
                 generations: int = 100,
                 mutation_rate: float = 0.1,
                 crossover_rate: float = 0.8):
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
    
    def solve(self, 
              graph: nx.DiGraph,
              vehicles: List[Vehicle],
              deliveries: List[DeliveryRequest],
              depot_location: Tuple[float, float]) -> List[Route]:
        """Resolve o VRP usando algoritmo genético."""
        # placeholder para implementação do alg genético
        print("Algoritmo genético para VRP - implementação pendente")
        return []

class VRPManager:
    """Gerencia o problema VRP e coordena os algoritmos."""
    
    def __init__(self, graph_parser):
        self.graph_parser = graph_parser
        self.algorithms = {
            'nearest_neighbor': NearestNeighborVRP(),
            'genetic_algorithm': GeneticAlgorithmVRP()
        }
    
    def solve_vrp(self, 
                  vehicles: List[Vehicle],
                  deliveries: List[DeliveryRequest],
                  depot_location: Tuple[float, float],
                  algorithm: str = 'nearest_neighbor') -> List[Route]:
        """Resolve o problema VRP usando o algoritmo especificado."""
        
        if algorithm not in self.algorithms:
            raise ValueError(f"Algoritmo '{algorithm}' não suportado")
        
        graph = self.graph_parser.get_graph()
        
        if not self._validate_inputs(vehicles, deliveries, depot_location):
            raise ValueError("Entradas inválidas para VRP")
        
        depot_node = self._map_locations_to_nodes(deliveries, depot_location)
        
        algorithm_instance = self.algorithms[algorithm]
        routes = algorithm_instance.solve(graph, vehicles, deliveries, depot_location, depot_node)
        
        self._validate_routes(routes, vehicles)
        
        return routes
    
    def _validate_inputs(self, 
                        vehicles: List[Vehicle], 
                        deliveries: List[DeliveryRequest],
                        depot_location: Tuple[float, float]) -> bool:
        """Valida as entradas do VRP."""
        if not vehicles:
            print("Erro: Nenhum veículo fornecido")
            return False
        
        if not deliveries:
            print("Erro: Nenhuma entrega fornecida")
            return False
        
        if not depot_location:
            print("Erro: Localização do depósito não fornecida")
            return False
        
        return True
    
    def _map_locations_to_nodes(self, 
                               deliveries: List[DeliveryRequest],
                               depot_location: Tuple[float, float]) -> int:
        """Mapeia localizações geográficas para nós do grafo."""
        print("Debug: mapeando delivery para no nós do grafo...")
        node_mapping = {} 
        
        for delivery in deliveries:
            delivery.pickup_node = self.graph_parser.get_closest_node(
                delivery.pickup_location[0], delivery.pickup_location[1]
            )
            
            delivery.delivery_node = self.graph_parser.get_closest_node(
                delivery.delivery_location[0], delivery.delivery_location[1]
            )
            print(f"Debug: Delivery {delivery.id}: recolhido=({delivery.pickup_location[0]:.4f}, {delivery.pickup_location[1]:.4f}) -> no {delivery.pickup_node}")
            print(f"Debug: Delivery {delivery.id}: delivery=({delivery.delivery_location[0]:.4f}, {delivery.delivery_location[1]:.4f}) -> no {delivery.delivery_node}")
            
            if delivery.delivery_node not in node_mapping:
                node_mapping[delivery.delivery_node] = []
            node_mapping[delivery.delivery_node].append(delivery.id)
        
        for node, delivery_ids in node_mapping.items():
            if len(delivery_ids) > 1:
                print(f"Atencao: Multiplas rotas ({delivery_ids}) apontam pro mesmo no {node}")
        
        depot_node = self.graph_parser.get_closest_node(depot_location[0], depot_location[1])
        print(f"Debug: Deposito ({depot_location[0]:.4f}, {depot_location[1]:.4f}) -> no {depot_node}")
        return depot_node
    
    def _validate_routes(self, routes: List[Route], vehicles: List[Vehicle]):
        """Valida se as rotas são viáveis."""
        for route in routes:
            vehicle = next((v for v in vehicles if v.id == route.vehicle_id), None)
            if not vehicle:
                route.is_feasible = False
                continue
            
            total_weight = sum(d.weight for d in route.deliveries)
            if total_weight > vehicle.capacity:
                route.is_feasible = False
                print(f"Aviso: Rota do veículo {vehicle.id} excede capacidade")
    
    def get_solution_stats(self, routes: List[Route]) -> Dict[str, Any]:
        """Retorna estatísticas da solução."""
        if not routes:
            return {}
        
        total_distance = sum(route.total_distance for route in routes)
        total_deliveries = sum(len(route.deliveries) for route in routes)
        feasible_routes = sum(1 for route in routes if route.is_feasible)
        
        return {
            'total_routes': len(routes),
            'feasible_routes': feasible_routes,
            'total_distance': total_distance,
            'total_deliveries': total_deliveries,
            'average_route_distance': total_distance / len(routes) if routes else 0,
            'utilization_rate': feasible_routes / len(routes) if routes else 0
        }
