#!/usr/bin/env python3
"""
Testes unitários para o módulo datastructures.
"""

import unittest
import sys
import os

# Adiciona o diretório pai ao path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datastructures import filaPrioridade, Fila, Pilha


class TestFilaPrioridade(unittest.TestCase):
    """Testa a filaPrioridade (baseada em heap)."""

    def setUp(self):
        self.pq = filaPrioridade()

    def test_is_empty(self):
        """Testa se a fila está vazia."""
        self.assertTrue(self.pq.is_empty())
        self.pq.put('item', 1)
        self.assertFalse(self.pq.is_empty())

    def test_put_and_get_order(self):
        """Testa a ordem de prioridade."""
        self.pq.put('medium', 5)
        self.pq.put('low', 10)
        self.pq.put('high', 1)

        self.assertEqual(self.pq.get(), 'high')
        self.assertEqual(self.pq.get(), 'medium')
        self.assertEqual(self.pq.get(), 'low')

    def test_get_from_empty(self):
        """Testa get() em fila vazia."""
        with self.assertRaises(IndexError):
            self.pq.get()


class TestFila(unittest.TestCase):
    """Testa a Fila (FIFO)."""

    def setUp(self):
        self.q = Fila()

    def test_is_empty(self):
        """Testa se a fila está vazia."""
        self.assertTrue(self.q.is_empty())
        self.q.enqueue('item')
        self.assertFalse(self.q.is_empty())

    def test_fifo_order(self):
        """Testa a ordem FIFO (First-In, First-Out)."""
        self.q.enqueue(1)
        self.q.enqueue(2)
        self.q.enqueue(3)

        self.assertEqual(self.q.dequeue(), 1)
        self.assertEqual(self.q.dequeue(), 2)
        self.assertEqual(self.q.dequeue(), 3)

    def test_dequeue_from_empty(self):
        """Testa dequeue() em fila vazia."""
        with self.assertRaises(IndexError):
            self.q.dequeue()


class TestPilha(unittest.TestCase):
    """Testa a Pilha (LIFO)."""

    def setUp(self):
        self.s = Pilha()

    def test_is_empty(self):
        """Testa se a pilha está vazia."""
        self.assertTrue(self.s.is_empty())
        self.s.push('item')
        self.assertFalse(self.s.is_empty())

    def test_lifo_order(self):
        """Testa a ordem LIFO (Last-In, First-Out)."""
        self.s.push(1)
        self.s.push(2)
        self.s.push(3)

        self.assertEqual(self.s.pop(), 3)
        self.assertEqual(self.s.pop(), 2)
        self.assertEqual(self.s.pop(), 1)

    def test_pop_from_empty(self):
        """Testa pop() em pilha vazia."""
        with self.assertRaises(IndexError):
            self.s.pop()


if __name__ == '__main__':
    unittest.main()
