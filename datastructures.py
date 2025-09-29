import heapq
import collections

class filaPrioridade:
  """Implementa uma fila de prioridade usando heapq.
  É a estrutura de dados central para maior eficiência de Dijkstra e A*
  """

  def __init__(self):
    self.elements = []

  def is_empty(self):
    return not self.elements
    
  def put(self, item, prioridade):
    """Adiciona um item à fila com uma certa prioridade."""
    heapq.heappush(self.elements, (prioridade, item))

  def get(self):
    """Remove e retorna o item com a menor prioridade."""
    return heapq.heappop(self.elements)[1]

class Fila:
  """Implementa uma fila padrão FIFO(gerenciar pedidos de entrega)"""
  def __init__(self):
    self.elements = collections.deque()

  def is_empty(self):
    return not self.elements
  
  def enqueue(self, item):
    """Adiciona um item ao final da fila."""
    self.elements.append(item)

  def dequeue(self):
    """Remove e retorna o item do início da fila."""
    return self.elements.popleft()
    
class Pilha:
  """Implementa uma pilha padrão LIFO(para reconstruir os caminhos encontrados pelos algoritmos)"""
  def __init__(self):
    self.elements = []

  def is_empty(self):
    return not self.elements
  
  def push(self, item):
    """Adiciona um item ao topo da pilha."""
    self.elements.append(item)

  def pop(self):
    """Remove e retorna o item do topo da pilha."""
    return self.elements.pop()