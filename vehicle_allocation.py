"""
Módulo para alocação de veículos e gerenciamento de clientes e rotas.
Prototipo flexível que suporta futuros algoritmos de otimização.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from vrp import Vehicle, DeliveryRequest
from cost_matrix import get_cost_between_nodes

@dataclass
class Client:
    """Representa um cliente no sistema."""
    id: int
    name: str
    location: Tuple[float, float] 
    node_id: Optional[int] = None
    priority: int = 1 
    service_time: float = 0.0  
    time_window_start: Optional[datetime] = None
    time_window_end: Optional[datetime] = None
    special_requirements: List[str] = field(default_factory=list)
    
@dataclass
class AllocationRequest:
    """Representa uma solicitação de alocação de veículo."""
    id: int
    client: Client
    delivery_request: DeliveryRequest
    requested_vehicle_type: Optional[str] = None
    max_wait_time: Optional[float] = None 
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class VehicleAllocation:
    """Representa a alocação de um veículo para um cliente."""
    vehicle: Vehicle
    client: Client
    allocation_request: AllocationRequest
    estimated_arrival: datetime
    estimated_departure: datetime
    route_to_client: Optional[List[int]] = None
    route_from_client: Optional[List[int]] = None
    status: str = "pending" 

@dataclass
class AllocationSolution:
    """Representa uma solução completa de alocação."""
    allocations: List[VehicleAllocation]
    unassigned_requests: List[AllocationRequest]
    total_cost: float = 0.0
    total_distance: float = 0.0
    total_time: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)
    algorithm_used: str = "unknown"

class VehicleAllocationManager:
    """Gerencia a alocação de veículos para clientes."""
    
    def __init__(self, graph_parser, cost_matrix: Optional[Dict] = None):
        self.graph_parser = graph_parser
        self.graph = graph_parser.get_graph()
        self.cost_matrix = cost_matrix
        self.clients: Dict[int, Client] = {}
        self.vehicles: Dict[int, Vehicle] = {}
        self.allocation_requests: Dict[int, AllocationRequest] = {}
        self.allocations: Dict[int, VehicleAllocation] = {}
        
    def add_client(self, client: Client) -> None:
        """Adiciona um cliente ao sistema."""
        if client.node_id is None:
            client.node_id = self.graph_parser.get_closest_node(
                client.location[0], client.location[1]
            )
        self.clients[client.id] = client
        
    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Adiciona um veículo à frota."""
        if vehicle.current_node is None:
            vehicle.current_node = self.graph_parser.get_closest_node(
                vehicle.current_location[0], vehicle.current_location[1]
            )
        self.vehicles[vehicle.id] = vehicle
        
    def create_allocation_request(self, 
                                client_id: int, 
                                delivery_request: DeliveryRequest,
                                requested_vehicle_type: Optional[str] = None) -> AllocationRequest:
        """Cria uma solicitação de alocação."""
        if client_id not in self.clients:
            raise ValueError(f"Cliente {client_id} não encontrado")
            
        client = self.clients[client_id]
        request_id = len(self.allocation_requests) + 1
        
        request = AllocationRequest(
            id=request_id,
            client=client,
            delivery_request=delivery_request,
            requested_vehicle_type=requested_vehicle_type
        )
        
        self.allocation_requests[request_id] = request
        return request
        
    def find_available_vehicles(self, 
                               request: AllocationRequest,
                               current_time: datetime = None) -> List[Vehicle]:
        """Encontra veículos disponíveis para uma solicitação."""
        if current_time is None:
            current_time = datetime.now()
            
        available_vehicles = []
        
        for vehicle in self.vehicles.values():
            if self._is_vehicle_available(vehicle, request, current_time):
                available_vehicles.append(vehicle)
                
        return available_vehicles
        
    def _is_vehicle_available(self, 
                            vehicle: Vehicle, 
                            request: AllocationRequest,
                            current_time: datetime) -> bool:
        """Verifica se um veículo está disponível para uma solicitação."""
        if request.requested_vehicle_type and hasattr(vehicle, 'type'):
            if vehicle.type != request.requested_vehicle_type:
                return False
                
        if vehicle.current_load + request.delivery_request.weight > vehicle.capacity:
            return False
            
        vehicle_allocations = [a for a in self.allocations.values() 
                             if a.vehicle.id == vehicle.id and a.status in ["confirmed", "in_progress"]]
        
        if vehicle_allocations:
            for allocation in vehicle_allocations:
                if self._has_time_conflict(allocation, request, current_time):
                    return False
                    
        return True
        
    def _has_time_conflict(self, 
                          existing_allocation: VehicleAllocation,
                          new_request: AllocationRequest,
                          current_time: datetime) -> bool:
        """Verifica se há conflito de tempo entre alocações."""
        return False
        
    def calculate_allocation_cost(self, 
                                vehicle: Vehicle, 
                                request: AllocationRequest) -> float:
        """Calcula o custo de alocar um veículo para uma solicitação."""
        if self.cost_matrix:
            cost = get_cost_between_nodes(
                self.cost_matrix['matrix'],
                self.cost_matrix['node_index'],
                vehicle.current_node,
                request.client.node_id
            )
        else:
            from OptiRota.algorithms.a_star import get_shortest_distance_a_star
            cost = get_shortest_distance_a_star(
                self.graph,
                vehicle.current_node,
                request.client.node_id
            )
            
        priority_penalty = (4 - request.client.priority) * 0.1 * cost
        
        return cost + priority_penalty
        
    def allocate_vehicle_greedy(self, 
                               request: AllocationRequest,
                               current_time: datetime = None) -> Optional[VehicleAllocation]:
        """Aloca veículo usando estratégia gulosa (mais próximo)."""
        if current_time is None:
            current_time = datetime.now()
            
        available_vehicles = self.find_available_vehicles(request, current_time)
        
        if not available_vehicles:
            return None
            
        best_vehicle = min(available_vehicles, 
                          key=lambda v: self.calculate_allocation_cost(v, request))
        
        allocation = VehicleAllocation(
            vehicle=best_vehicle,
            client=request.client,
            allocation_request=request,
            estimated_arrival=current_time + timedelta(minutes=30),  
            estimated_departure=current_time + timedelta(minutes=60)
        )
        
        best_vehicle.current_load += request.delivery_request.weight
        
        allocation_id = len(self.allocations) + 1
        self.allocations[allocation_id] = allocation
        
        return allocation
        
    def solve_allocation_problem(self, 
                               requests: List[AllocationRequest],
                               algorithm: str = "greedy") -> AllocationSolution:
        """Resolve o problema de alocação usando algoritmo especificado."""
        if algorithm == "greedy":
            return self._solve_greedy(requests)
        else:
            raise ValueError(f"Algoritmo '{algorithm}' não suportado")
            
    def _solve_greedy(self, requests: List[AllocationRequest]) -> AllocationSolution:
        """Resolve alocação usando estratégia gulosa."""
        allocations = []
        unassigned_requests = []
        current_time = datetime.now()
        
        sorted_requests = sorted(requests, 
                               key=lambda r: (r.client.priority, r.created_at))
        
        for request in sorted_requests:
            allocation = self.allocate_vehicle_greedy(request, current_time)
            
            if allocation:
                allocations.append(allocation)
            else:
                unassigned_requests.append(request)
                
        total_cost = sum(self.calculate_allocation_cost(a.vehicle, a.allocation_request) 
                        for a in allocations)
        
        solution = AllocationSolution(
            allocations=allocations,
            unassigned_requests=unassigned_requests,
            total_cost=total_cost,
            algorithm_used="greedy"
        )
        
        return solution
        
    def get_allocation_stats(self, solution: AllocationSolution) -> Dict[str, Any]:
        """Retorna estatísticas da solução de alocação."""
        if not solution.allocations:
            return {
                'total_allocations': 0,
                'unassigned_requests': len(solution.unassigned_requests),
                'success_rate': 0.0,
                'total_cost': 0.0
            }
            
        total_requests = len(solution.allocations) + len(solution.unassigned_requests)
        
        return {
            'total_allocations': len(solution.allocations),
            'unassigned_requests': len(solution.unassigned_requests),
            'success_rate': len(solution.allocations) / total_requests if total_requests > 0 else 0,
            'total_cost': solution.total_cost,
            'average_cost_per_allocation': solution.total_cost / len(solution.allocations) if solution.allocations else 0,
            'vehicle_utilization': len(set(a.vehicle.id for a in solution.allocations)) / len(self.vehicles) if self.vehicles else 0
        }
        
    def update_allocation_status(self, 
                               allocation_id: int, 
                               new_status: str) -> bool:
        """Atualiza o status de uma alocação."""
        if allocation_id not in self.allocations:
            return False
            
        valid_statuses = ["pending", "confirmed", "in_progress", "completed", "cancelled"]
        if new_status not in valid_statuses:
            return False
            
        self.allocations[allocation_id].status = new_status
        return True
        
    def cancel_allocation(self, allocation_id: int) -> bool:
        """Cancela uma alocação e libera o veículo."""
        if allocation_id not in self.allocations:
            return False
            
        allocation = self.allocations[allocation_id]
        
        allocation.vehicle.current_load -= allocation.allocation_request.delivery_request.weight
        
        allocation.status = "cancelled"
        
        return True
