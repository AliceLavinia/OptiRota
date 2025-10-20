#!/usr/bin/env python3
"""
Testes unitários para o módulo graph_parser.
"""

import unittest
import sys
import os
import networkx as nx
from unittest.mock import patch, MagicMock

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from graph_parser import GraphParser


class TestGraphParser(unittest.TestCase):
    """Testa o GraphParser."""

    def setUp(self):
        """Configura um grafo mock básico."""
        self.location = "Test City, Test Country"
        self.parser = GraphParser(self.location)

        # Cria um grafo mock que será "retornado" pelo osmnx
        self.mock_graph = nx.MultiDiGraph()
        self.mock_graph.add_node(1, y=10.0, x=10.0)
        self.mock_graph.add_node(2, y=10.1, x=10.1)
        self.mock_graph.add_edge(1, 2, 0, length=100.0, travel_time=10.0)

    def test_initialization(self):
        """Testa a inicialização do parser."""
        self.assertEqual(self.parser.location_query, self.location)
        self.assertIsNone(self.parser.graph)

    def test_get_graph_not_built(self):
        """Testa get_graph() antes de build_graph()."""
        with self.assertRaisesRegex(ValueError, "Grafo não construído"):
            self.parser.get_graph()

    @patch('graph_parser.nx.weakly_connected_components')
    @patch('graph_parser.ox')
    def test_build_graph(self, mock_ox, mock_wcc):
        """Testa o processo de build_graph() usando mocks."""

        # Configura os mocks para não fazerem chamadas de rede
        mock_ox.graph_from_place.return_value = self.mock_graph
        mock_ox.add_edge_speeds.return_value = self.mock_graph
        mock_ox.add_edge_travel_times.return_value = self.mock_graph
        mock_wcc.return_value = [self.mock_graph.nodes()]  # Simula o maior componente

        # Chama a função
        graph = self.parser.build_graph()

        # Verifica se o grafo foi construído
        self.assertIsNotNone(graph)
        self.assertEqual(graph, self.parser.get_graph())

        # Verifica se as funções mock foram chamadas
        mock_ox.graph_from_place.assert_called_once_with(self.location, network_type='drive')
        mock_wcc.assert_called_once()
        mock_ox.add_edge_speeds.assert_called_once()
        mock_ox.add_edge_travel_times.assert_called_once()

    @patch('graph_parser.ox.distance.nearest_nodes')
    def test_get_closest_node(self, mock_nearest_nodes):
        """Testa get_closest_node() e a lógica robusta."""

        # Simula que o grafo já foi construído
        self.parser.graph = self.mock_graph

        # Teste 1: Simula retorno como array (versões antigas do osmnx)
        mock_nearest_nodes.return_value = [1]
        node = self.parser.get_closest_node(10.0, 10.0)
        self.assertEqual(node, 1)
        mock_nearest_nodes.assert_called_with(self.mock_graph, X=10.0, Y=10.0)

        # Teste 2: Simula retorno como int (versões novas do osmnx)
        mock_nearest_nodes.return_value = 2
        node = self.parser.get_closest_node(10.1, 10.1)
        self.assertEqual(node, 2)
        mock_nearest_nodes.assert_called_with(self.mock_graph, X=10.1, Y=10.1)

    def test_get_node_attributes(self):
        """Testa obtenção de atributos de nó."""
        self.parser.graph = self.mock_graph
        attrs = self.parser.get_node_attributes(1)
        self.assertEqual(attrs['y'], 10.0)

        with self.assertRaises(ValueError):
            self.parser.get_node_attributes(999)  # Nó não existe

    def test_get_edge_attributes(self):
        """Testa obtenção de atributos de aresta."""
        self.parser.graph = self.mock_graph
        attrs = self.parser.get_edge_attributes(1, 2)
        self.assertEqual(attrs['length'], 100.0)

        with self.assertRaises(ValueError):
            self.parser.get_edge_attributes(2, 1)  # Aresta não existe

    def test_validate_graph(self):
        """Testa a validação do grafo."""
        self.parser.graph = self.mock_graph
        # Grafo mock tem 'length' e 'travel_time' > 0, deve ser válido
        self.assertTrue(self.parser.validate_graph())

        # Testa grafo inválido (sem 'length')
        invalid_graph = nx.MultiDiGraph()
        invalid_graph.add_edge(1, 2, 0, travel_time=10)
        self.parser.graph = invalid_graph
        self.assertFalse(self.parser.validate_graph())


if __name__ == '__main__':
    unittest.main()
