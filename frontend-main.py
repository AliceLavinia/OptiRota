import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading  # Importado para carregar o mapa sem travar a UI

# --- Imports do Backend ---
try:
    from graph_parser import GraphParser
    from a_star import find_path_a_star, get_shortest_distance_a_star
    from dijkstra import find_path_dijkstra
    import osmnx as ox
    import networkx as nx
except ImportError as e:
    messagebox.showerror("Erro de Importação",
                         f"Não foi possível importar os módulos do backend: {e}\n"
                         "Verifique se 'graph_parser.py' existe e se 'osmnx' está instalado.")
    exit()


# --- Fim dos Imports do Backend ---


class RouteOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OptiRota - Otimizador de Rotas")
        self.root.geometry("1200x800")
        # Removida cor de fundo fixa para permitir tema nativo (Dark Mode)
        # self.root.configure(bg="#f0f0f0")

        # --- Estado do Backend ---
        self.graph_parser = None
        self.graph = None
        self.bbox = None  # (min_lon, min_lat, max_lon, max_lat) Bounding box do mapa

        self.points = []
        self.point_nodes = {}
        self.route_nodes = []
        self.multi_stop_route = []
        # --- Fim do Estado ---

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)  # Removido: bg="#f0f0f0"
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Frame de Carregamento do Mapa ---
        map_load_frame = tk.LabelFrame(
            main_frame,
            text="1. Carregar Mapa (OSM)",
            font=("Arial", 10, "bold"),
            # Removido: bg="white"
            padx=15,
            pady=10
        )
        map_load_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(map_load_frame, text="Localização (Ex: 'São Paulo, Brazil'):").pack(side=tk.LEFT,
                                                                                     padx=5)  # Removido: bg="white"
        self.location_entry = tk.Entry(map_load_frame, width=40)

        # CORREÇÃO: Localização padrão Jatiúca (mais estável que Ponta Verde)
        self.location_entry.insert(0, "Jatiúca, Maceió")
        self.location_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        # CORREÇÃO: Removidas cores bg/fg para legibilidade no Dark Mode
        self.btn_load_map = tk.Button(
            map_load_frame,
            text="Carregar Mapa",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=self.start_map_load_thread  # CORREÇÃO: Threading
        )
        self.btn_load_map.pack(side=tk.LEFT, padx=10)

        self.load_status_label = tk.Label(map_load_frame, text="")  # Removido: bg="white"
        self.load_status_label.pack(side=tk.LEFT, padx=5)
        # --- Fim do Frame de Carregamento ---

        params_frame = tk.LabelFrame(
            main_frame,
            text="2. Parâmetros de Busca",
            font=("Arial", 10, "bold"),
            # Removido: bg="white"
            padx=15,
            pady=15
        )
        params_frame.pack(fill=tk.X, pady=(0, 10))

        inputs_grid = tk.Frame(params_frame)  # Removido: bg="white"
        inputs_grid.pack(fill=tk.X)

        # CORREÇÃO: Removido bg="white" das Labels
        tk.Label(inputs_grid, text="Latitude Inicial:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lat_inicial = tk.Entry(inputs_grid, width=15)
        # CORREÇÃO: Coordenadas padrão (Jatiúca)
        self.lat_inicial.insert(0, "-9.6582")
        self.lat_inicial.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Inicial:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.lon_inicial = tk.Entry(inputs_grid, width=15)
        self.lon_inicial.insert(0, "-35.7032")
        self.lon_inicial.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(inputs_grid, text="Latitude Final:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lat_final = tk.Entry(inputs_grid, width=15)
        # CORREÇÃO: Coordenadas padrão (Aeroporto)
        self.lat_final.insert(0, "-9.5108")
        self.lat_final.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Final:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lon_final = tk.Entry(inputs_grid, width=15)
        self.lon_final.insert(0, "-35.7899")
        self.lon_final.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(inputs_grid, text="Modo de Viagem:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.modo_viagem = ttk.Combobox(inputs_grid, width=13, state="readonly")
        self.modo_viagem['values'] = ("car", "bike", "pedestrian", "truck")
        self.modo_viagem.current(0)
        self.modo_viagem.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Algoritmo:").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.algoritmo = ttk.Combobox(inputs_grid, width=13, state="readonly")
        self.algoritmo['values'] = ("A*", "Dijkstra")
        self.algoritmo.current(0)
        self.algoritmo.grid(row=2, column=3, padx=5, pady=5)

        btn_frame = tk.Frame(params_frame)  # Removido: bg="white"
        btn_frame.pack(pady=10)

        # CORREÇÃO: Removidas cores bg/fg
        self.btn_encontrar = tk.Button(
            btn_frame,
            text="Encontrar Caminho",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.encontrar_caminho,
            state=tk.DISABLED
        )
        self.btn_encontrar.pack()

        results_container = tk.Frame(main_frame)  # Removido: bg="#f0f0f0"
        results_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.LabelFrame(
            results_container,
            text="3. Visualização do Mapa",
            font=("Arial", 10, "bold"),
            # Removido: bg="white"
            padx=10,
            pady=10
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # CORREÇÃO: Fundo do canvas alterado para melhor visualização (neutro)
        self.canvas = tk.Canvas(left_frame, bg="#e8f4f8", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.add_point_click)

        right_frame = tk.LabelFrame(
            results_container,
            text="4. Resultados e Ações",
            font=("Arial", 10, "bold"),
            # Removido: bg="white"
            padx=10,
            pady=10
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.configure(width=350)
        right_frame.pack_propagate(False)

        info_frame = tk.Frame(right_frame)  # Removido: bg="white"
        info_frame.pack(fill=tk.X, pady=5)

        # CORREÇÃO: Removido bg="white" das Labels
        tk.Label(info_frame, text="Distância Total:", font=("Arial", 9, "bold")).pack(anchor="w")
        # CORREÇÃO: Removido bg="white" e fg="..."
        self.lbl_distancia = tk.Label(info_frame, text="0.0 km", font=("Arial", 11))
        self.lbl_distancia.pack(anchor="w", pady=2)

        tk.Label(info_frame, text="Tempo Estimado:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.lbl_tempo = tk.Label(info_frame, text="0 min", font=("Arial", 11))
        self.lbl_tempo.pack(anchor="w", pady=2)

        tk.Label(info_frame, text="Pontos de Parada:", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.lbl_pontos = tk.Label(info_frame, text="0", font=("Arial", 11))
        self.lbl_pontos.pack(anchor="w", pady=2)

        tk.Label(right_frame, text="Coordenadas (Pontos de Parada):", font=("Arial", 9, "bold")).pack(anchor="w",
                                                                                                      pady=(15, 5))

        coords_frame = tk.Frame(right_frame)  # Removido: bg="white"
        coords_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(coords_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.coords_listbox = tk.Listbox(coords_frame, yscrollcommand=scrollbar.set,
                                         font=("Courier", 9))  # Removido: bg="#f9f9f9"
        self.coords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.coords_listbox.yview)

        control_frame = tk.Frame(right_frame)  # Removido: bg="white"
        control_frame.pack(fill=tk.X, pady=(10, 0))

        # CORREÇÃO: Removidas cores bg/fg
        self.btn_add_point = tk.Button(control_frame, text="Adicionar Ponto (Manual)", command=self.add_point_manual,
                                       font=("Arial", 9), state=tk.DISABLED)
        self.btn_add_point.pack(fill=tk.X, pady=2)

        self.btn_optimize = tk.Button(control_frame, text="Otimizar Rota (Múltiplos Pontos)",
                                      command=self.optimize_route,
                                      font=("Arial", 9), state=tk.DISABLED)
        self.btn_optimize.pack(fill=tk.X, pady=2)

        self.btn_clear = tk.Button(control_frame, text="Limpar Mapa", command=self.clear_map,
                                   font=("Arial", 9), state=tk.DISABLED)
        self.btn_clear.pack(fill=tk.X, pady=2)

    # --- Funções de Mapeamento de Coordenadas ---

    # CORREÇÃO: Bug do "if not self.bbox" (ambiguidade do NumPy)
    def latlon_to_pixel(self, lat, lon):
        """Converte (lat, lon) para (x, y) no canvas baseado no BBox."""
        if self.bbox is None:
            return 0, 0
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        min_lon, min_lat, max_lon, max_lat = self.bbox

        if max_lon == min_lon: max_lon += 0.001
        if max_lat == min_lat: max_lat += 0.001

        x = (lon - min_lon) * w / (max_lon - min_lon)
        y = (max_lat - lat) * h / (max_lat - min_lat)  # Eixo Y invertido
        return int(x), int(y)

    # CORREÇÃO: Bug do "if not self.bbox" (ambiguidade do NumPy)
    def pixel_to_latlon(self, x, y):
        """Converte (x, y) do canvas para (lat, lon) baseado no BBox."""
        if self.bbox is None:
            return 0, 0
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        min_lon, min_lat, max_lon, max_lat = self.bbox

        if w == 0: w = 1
        if h == 0: h = 1

        lon = (x * (max_lon - min_lon) / w) + min_lon
        lat = max_lat - (y * (max_lat - min_lat) / h)
        return lat, lon

    # --- Funções do Backend e Lógica ---

    # CORREÇÃO: Funções de Threading para carregamento seguro
    def start_map_load_thread(self):
        """Inicia o carregamento do mapa em uma thread separada."""
        location = self.location_entry.get()
        if not location:
            messagebox.showerror("Erro", "Por favor, insira uma localização.")
            return

        self.load_status_label.config(text="Carregando...", fg="orange")
        self.btn_load_map.config(state=tk.DISABLED)

        threading.Thread(target=self.load_map_background,
                         args=(location,),
                         daemon=True).start()

    def load_map_background(self, location: str):
        """Lógica de carregamento do mapa (executa na thread de background)."""
        try:
            parser = GraphParser(location)
            graph = parser.build_graph()

            nodes_df, edges_df = ox.graph_to_gdfs(graph.to_undirected())
            bbox = edges_df.total_bounds

            result = (parser, graph, bbox)
            self.root.after(0, self.on_map_load_success, result)

        except Exception as e:
            self.root.after(0, self.on_map_load_failure, e)

    def on_map_load_success(self, result: tuple):
        """Executa na thread PRINCIPAL ao carregar o mapa com sucesso."""
        self.graph_parser, self.graph, self.bbox = result

        self.btn_encontrar.config(state=tk.NORMAL)
        self.btn_add_point.config(state=tk.NORMAL)
        self.btn_optimize.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)
        self.load_status_label.config(text="Mapa Carregado!", fg="green")
        self.btn_load_map.config(state=tk.NORMAL)

    def on_map_load_failure(self, error: Exception):
        """Executa na thread PRINCIPAL se o carregamento falhar."""
        self.load_status_label.config(text="Erro!", fg="red")
        self.btn_load_map.config(state=tk.NORMAL)
        messagebox.showerror("Erro ao Carregar Mapa", f"Não foi possível carregar o mapa: {error}")

    def encontrar_caminho(self):
        """Encontra e desenha o caminho ponto-a-ponto usando A* ou Dijkstra."""
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        try:
            lat1 = float(self.lat_inicial.get())
            lon1 = float(self.lon_inicial.get())
            lat2 = float(self.lat_final.get())
            lon2 = float(self.lon_final.get())

            node1 = self.graph_parser.get_closest_node(lat1, lon1)
            node2 = self.graph_parser.get_closest_node(lat2, lon2)

            algo = self.algoritmo.get()
            if algo == "A*":
                path_nodes, distance_meters = find_path_a_star(self.graph, node1, node2)
            else:  # Dijkstra
                path_nodes, distance_meters = find_path_dijkstra(self.graph, node1, node2)

            if not path_nodes or distance_meters == float('inf'):
                messagebox.showerror("Erro", "Nenhum caminho encontrado entre os pontos.")
                return

            self.clear_map(draw=False)
            self.points = [(lat1, lon1), (lat2, lon2)]

            # CORREÇÃO: Bug do KeyError na otimização
            self.point_nodes[(lat1, lon1)] = node1
            self.point_nodes[(lat2, lon2)] = node2

            self.route_nodes = path_nodes

            self.draw_map()
            self.update_info(distance_km=(distance_meters / 1000.0),
                             num_points=len(self.points))

            messagebox.showinfo("Sucesso", f"Rota calculada com {algo}!\nDistância: {distance_meters / 1000.0:.2f} km")

        except ValueError:
            messagebox.showerror("Erro", "Valores de coordenadas inválidos!")
        except Exception as e:
            messagebox.showerror("Erro no Cálculo", f"Ocorreu um erro: {e}")

    def optimize_route(self):
        """Otimiza uma rota com múltiplos pontos (Heurística Nearest Neighbor)."""
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        if len(self.points) < 2:
            messagebox.showwarning("Aviso", "Adicione pelo menos 2 pontos de parada!")
            return

        self.route_nodes = []
        self.multi_stop_route = []

        unvisited_points = self.points.copy()
        current_point = unvisited_points.pop(0)
        ordered_points = [current_point]

        total_distance_meters = 0

        try:
            while unvisited_points:
                current_node = self.point_nodes[current_point]

                nearest_point = None
                min_dist = float('inf')

                for point in unvisited_points:
                    target_node = self.point_nodes[point]
                    dist = get_shortest_distance_a_star(self.graph, current_node, target_node)

                    if dist < min_dist:
                        min_dist = dist
                        nearest_point = point

                if nearest_point is None or min_dist == float('inf'):
                    messagebox.showwarning("Aviso",
                                           "Não foi possível encontrar caminho para um dos pontos. Rota incompleta.")
                    break

                nearest_node = self.point_nodes[nearest_point]
                path_nodes, path_dist = find_path_a_star(self.graph, current_node, nearest_node)

                if path_nodes:
                    self.multi_stop_route.append(path_nodes)
                    total_distance_meters += path_dist

                current_point = nearest_point
                ordered_points.append(current_point)
                unvisited_points.remove(nearest_point)

            self.points = ordered_points
            self.draw_map()
            self.update_info(distance_km=(total_distance_meters / 1000.0),
                             num_points=len(self.points))
            messagebox.showinfo("Sucesso", "Rota otimizada (Vizinho Mais Próximo)!")

        except Exception as e:
            messagebox.showerror("Erro na Otimização", f"Ocorreu um erro: {e}")

    # --- Funções Auxiliares da UI ---

    def add_point_click(self, event):
        """Adiciona um ponto de parada ao clicar no mapa."""
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        try:
            x, y = event.x, event.y
            lat, lon = self.pixel_to_latlon(x, y)

            node_id = self.graph_parser.get_closest_node(lat, lon)
            self.points.append((lat, lon))
            self.point_nodes[(lat, lon)] = node_id

            self.draw_map()
            self.update_info(num_points=len(self.points))

        except Exception as e:
            messagebox.showerror("Erro ao Adicionar Ponto",
                                 f"Não foi possível adicionar o ponto:\n{e}")

    def add_point_manual(self):
        """Abre um diálogo para adicionar um ponto por Lat/Lon."""
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Ponto")
        dialog.geometry("300x150")
        # Removido: dialog.configure(bg="white")

        tk.Label(dialog, text="Latitude:").pack(pady=5)  # Removido: bg="white"
        lat_entry = tk.Entry(dialog)
        lat_entry.pack()

        tk.Label(dialog, text="Longitude:").pack(pady=5)  # Removido: bg="white"
        lon_entry = tk.Entry(dialog)
        lon_entry.pack()

        def add():
            try:
                lat = float(lat_entry.get())
                lon = float(lon_entry.get())

                node_id = self.graph_parser.get_closest_node(lat, lon)

                self.points.append((lat, lon))
                self.point_nodes[(lat, lon)] = node_id

                self.draw_map()
                self.update_info(num_points=len(self.points))
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Coordenadas inválidas!")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível adicionar o ponto: {e}")

        tk.Button(dialog, text="Adicionar", command=add).pack(pady=10)  # Removido: bg, fg

    # CORREÇÃO: Sempre desenhar a grade
    def draw_map(self):
        """Redesenha o canvas com todos os elementos (rotas e pontos)."""
        self.canvas.delete("all")

        # Sempre desenha a grade de fundo
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        if w > 0 and h > 0:
            for i in range(0, w, 50): self.canvas.create_line(i, 0, i, h, fill="#d0e8f0", width=1)
            for i in range(0, h, 50): self.canvas.create_line(0, i, w, i, fill="#d0e8f0", width=1)

        if self.graph is None:
            return

        if self.route_nodes:
            pixel_path = []
            for node_id in self.route_nodes:
                node_data = self.graph.nodes[node_id]
                lat, lon = node_data['y'], node_data['x']
                pixel_path.append(self.latlon_to_pixel(lat, lon))
            self.canvas.create_line(pixel_path, fill="#0066cc", width=3, arrow=tk.LAST)

        if self.multi_stop_route:
            for path_segment in self.multi_stop_route:
                pixel_path_segment = []
                for node_id in path_segment:
                    node_data = self.graph.nodes[node_id]
                    lat, lon = node_data['y'], node_data['x']
                    pixel_path_segment.append(self.latlon_to_pixel(lat, lon))
                self.canvas.create_line(pixel_path_segment, fill="#ffc107", width=3, arrow=tk.LAST)

        for i, (lat, lon) in enumerate(self.points):
            x, y = self.latlon_to_pixel(lat, lon)
            color = "#ff0000" if i == 0 else "#0066cc"
            if self.multi_stop_route and i == len(self.points) - 1:
                color = "#00ff00"

            self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=color, outline="white", width=2)
            self.canvas.create_text(x, y - 15, text=str(i + 1), font=("Arial", 9, "bold"), fill=color)

    # CORREÇÃO: Bug do "0 min"
    def update_info(self, distance_km=0.0, num_points=0):
        """Atualiza os labels de informação e a lista de coordenadas."""
        self.lbl_distancia.config(text=f"{distance_km:.2f} km")

        velocidades = {"car": 60, "bike": 20, "pedestrian": 5, "truck": 50}
        vel = velocidades.get(self.modo_viagem.get(), 60)
        tempo = (distance_km / vel) * 60 if distance_km > 0 else 0

        # Mudado de ':.0f' para ':.1f' para mostrar uma casa decimal
        self.lbl_tempo.config(text=f"{tempo:.1f} min")

        self.lbl_pontos.config(text=str(num_points))

        self.coords_listbox.delete(0, tk.END)
        for i, (lat, lon) in enumerate(self.points):
            self.coords_listbox.insert(tk.END, f"{i + 1}: ({lat:.4f}, {lon:.4f})")

    def clear_map(self, draw=True):
        """Limpa o estado do mapa e da UI."""
        self.points = []
        self.point_nodes = {}
        self.route_nodes = []
        self.multi_stop_route = []

        if draw:
            self.draw_map()
        self.update_info()


if __name__ == "__main__":
    root = tk.Tk()
    app = RouteOptimizerGUI(root)
    root.mainloop()
