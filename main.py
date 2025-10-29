# main.py

"""
OptiRota - Sistema de Otimização de Rotas
Demonstração completa do fluxo: construção do grafo, geração da matriz de custos (A*),
resolução do VRP e alocação de veículos.
"""

import time
import networkx as nx
from typing import List, Dict, Tuple

# Importações dos seus módulos
from graph_parser import GraphParser
from vrp import VRPManager, Vehicle, DeliveryRequest, Route # Importar Route também
from vehicle_allocation import VehicleAllocationManager, Client, AllocationRequest, VehicleAllocation, AllocationSolution
from cost_matrix import compute_cost_matrix, print_cost_matrix, export_cost_matrix
from algorithms.a_star import find_path_a_star, get_node_coordinates # get_node_coordinates para depuração/exemplo

def run_optirota_workflow():
    """
    Executa o fluxo de trabalho completo: cria grafo, gera matriz de custos,
    demonstra VRP e alocação de veículos.
    """
    print("=== OptiRota - Sistema de Otimização de Rotas ===\n")
    
    # --- 1. Construção do Grafo ---
    print("1. Inicializando parser do grafo e baixando dados do OpenStreetMap...")
    location = "São Paulo, Brazil" # Você pode mudar para uma área menor para testes mais rápidos
    graph_parser = GraphParser(location)
    
    graph = None
    try:
        graph_parser.build_graph()
        graph = graph_parser.get_graph()
        print(f"Grafo construído com {graph.number_of_nodes()} nós e {graph.number_of_edges()} arestas.\n")
    except Exception as e:
        print(f"Erro ao construir grafo: {e}")
        print("Não foi possível baixar dados reais. A demonstração continuará com um grafo mock para VRP e Alocação.\n")
        # Se o grafo real falhar, criamos um mock para as próximas etapas
        graph = nx.DiGraph()
        graph.add_nodes_from([0, 1, 2, 3, 4])
        graph.add_edges_from([
            (0, 1, {'weight': 10.0, 'length': 10.0}),
            (0, 2, {'weight': 15.0, 'length': 15.0}),
            (1, 3, {'weight': 8.0, 'length': 8.0}),
            (2, 4, {'weight': 12.0, 'length': 12.0}),
            (3, 4, {'weight': 5.0, 'length': 5.0})
        ])
        # Adicione coordenadas aos nós mock para que a heurística do A* funcione
        graph.nodes[0].update({'y': -23.5505, 'x': -46.6333})
        graph.nodes[1].update({'y': -23.5613, 'x': -46.6565})
        graph.nodes[2].update({'y': -23.5489, 'x': -46.6288})
        graph.nodes[3].update({'y': -23.5329, 'x': -46.6399})
        graph.nodes[4].update({'y': -23.5632, 'x': -46.6535})
        print("Grafo mock criado para continuar a demonstração.\n")

        # Mock do graph_parser para o caso de falha no download real
        class MockGraphParser:
            def __init__(self, mock_graph):
                self.graph = mock_graph
                # Mapeamento simples para o mock
                self._coords_to_node = {
                    (-23.5505, -46.6333): 0,
                    (-23.5613, -46.6565): 1,
                    (-23.5489, -46.6288): 2,
                    (-23.5329, -46.6399): 3,
                    (-23.5632, -46.6535): 4
                }
            def get_graph(self): return self.graph
            def get_closest_node(self, lat, lon):
                # Tenta encontrar uma correspondência exata ou a mais próxima no mock
                for (mlat, mlon), node_id in self._coords_to_node.items():
                    if abs(mlat - lat) < 0.001 and abs(mlon - lon) < 0.001:
                        return node_id
                # Fallback para o nó mais próximo do depósito mock
                return 0 # Default para o nó 0
            def get_node_coordinates(self, node_id: int) -> Tuple[float, float]:
                node_data = self.graph.nodes[node_id]
                return node_data['y'], node_data['x']
        graph_parser = MockGraphParser(graph) # Substitui o parser real pelo mock

    # --- 2. Geração da Matriz de Custos ---
    print("2. Gerando a matriz de custos para o VRP usando A*...")
    # Definir os locais de interesse (depósito + clientes)
    depot_location_coords = (-23.5505, -46.6333) # Coordenadas do depósito
    
    # Coordenadas dos clientes (usadas nas DeliveryRequests)
    client_locations_coords = [
        (-23.5613, -46.6565), # Cliente 1
        (-23.5489, -46.6288), # Cliente 2
        (-23.5329, -46.6399), # Cliente 3
        (-23.5632, -46.6535)  # Cliente 4
    ]
    
    # Mapear todas as coordenadas para IDs de nós no grafo
    all_unique_coords = [depot_location_coords] + client_locations_coords
    node_ids_for_cost_matrix = []
    for lat, lon in all_unique_coords:
        try:
            node_id = graph_parser.get_closest_node(lat, lon)
            if node_id not in node_ids_for_cost_matrix: # Garantir unicidade
                node_ids_for_cost_matrix.append(node_id)
        except Exception as e:
            print(f"  Aviso: Não foi possível encontrar nó para ({lat}, {lon}): {e}")
    
    if not node_ids_for_cost_matrix:
        print("  Nenhum nó válido encontrado para gerar a matriz de custos. Pulando geração.")
        cost_matrix_data = None
    else:
        print(f"  Nós selecionados para a matriz de custos: {node_ids_for_cost_matrix}")
        cost_matrix_data = compute_cost_matrix(graph, node_ids_for_cost_matrix, algorithm='a_star', use_paths=False)
        print("\nMatriz de Custos Gerada:")
        print_cost_matrix(cost_matrix_data['matrix'], cost_matrix_data['node_index'], precision=2)
        export_cost_matrix(cost_matrix_data['matrix'], cost_matrix_data['node_index'], "cost_matrix_output.csv")
        print("-" * 50)

    # --- 3. Configuração de Veículos e Entregas ---
    print("3. Configurando frota de veículos e solicitações de entrega...")
    vehicles = [
        Vehicle(id=1, capacity=100.0, current_location=depot_location_coords),
        Vehicle(id=2, capacity=150.0, current_location=depot_location_coords),
        Vehicle(id=3, capacity=80.0, current_location=depot_location_coords)
    ]
    
    deliveries = [
        DeliveryRequest(id=1, pickup_location=depot_location_coords, delivery_location=client_locations_coords[0], weight=25.0, priority=1),
        DeliveryRequest(id=2, pickup_location=depot_location_coords, delivery_location=client_locations_coords[1], weight=40.0, priority=2),
        DeliveryRequest(id=3, pickup_location=depot_location_coords, delivery_location=client_locations_coords[2], weight=60.0, priority=1),
        DeliveryRequest(id=4, pickup_location=depot_location_coords, delivery_location=client_locations_coords[3], weight=30.0, priority=3)
    ]
    
    for vehicle in vehicles:
        print(f"  Veículo {vehicle.id}: Capacidade {vehicle.capacity}kg")
    for delivery in deliveries:
        print(f"  Entrega {delivery.id}: {delivery.weight}kg, Prioridade {delivery.priority}")
    print(f"  Depósito localizado em: {depot_location_coords}\n")
    
    # --- 4. Resolução do Problema de Roteamento de Veículos (VRP) ---
    print("4. Resolvendo problema VRP com VRPManager (Nearest Neighbor)...")
    vrp_manager = VRPManager(graph_parser)
    
    start_time_vrp = time.time()
    routes = vrp_manager.solve_vrp(
        vehicles=vehicles,
        deliveries=deliveries,
        depot_location=depot_location_coords,
        algorithm='nearest_neighbor'
    )
    end_time_vrp = time.time()
    print(f"  Tempo de execução do VRP: {end_time_vrp - start_time_vrp:.4f} segundos\n")
    
    print("Resultados do VRP:")
    if not routes:
        print("  Nenhuma rota foi gerada pelo VRP.")
    else:
        for i, route in enumerate(routes, 1):
            print(f"\n  Rota {i} (Veículo {route.vehicle_id}):")
            print(f"    Entregas: {len(route.deliveries)}")
            print(f"    Distância total: {route.total_distance:.2f} km")
            print(f"    Viável: {'Sim' if route.is_feasible else 'Não'}")
            if route.deliveries:
                total_weight = sum(d.weight for d in route.deliveries)
                print(f"    Peso total: {total_weight:.1f} kg")
                print("    Entregas:")
                for d_req in route.deliveries:
                    print(f"      - ID {d_req.id}: {d_req.weight}kg")
        stats_vrp = vrp_manager.get_solution_stats(routes)
        print("\n  Estatísticas da solução VRP:")
        for key, value in stats_vrp.items():
            if isinstance(value, float):
                print(f"    {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"    {key.replace('_', ' ').title()}: {value}")
    print("-" * 50)

    # --- 5. Demonstração de Alocação de Veículos ---
    print("5. Demonstrando Alocação de Veículos com VehicleAllocationManager...")
    # O VehicleAllocationManager pode receber a matriz de custos pré-calculada
    alloc_manager = VehicleAllocationManager(graph_parser, cost_matrix=cost_matrix_data)
    
    # Adicionar veículos ao manager de alocação
    for vehicle in vehicles:
        alloc_manager.add_vehicle(vehicle)
    
    # Criar clientes e solicitações de alocação
    clients = [
        Client(id=101, name="Cliente A", location=client_locations_coords[0], priority=1),
        Client(id=102, name="Cliente B", location=client_locations_coords[1], priority=2),
        Client(id=103, name="Cliente C", location=client_locations_coords[2], priority=1)
    ]
    for client in clients:
        alloc_manager.add_client(client)

    alloc_requests = [
        alloc_manager.create_allocation_request(clients[0].id, deliveries[0]),
        alloc_manager.create_allocation_request(clients[1].id, deliveries[1]),
        alloc_manager.create_allocation_request(clients[2].id, deliveries[2])
    ]

    start_time_alloc = time.time()
    allocation_solution = alloc_manager.solve_allocation_problem(alloc_requests, algorithm="greedy")
    end_time_alloc = time.time()
    print(f"  Tempo de execução da Alocação: {end_time_alloc - start_time_alloc:.4f} segundos\n")

    print("Resultados da Alocação:")
    if not allocation_solution.allocations:
        print("  Nenhuma alocação foi realizada.")
    else:
        for alloc in allocation_solution.allocations:
            print(f"\n  Alocação ID {alloc.allocation_request.id}:")
            print(f"    Veículo {alloc.vehicle.id} alocado para Cliente {alloc.client.id} ({alloc.client.name})")
            print(f"    Entrega: {alloc.allocation_request.delivery_request.id} ({alloc.allocation_request.delivery_request.weight}kg)")
            print(f"    Custo estimado: {alloc_manager.calculate_allocation_cost(alloc.vehicle, alloc.allocation_request):.2f}")
        
        stats_alloc = alloc_manager.get_allocation_stats(allocation_solution)
        print("\n  Estatísticas da solução de Alocação:")
        for key, value in stats_alloc.items():
            if isinstance(value, float):
                print(f"    {key.replace('_', ' ').title()}: {value:.2f}")
            else:
                print(f"    {key.replace('_', ' ').title()}: {value}")
    print("-" * 50)

    print("\n=== Fluxo de trabalho do OptiRota concluído! ===")

if __name__ == "__main__":
    run_optirota_workflow()