import unittest
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from vrp import DeliveryRequest, Vehicle, Route, VRPManager, NearestNeighborVRP
from graph_parser import GraphParser

class TestVRPModule(unittest.TestCase):
    """Testa o módulo VRP."""
    
    def setUp(self):
        """Configuração inicial para os testes."""
        self.graph_parser = GraphParser("São Paulo, Brazil")
        # Para testes, vamos usar um grafo mock
        self.mock_graph = None
        
        # Dados de teste
        self.vehicles = [
            Vehicle(id=1, capacity=100.0),
            Vehicle(id=2, capacity=150.0)
        ]
        
        self.deliveries = [
            DeliveryRequest(
                id=1,
                pickup_location=(-23.5505, -46.6333),  # São Paulo
                delivery_location=(-23.5613, -46.6565),
                weight=50.0
            ),
            DeliveryRequest(
                id=2,
                pickup_location=(-23.5505, -46.6333),
                delivery_location=(-23.5489, -46.6388),
                weight=30.0
            )
        ]
        
        self.depot_location = (-23.5505, -46.6333)
    
    def test_delivery_request_creation(self):
        """Testa criação de DeliveryRequest."""
        delivery = DeliveryRequest(
            id=1,
            pickup_location=(0.0, 0.0),
            delivery_location=(1.0, 1.0),
            weight=25.0
        )
        
        self.assertEqual(delivery.id, 1)
        self.assertEqual(delivery.weight, 25.0)
        self.assertIsNone(delivery.pickup_node)
        self.assertIsNone(delivery.delivery_node)
    
    def test_vehicle_creation(self):
        """Testa criação de Vehicle."""
        vehicle = Vehicle(id=1, capacity=100.0)
        
        self.assertEqual(vehicle.id, 1)
        self.assertEqual(vehicle.capacity, 100.0)
        self.assertEqual(vehicle.current_load, 0.0)
        self.assertEqual(vehicle.fuel_level, 100.0)
    
    def test_route_creation(self):
        """Testa criação de Route."""
        deliveries = [self.deliveries[0]]
        route = Route(
            vehicle_id=1,
            deliveries=deliveries,
            total_distance=10.5
        )
        
        self.assertEqual(route.vehicle_id, 1)
        self.assertEqual(len(route.deliveries), 1)
        self.assertEqual(route.total_distance, 10.5)
        self.assertTrue(route.is_feasible)
    
    def test_nearest_neighbor_vrp_initialization(self):
        """Testa inicialização do NearestNeighborVRP."""
        vrp = NearestNeighborVRP()
        self.assertIsNone(vrp.graph)
        self.assertIsNone(vrp.depot_node)
    
    def test_vrp_manager_initialization(self):
        """Testa inicialização do VRPManager."""
        manager = VRPManager(self.graph_parser)
        self.assertIsNotNone(manager.graph_parser)
        self.assertIn('nearest_neighbor', manager.algorithms)
        self.assertIn('genetic_algorithm', manager.algorithms)
    
    def test_validate_inputs_valid(self):
        """Testa validação de entradas válidas."""
        manager = VRPManager(self.graph_parser)
        result = manager._validate_inputs(
            self.vehicles, 
            self.deliveries, 
            self.depot_location
        )
        self.assertTrue(result)
    
    def test_validate_inputs_invalid_vehicles(self):
        """Testa validação com veículos inválidos."""
        manager = VRPManager(self.graph_parser)
        result = manager._validate_inputs([], self.deliveries, self.depot_location)
        self.assertFalse(result)
    
    def test_validate_inputs_invalid_deliveries(self):
        """Testa validação com entregas inválidas."""
        manager = VRPManager(self.graph_parser)
        result = manager._validate_inputs(self.vehicles, [], self.depot_location)
        self.assertFalse(result)
    
    def test_validate_inputs_invalid_depot(self):
        """Testa validação com depósito inválido."""
        manager = VRPManager(self.graph_parser)
        result = manager._validate_inputs(self.vehicles, self.deliveries, None)
        self.assertFalse(result)
    
    def test_get_solution_stats_empty(self):
        """Testa estatísticas de solução vazia."""
        manager = VRPManager(self.graph_parser)
        stats = manager.get_solution_stats([])
        self.assertEqual(stats, {})
    
    def test_get_solution_stats_with_routes(self):
        """Testa estatísticas de solução com rotas."""
        manager = VRPManager(self.graph_parser)
        
        routes = [
            Route(vehicle_id=1, deliveries=[self.deliveries[0]], total_distance=10.0),
            Route(vehicle_id=2, deliveries=[self.deliveries[1]], total_distance=15.0)
        ]
        
        stats = manager.get_solution_stats(routes)
        
        self.assertEqual(stats['total_routes'], 2)
        self.assertEqual(stats['feasible_routes'], 2)
        self.assertEqual(stats['total_distance'], 25.0)
        self.assertEqual(stats['total_deliveries'], 2)
        self.assertEqual(stats['average_route_distance'], 12.5)
        self.assertEqual(stats['utilization_rate'], 1.0)

if __name__ == '__main__':
    unittest.main()
