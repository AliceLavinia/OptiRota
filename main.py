#!/usr/bin/env python3
"""
OptiRota - Sistema de Otimização de Rotas
Exemplo de uso do módulo VRP
"""

from graph_parser import GraphParser
from vrp import VRPManager, Vehicle, DeliveryRequest
import time

def main():
    """Função principal para demonstrar o uso do VRP."""
    print("=== OptiRota - Sistema de Otimização de Rotas ===\n")
    
    print("1. Inicializando parser do grafo...")
    location = "São Paulo, Brazil"
    graph_parser = GraphParser(location)
    
    print(f"Parser configurado para: {location}")
    print("(Em produção, chame graph_parser.build_graph() para baixar dados reais)\n")
    
    print("2. Configurando frota de veículos...")
    vehicles = [
        Vehicle(id=1, capacity=100.0, current_location=(-23.5505, -46.6333)),
        Vehicle(id=2, capacity=150.0, current_location=(-23.5505, -46.6333)),
        Vehicle(id=3, capacity=80.0, current_location=(-23.5505, -46.6333))
    ]
    
    for vehicle in vehicles:
        print(f"  Veículo {vehicle.id}: Capacidade {vehicle.capacity}kg")
    print()
    
    print("3. Configurando solicitações de entrega...")
    deliveries = [
        DeliveryRequest(
            id=1,
            pickup_location=(-23.5505, -46.6333),  
            delivery_location=(-23.5613, -46.6565),  
            weight=25.0,
            priority=1
        ),
        DeliveryRequest(
            id=2,
            pickup_location=(-23.5505, -46.6333),
            delivery_location=(-23.5489, -46.6388),
            weight=40.0,
            priority=2
        ),
        DeliveryRequest(
            id=3,
            pickup_location=(-23.5505, -46.6333),
            delivery_location=(-23.5329, -46.6399),
            weight=60.0,
            priority=1
        ),
        DeliveryRequest(
            id=4,
            pickup_location=(-23.5505, -46.6333),
            delivery_location=(-23.5632, -46.6535), 
            weight=30.0,
            priority=3
        )
    ]
    
    for delivery in deliveries:
        print(f"  Entrega {delivery.id}: {delivery.weight}kg, Prioridade {delivery.priority}")
    print()
    
    depot_location = (-23.5505, -46.6333) 
    print(f"4. Depósito localizado em: {depot_location}\n")
    
    print("5. Inicializando VRP Manager...")
    vrp_manager = VRPManager(graph_parser)
    print("VRP Manager inicializado com sucesso!\n")
    
    print("6. Resolvendo problema VRP...")
    print("Algoritmos disponíveis:")
    for algo_name in vrp_manager.algorithms.keys():
        print(f"  - {algo_name}")
    print()
    
    try:
        print("Executando algoritmo Nearest Neighbor...")
        start_time = time.time()
        
        routes = vrp_manager.solve_vrp(
            vehicles=vehicles,
            deliveries=deliveries,
            depot_location=depot_location,
            algorithm='nearest_neighbor'
        )
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        print(f"Tempo de execução: {execution_time:.4f} segundos\n")
        
        print("7. Resultados da otimização:")
        print("=" * 50)
        
        if not routes:
            print("Nenhuma rota foi gerada.")
            return
        
        for i, route in enumerate(routes, 1):
            print(f"\nRota {i} (Veículo {route.vehicle_id}):")
            print(f"  Entregas: {len(route.deliveries)}")
            print(f"  Distância total: {route.total_distance:.2f} km")
            print(f"  Viável: {'Sim' if route.is_feasible else 'Não'}")
            
            if route.deliveries:
                total_weight = sum(d.weight for d in route.deliveries)
                print(f"  Peso total: {total_weight:.1f} kg")
                print("  Entregas:")
                for delivery in route.deliveries:
                    print(f"    - ID {delivery.id}: {delivery.weight}kg")
        
        print("\n8. Estatísticas da solução:")
        print("=" * 30)
        stats = vrp_manager.get_solution_stats(routes)
        
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"  {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"  {key.replace('_', ' ').title()}: {value}")
        
        # 9. Resumo
        print(f"\n9. Resumo:")
        print(f"  Total de veículos utilizados: {len(routes)}")
        print(f"  Total de entregas atendidas: {stats.get('total_deliveries', 0)}")
        print(f"  Taxa de utilização: {stats.get('utilization_rate', 0):.1%}")
        
    except Exception as e:
        print(f"Erro durante a execução: {e}")
        print("Nota: Para execução completa, é necessário um grafo real.")
        print("Chame graph_parser.build_graph() para baixar dados do OpenStreetMap.")

def demo_with_mock_data():
    """Demonstração com dados simulados (sem necessidade de conexão com OSM)."""
    print("\n=== Demonstração com Dados Simulados ===")
    
    import networkx as nx
    
    mock_graph = nx.DiGraph()
    mock_graph.add_nodes_from([0, 1, 2, 3, 4])
    mock_graph.add_edges_from([
        (0, 1, {'weight': 10.0}),
        (0, 2, {'weight': 15.0}),
        (1, 3, {'weight': 8.0}),
        (2, 4, {'weight': 12.0}),
        (3, 4, {'weight': 5.0})
    ])
    
    class MockGraphParser:
        def __init__(self):
            self.graph = mock_graph
        
        def get_graph(self):
            return self.graph
        
        def get_closest_node(self, lat, lon):
            return int((lat + 24) * 10) % 5
    
    mock_parser = MockGraphParser()
    vrp_manager = VRPManager(mock_parser)
    
    vehicles = [Vehicle(id=1, capacity=100.0)]
    deliveries = [
        DeliveryRequest(id=1, pickup_location=(0, 0), delivery_location=(1, 1), weight=50.0),
        DeliveryRequest(id=2, pickup_location=(0, 0), delivery_location=(2, 2), weight=30.0)
    ]
    
    try:
        routes = vrp_manager.solve_vrp(vehicles, deliveries, (0, 0))
        print(f"Rotas geradas: {len(routes)}")
        for route in routes:
            print(f"  Veículo {route.vehicle_id}: {len(route.deliveries)} entregas")
    except Exception as e:
        print(f"Erro na demonstração: {e}")

if __name__ == "__main__":
    main()
    demo_with_mock_data()
