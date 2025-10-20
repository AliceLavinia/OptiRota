import tkinter as tk
from tkinter import ttk, messagebox
import math
import threading
import tkintermapview  # <-- NOVO IMPORT
from typing import Tuple

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

        self.graph_parser = None
        self.graph = None
        self.bbox = None  # (min_lon, min_lat, max_lon, max_lat)
        self.points = []
        self.point_nodes = {}
        self.route_nodes = []
        self.multi_stop_route = []
        self_map_widget = None  # Widget do mapa

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Frame de Carregamento do Mapa ---
        map_load_frame = tk.LabelFrame(
            main_frame,
            text="1. Carregar Mapa (OSM)",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10
        )
        map_load_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(map_load_frame, text="Localização:").pack(side=tk.LEFT, padx=5)
        self.location_entry = tk.Entry(map_load_frame, width=40)
        self.location_entry.insert(0, "Jatiúca, Maceió")
        self.location_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.btn_load_map = tk.Button(
            map_load_frame,
            text="Carregar Mapa",
            font=("Arial", 10, "bold"),
            cursor="hand2",
            command=self.start_map_load_thread
        )
        self.btn_load_map.pack(side=tk.LEFT, padx=10)

        self.load_status_label = tk.Label(map_load_frame, text="")
        self.load_status_label.pack(side=tk.LEFT, padx=5)
        # --- Fim do Frame de Carregamento ---

        params_frame = tk.LabelFrame(
            main_frame,
            text="2. Parâmetros de Busca",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=15
        )
        params_frame.pack(fill=tk.X, pady=(0, 10))

        inputs_grid = tk.Frame(params_frame)
        inputs_grid.pack(fill=tk.X)

        tk.Label(inputs_grid, text="Latitude Inicial:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lat_inicial = tk.Entry(inputs_grid, width=15)
        self.lat_inicial.insert(0, "-9.6582")  # Jatiúca
        self.lat_inicial.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Inicial:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.lon_inicial = tk.Entry(inputs_grid, width=15)
        self.lon_inicial.insert(0, "-35.7032")  # Jatiúca
        self.lon_inicial.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(inputs_grid, text="Latitude Final:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lat_final = tk.Entry(inputs_grid, width=15)
        self.lat_final.insert(0, "-9.5108")  # Aeroporto
        self.lat_final.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Final:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lon_final = tk.Entry(inputs_grid, width=15)
        self.lon_final.insert(0, "-35.7899")  # Aeroporto
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

        btn_frame = tk.Frame(params_frame)
        btn_frame.pack(pady=10)

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

        results_container = tk.Frame(main_frame)
        results_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.LabelFrame(
            results_container,
            text="3. Visualização do Mapa",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # --- SUBSTITUIÇÃO DO CANVAS ---
        # self.canvas = tk.Canvas(...) foi removido.
        self.map_widget = tkintermapview.TkinterMapView(left_frame, width=800, height=600, corner_radius=0)
        self.map_widget.pack(fill=tk.BOTH, expand=True)
        # Seta um tile server (OpenStreetMap)
        self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")
        # Adiciona comando de clique
        self.map_widget.add_left_click_map_command(self.on_map_click)
        # --- FIM DA SUBSTITUIÇÃO ---

        right_frame = tk.LabelFrame(
            results_container,
            text="4. Resultados e Ações",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.configure(width=350)
        right_frame.pack_propagate(False)

        info_frame = tk.Frame(right_frame)
        info_frame.pack(fill=tk.X, pady=5)

        tk.Label(info_frame, text="Distância Total:", font=("Arial", 9, "bold")).pack(anchor="w")
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

        coords_frame = tk.Frame(right_frame)
        coords_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(coords_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.coords_listbox = tk.Listbox(coords_frame, yscrollcommand=scrollbar.set, font=("Courier", 9))
        self.coords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.coords_listbox.yview)

        control_frame = tk.Frame(right_frame)
        control_frame.pack(fill=tk.X, pady=(10, 0))

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

    # As funções latlon_to_pixel e pixel_to_latlon foram REMOVIDAS
    # pois o tkintermapview não precisa delas.

    # --- Funções do Backend e Lógica ---

    def start_map_load_thread(self):
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
        self.graph_parser, self.graph, self.bbox = result

        self.btn_encontrar.config(state=tk.NORMAL)
        self.btn_add_point.config(state=tk.NORMAL)
        self.btn_optimize.config(state=tk.NORMAL)
        self.btn_clear.config(state=tk.NORMAL)
        self.load_status_label.config(text="Mapa Carregado!", fg="green")
        self.btn_load_map.config(state=tk.NORMAL)

        # --- ATUALIZAÇÃO DO MAPA ---
        min_lon, min_lat, max_lon, max_lat = self.bbox

        # CORREÇÃO: A biblioteca espera (Top-Left) e (Bottom-Right)
        top_left = (max_lat, min_lon)
        bottom_right = (min_lat, max_lon)

        self.map_widget.fit_bounding_box(top_left, bottom_right)
        # --- FIM DA ATUALIZAÇÃO ---

    def on_map_load_failure(self, error: Exception):
        self.load_status_label.config(text="Erro!", fg="red")
        self.btn_load_map.config(state=tk.NORMAL)
        messagebox.showerror("Erro ao Carregar Mapa", f"Não foi possível carregar o mapa: {error}")

    def encontrar_caminho(self):
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
            else:
                path_nodes, distance_meters = find_path_dijkstra(self.graph, node1, node2)

            if not path_nodes or distance_meters == float('inf'):
                messagebox.showerror("Erro", "Nenhum caminho encontrado entre os pontos.")
                return

            self.clear_map(draw=False)
            self.points = [(lat1, lon1), (lat2, lon2)]
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
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        if len(self.points) < 2:
            messagebox.showwarning("Aviso", "Adicione pelo menos 2 pontos de parada!")
            return

        self.route_nodes = []
        self.multi_stop_route = []

        # Copia os pontos para não bagunçar a ordem original do usuário
        unvisited_points = self.points.copy()
        current_point = unvisited_points.pop(0)
        ordered_points = [current_point]  # A rota otimizada começa no primeiro ponto

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

            # NOTE: self.points não é reordenado, para manter a ordem do usuário.
            # Apenas desenhamos a rota otimizada.
            self.draw_map()
            self.update_info(distance_km=(total_distance_meters / 1000.0),
                             num_points=len(self.points))
            messagebox.showinfo("Sucesso", "Rota otimizada (Vizinho Mais Próximo)!")

        except Exception as e:
            messagebox.showerror("Erro na Otimização", f"Ocorreu um erro: {e}")

    # --- Funções Auxiliares da UI ---

    # ESTA É A NOVA FUNÇÃO DE CLIQUE
    def on_map_click(self, coords: Tuple[float, float]):
        """Adiciona um ponto de parada ao clicar no mapa."""
        if self.graph is None:
            messagebox.showwarning("Aviso", "Carregue um mapa primeiro!")
            return

        try:
            lat, lon = coords[0], coords[1]

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

        tk.Label(dialog, text="Latitude:").pack(pady=5)
        lat_entry = tk.Entry(dialog)
        lat_entry.pack()

        tk.Label(dialog, text="Longitude:").pack(pady=5)
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

        tk.Button(dialog, text="Adicionar", command=add).pack(pady=10)

    # ESTA FUNÇÃO FOI TOTALMENTE REESCRITA
    def draw_map(self):
        """Redesenha o widget do mapa com todos os elementos (rotas e pontos)."""

        # Limpa marcadores e rotas antigas
        self.map_widget.delete_all_marker()
        self.map_widget.delete_all_path()

        if self.graph is None:
            return

        # 1. Desenha o caminho ponto-a-ponto (se existir)
        if self.route_nodes:
            # Converte lista de nós em lista de (lat, lon)
            path_coordinates = []
            for node_id in self.route_nodes:
                node_data = self.graph.nodes[node_id]
                path_coordinates.append((node_data['y'], node_data['x']))

            # Desenha o caminho no mapa
            if path_coordinates:
                self.map_widget.set_path(path_coordinates, color="#0066cc", width=3)

        # 2. Desenha a rota multi-pontos (se existir)
        if self.multi_stop_route:
            for path_segment in self.multi_stop_route:
                # Converte lista de nós em lista de (lat, lon)
                segment_coordinates = []
                for node_id in path_segment:
                    node_data = self.graph.nodes[node_id]
                    segment_coordinates.append((node_data['y'], node_data['x']))

                # Desenha o segmento no mapa
                if segment_coordinates:
                    self.map_widget.set_path(segment_coordinates, color="#ffc107", width=3)

        # 3. Desenha os pontos de parada (self.points)
        for i, (lat, lon) in enumerate(self.points):
            self.map_widget.set_marker(lat, lon, text=f"{i + 1}")

    def update_info(self, distance_km=0.0, num_points=0):
        """Atualiza os labels de informação e a lista de coordenadas."""
        self.lbl_distancia.config(text=f"{distance_km:.2f} km")

        velocidades = {"car": 60, "bike": 20, "pedestrian": 5, "truck": 50}

        # --- CORREÇÃO AQUI ---
        # Trocado 'velocities.get' por 'velocidades.get'
        vel = velocidades.get(self.modo_viagem.get(), 60)
        # --- FIM DA CORREÇÃO ---

        tempo = (distance_km / vel) * 60 if distance_km > 0 else 0

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
        self.update_info()  # Reseta os labels para 0


if __name__ == "__main__":
    root = tk.Tk()
    app = RouteOptimizerGUI(root)
    root.mainloop()
