#!/usr/bin/env python3
"""
Testes unitários para o módulo de matriz de custo.
"""

import unittest
import sys
import os
import networkx as nx
import numpy as np

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cost_matrix import (
    compute_cost_matrix,
    compute_cost_matrix_symmetric,
    get_cost_between_nodes,
    validate_cost_matrix,
    print_cost_matrix,
    export_cost_matrix
)

class TestCostMatrix(unittest.TestCase):
    """Testa as funções do módulo de matriz de custo."""
    
    def setUp(self):
        """Configuração inicial."""
        # Cria grafo de teste
        self.graph = nx.DiGraph()
        self.graph.add_nodes_from([0, 1, 2, 3, 4])
        self.graph.add_edges_from([
            (0, 1, {'length': 10.0}),
            (0, 2, {'length': 15.0}),
            (1, 3, {'length': 8.0}),
            (2, 4, {'length': 12.0}),
            (3, 4, {'length': 5.0}),
            (1, 2, {'length': 3.0})
        ])
        
        self.test_nodes = [0, 1, 2, 3, 4]
    
    def test_compute_cost_matrix_empty_nodes(self):
        """Testa matriz de custo com lista vazia de nós."""
        result = compute_cost_matrix(self.graph, [])
        self.assertEqual(result['matrix'].size, 0)
        self.assertEqual(result['node_index'], {})
        self.assertEqual(result['nodes'], [])
    
    def test_compute_cost_matrix_dijkstra(self):
        """Testa computação de matriz usando Dijkstra."""
        result = compute_cost_matrix(self.graph, self.test_nodes, algorithm='dijkstra')
        
        # Verifica estrutura do resultado
        self.assertIn('matrix', result)
        self.assertIn('node_index', result)
        self.assertIn('nodes', result)
        
        # Verifica dimensões da matriz
        n = len(self.test_nodes)
        self.assertEqual(result['matrix'].shape, (n, n))
        
        # Verifica diagonal (distância de um nó para ele mesmo é 0)
        np.testing.assert_array_equal(np.diag(result['matrix']), 0.0)
        
        # Verifica que não há valores negativos
        self.assertTrue(np.all(result['matrix'] >= 0))
    
    def test_compute_cost_matrix_astar(self):
        """Testa computação de matriz usando A*."""
        # Adiciona coordenadas para A*
        for i, node in enumerate(self.test_nodes):
            self.graph.nodes[node]['y'] = i * 0.01
            self.graph.nodes[node]['x'] = i * 0.01
        
        result = compute_cost_matrix(self.graph, self.test_nodes, algorithm='a_star')
        
        # Verifica estrutura do resultado
        self.assertIn('matrix', result)
        self.assertIn('node_index', result)
        self.assertIn('nodes', result)
        
        # Verifica dimensões da matriz
        n = len(self.test_nodes)
        self.assertEqual(result['matrix'].shape, (n, n))
        
        # Verifica diagonal
        np.testing.assert_array_equal(np.diag(result['matrix']), 0.0)
    
    def test_compute_cost_matrix_with_paths(self):
        """Testa computação de matriz com caminhos completos."""
        result = compute_cost_matrix(self.graph, self.test_nodes, 
                                   algorithm='dijkstra', use_paths=True)
        
        # Verifica que inclui caminhos
        self.assertIn('paths', result)
        self.assertIsInstance(result['paths'], dict)
        
        # Verifica alguns caminhos conhecidos
        if (0, 1) in result['paths']:
            self.assertEqual(result['paths'][(0, 1)], [0, 1])
    
    def test_compute_cost_matrix_invalid_algorithm(self):
        """Testa algoritmo inválido."""
        with self.assertRaises(ValueError):
            compute_cost_matrix(self.graph, self.test_nodes, algorithm='invalid')
    
    def test_compute_cost_matrix_symmetric(self):
        """Testa matriz simétrica."""
        result = compute_cost_matrix_symmetric(self.graph, self.test_nodes, 
                                             algorithm='dijkstra')
        
        # Verifica que é simétrica
        matrix = result['matrix']
        np.testing.assert_array_almost_equal(matrix, matrix.T, decimal=10)
        
        # Verifica diagonal
        np.testing.assert_array_equal(np.diag(matrix), 0.0)
    
    def test_get_cost_between_nodes(self):
        """Testa obtenção de custo entre dois nós."""
        result = compute_cost_matrix(self.graph, self.test_nodes, algorithm='dijkstra')
        
        # Testa custo entre nós conectados
        cost = get_cost_between_nodes(result['matrix'], result['node_index'], 0, 1)
        self.assertEqual(cost, 10.0)
        
        # Testa custo de um nó para ele mesmo
        cost = get_cost_between_nodes(result['matrix'], result['node_index'], 0, 0)
        self.assertEqual(cost, 0.0)
        
        # Testa nós que não existem
        cost = get_cost_between_nodes(result['matrix'], result['node_index'], 0, 999)
        self.assertEqual(cost, float('inf'))
    
    def test_validate_cost_matrix_valid(self):
        """Testa validação de matriz válida."""
        result = compute_cost_matrix(self.graph, self.test_nodes, algorithm='dijkstra')
        
        self.assertTrue(validate_cost_matrix(result['matrix'], result['node_index']))
    
    def test_validate_cost_matrix_invalid_empty(self):
        """Testa validação de matriz vazia."""
        self.assertFalse(validate_cost_matrix(np.array([]), {}))
        self.assertFalse(validate_cost_matrix(None, {}))
    
    def test_validate_cost_matrix_invalid_not_square(self):
        """Testa validação de matriz não quadrada."""
        invalid_matrix = np.array([[1, 2, 3], [4, 5, 6]])  # 2x3
        node_index = {0: 0, 1: 1, 2: 2}
        
        self.assertFalse(validate_cost_matrix(invalid_matrix, node_index))
    
    def test_validate_cost_matrix_invalid_diagonal(self):
        """Testa validação de matriz com diagonal não zero."""
        invalid_matrix = np.array([[1, 2], [3, 4]])
        node_index = {0: 0, 1: 1}
        
        self.assertFalse(validate_cost_matrix(invalid_matrix, node_index))
    
    def test_validate_cost_matrix_invalid_negative(self):
        """Testa validação de matriz com valores negativos."""
        invalid_matrix = np.array([[0, -1], [2, 0]])
        node_index = {0: 0, 1: 1}
        
        self.assertFalse(validate_cost_matrix(invalid_matrix, node_index))
    
    def test_validate_cost_matrix_invalid_size_mismatch(self):
        """Testa validação com tamanho de matriz diferente do node_index."""
        matrix = np.array([[0, 1], [1, 0]])
        node_index = {0: 0, 1: 1, 2: 2}  # 3 nós, mas matriz 2x2
        
        self.assertFalse(validate_cost_matrix(matrix, node_index))

class TestCostMatrixEdgeCases(unittest.TestCase):
    """Testa casos extremos da matriz de custo."""
    
    def test_single_node_matrix(self):
        """Testa matriz com um único nó."""
        graph = nx.DiGraph()
        graph.add_node(0)
        
        result = compute_cost_matrix(graph, [0], algorithm='dijkstra')
        
        self.assertEqual(result['matrix'].shape, (1, 1))
        self.assertEqual(result['matrix'][0, 0], 0.0)
        self.assertEqual(result['node_index'], {0: 0})
    
    def test_disconnected_graph(self):
        """Testa grafo desconectado."""
        graph = nx.DiGraph()
        graph.add_nodes_from([0, 1, 2])
        # Sem arestas - grafo desconectado
        
        result = compute_cost_matrix(graph, [0, 1, 2], algorithm='dijkstra')
        
        # Diagonal deve ser zero
        np.testing.assert_array_equal(np.diag(result['matrix']), 0.0)
        
        # Todos os outros valores devem ser infinito
        matrix = result['matrix']
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if i != j:
                    self.assertEqual(matrix[i, j], float('inf'))
    
    def test_duplicate_nodes(self):
        """Testa lista de nós com duplicatas."""
        graph = nx.DiGraph()
        graph.add_nodes_from([0, 1, 2])
        graph.add_edges_from([(0, 1, {'length': 5.0}), (1, 2, {'length': 3.0})])
        
        # Lista com duplicatas
        nodes_with_duplicates = [0, 1, 2, 0, 1]
        
        result = compute_cost_matrix(graph, nodes_with_duplicates, algorithm='dijkstra')
        
        # Deve remover duplicatas
        self.assertEqual(len(result['nodes']), 3)
        self.assertEqual(len(result['node_index']), 3)
        self.assertEqual(result['matrix'].shape, (3, 3))

class TestCostMatrixUtilities(unittest.TestCase):
    """Testa funções utilitárias da matriz de custo."""
    
    def test_print_cost_matrix(self):
        """Testa impressão da matriz de custo."""
        import io
        import sys
        
        # Captura stdout
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            # Cria matriz de teste
            matrix = np.array([[0, 10, 20], [10, 0, 15], [20, 15, 0]])
            node_index = {0: 0, 1: 1, 2: 2}
            
            print_cost_matrix(matrix, node_index)
            
            # Verifica que algo foi impresso
            output = captured_output.getvalue()
            self.assertIn("Matriz de Custo", output)
            self.assertIn("0", output)
            
        finally:
            # Restaura stdout
            sys.stdout = sys.__stdout__
    
    def test_export_cost_matrix(self):
        """Testa exportação da matriz de custo."""
        import tempfile
        import os
        
        # Cria matriz de teste
        matrix = np.array([[0, 10, 20], [10, 0, 15], [20, 15, 0]])
        node_index = {0: 0, 1: 1, 2: 2}
        
        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            export_cost_matrix(matrix, node_index, tmp_filename)
            
            # Verifica que o arquivo foi criado
            self.assertTrue(os.path.exists(tmp_filename))
            
            # Verifica conteúdo básico
            with open(tmp_filename, 'r') as f:
                content = f.read()
                self.assertIn('0', content)
                self.assertIn('1', content)
                self.assertIn('2', content)
                
        finally:
            # Remove arquivo temporário
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)
    
    def test_export_cost_matrix_empty(self):
        """Testa exportação de matriz vazia."""
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_file:
            tmp_filename = tmp_file.name
        
        try:
            # Não deve criar arquivo para matriz vazia
            export_cost_matrix(np.array([]), {}, tmp_filename)
            self.assertFalse(os.path.exists(tmp_filename))
            
        finally:
            if os.path.exists(tmp_filename):
                os.unlink(tmp_filename)

if __name__ == '__main__':
    unittest.main()
