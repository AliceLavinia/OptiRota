from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass
from datastructures import filaPrioridade, Fila, Pilha
import networkx as nx
import numpy as np
from abc import ABC, abstractmethod

@dataclass
class DeliveryRequest:
    """Representa uma solicitação de entrega."""
    id: int
    pickup_location: Tuple[float, float]
    delivery_location: Tuple[float, float] 
    pickup_node: Optional[int] = None 
    delivery_node: Optional[int] = None 
    weight: float = 1.0  # peso da carga
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
              depot_location: Tuple[float, float]) -> List[Route]:
        """Resolve o VRP usando Nearest Neighbor."""
        self.graph = graph
        self.depot_node = self._find_depot_node(depot_location)
        
        routes = []
        remaining_deliveries = deliveries.copy()
        
        for vehicle in vehicles:
            if not remaining_deliveries:
                break
                
            route = self._build_route_nearest_neighbor(vehicle, remaining_deliveries)
            if route.deliveries:
                routes.append(route)
                for delivery in route.deliveries:
                    remaining_deliveries.remove(delivery)
        
        return routes
    
    def _find_depot_node(self, depot_location: Tuple[float, float]) -> int:
        """Encontra o nó do depósito mais próximo."""
        return 0  
    
    def _build_route_nearest_neighbor(self, 
                                    vehicle: Vehicle, 
                                    deliveries: List[DeliveryRequest]) -> Route:
        """Constrói uma rota usando nearest neighbor."""
        route_deliveries = []
        current_node = self.depot_node
        current_load = 0.0
        total_distance = 0.0
        
        while deliveries and current_load < vehicle.capacity:
            nearest_delivery = self._find_nearest_delivery(
                current_node, deliveries, vehicle.capacity - current_load
            )
            
            if nearest_delivery is None:
                break
            
            if current_load + nearest_delivery.weight <= vehicle.capacity:
                route_deliveries.append(nearest_delivery)
                current_load += nearest_delivery.weight
                total_distance += 1.0
                deliveries.remove(nearest_delivery)
        
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
        
        # mplementação simplificada, só retorna a primeira válida
        #em produção, calcular distância real usando Dijkstra/A*
        return valid_deliveries[0]

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
        
        self._map_locations_to_nodes(deliveries, depot_location)
        
        algorithm_instance = self.algorithms[algorithm]
        routes = algorithm_instance.solve(graph, vehicles, deliveries, depot_location)
        
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
                               depot_location: Tuple[float, float]):
        """Mapeia localizações geográficas para nós do grafo."""
        for delivery in deliveries:
            delivery.pickup_node = self.graph_parser.get_closest_node(
                delivery.pickup_location[0], delivery.pickup_location[1]
            )
            
            delivery.delivery_node = self.graph_parser.get_closest_node(
                delivery.delivery_location[0], delivery.delivery_location[1]
            )
    
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
