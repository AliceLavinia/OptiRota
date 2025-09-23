"""
Script simples para testar as implementações dos algoritmos.
"""

def test_basic_functionality():
    """Testa funcionalidade básica dos algoritmos."""
    try:
        import networkx as nx
        from dijkstra import find_path_dijkstra
        from a_star import find_path_a_star
        
        graph = nx.DiGraph()
        graph.add_nodes_from([0, 1, 2, 3])
        graph.add_edges_from([
            (0, 1, {'length': 10.0}),
            (1, 2, {'length': 5.0}),
            (2, 3, {'length': 8.0}),
            (0, 3, {'length': 25.0})
        ])
        
        path, distance = find_path_dijkstra(graph, 0, 3)
        print(f"✓ Dijkstra: Path {path}, Distance {distance}")
        
        for i in range(4):
            graph.nodes[i]['y'] = i * 0.01
            graph.nodes[i]['x'] = i * 0.01
        
        # Testa A*
        path, distance = find_path_a_star(graph, 0, 3)
        print(f"✓ A*: Path {path}, Distance {distance}")
        
        return True
    except Exception as e:
        print(f"✗ Functionality test error: {e}")
        return False

def test_cost_matrix():
    """Testa matriz de custo."""
    try:
        import networkx as nx
        from cost_matrix import compute_cost_matrix
        
        graph = nx.DiGraph()
        graph.add_nodes_from([0, 1, 2])
        graph.add_edges_from([
            (0, 1, {'length': 10.0}),
            (1, 2, {'length': 5.0}),
            (0, 2, {'length': 20.0})
        ])
        
        result = compute_cost_matrix(graph, [0, 1, 2], algorithm='dijkstra')
        print(f"✓ Cost matrix computed: {result['matrix'].shape}")
        
        return True
    except Exception as e:
        print(f"✗ Cost matrix test error: {e}")
        return False

def main():
    """Executa todos os testes."""
    print("=== Testando Implementações ===\n")
    
    print("\n=== Testando Funcionalidade Básica ===")
    if not test_basic_functionality():
        print("\n falha na funcionalidade básica.")
        return
    
    print("\n=== Testando Matriz de Custo ===")
    if not test_cost_matrix():
        print("\n falha na matriz de custo.")
        return
    
    print("\n todos os testes passaram")

if __name__ == "__main__":
    main()
