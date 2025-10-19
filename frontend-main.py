import tkinter as tk
from tkinter import ttk, messagebox
import math


class RouteOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("OptiRota - Otimizador de Rotas")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.points = []
        self.route = []

        self.create_widgets()

    def create_widgets(self):
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        params_frame = tk.LabelFrame(
            main_frame,
            text="1. Parâmetros de Busca",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=15,
            pady=15
        )
        params_frame.pack(fill=tk.X, pady=(0, 10))

        inputs_grid = tk.Frame(params_frame, bg="white")
        inputs_grid.pack(fill=tk.X)

        tk.Label(inputs_grid, text="Latitude Inicial:", bg="white").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.lat_inicial = tk.Entry(inputs_grid, width=15)
        self.lat_inicial.insert(0, "-23.55")
        self.lat_inicial.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Inicial:", bg="white").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.lon_inicial = tk.Entry(inputs_grid, width=15)
        self.lon_inicial.insert(0, "-46.63")
        self.lon_inicial.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(inputs_grid, text="Latitude Final:", bg="white").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.lat_final = tk.Entry(inputs_grid, width=15)
        self.lat_final.insert(0, "-23.554")
        self.lat_final.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Longitude Final:", bg="white").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.lon_final = tk.Entry(inputs_grid, width=15)
        self.lon_final.insert(0, "-46.634")
        self.lon_final.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(inputs_grid, text="Modo de Viagem:", bg="white").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.modo_viagem = ttk.Combobox(inputs_grid, width=13, state="readonly")
        self.modo_viagem['values'] = ("car", "bike", "pedestrian", "truck")
        self.modo_viagem.current(0)
        self.modo_viagem.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(inputs_grid, text="Algoritmo:", bg="white").grid(row=2, column=2, sticky="w", padx=5, pady=5)
        self.algoritmo = ttk.Combobox(inputs_grid, width=13, state="readonly")
        self.algoritmo['values'] = ("Dijkstra", "A*", "Bellman-Ford", "Floyd-Warshall")
        self.algoritmo.current(0)
        self.algoritmo.grid(row=2, column=3, padx=5, pady=5)

        btn_frame = tk.Frame(params_frame, bg="white")
        btn_frame.pack(pady=10)

        self.btn_encontrar = tk.Button(
            btn_frame,
            text="Encontrar Caminho",
            bg="#0066cc",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=8,
            cursor="hand2",
            command=self.encontrar_caminho
        )
        self.btn_encontrar.pack()

        results_container = tk.Frame(main_frame, bg="#f0f0f0")
        results_container.pack(fill=tk.BOTH, expand=True)

        left_frame = tk.LabelFrame(
            results_container,
            text="2. Visualização do Mapa",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        self.canvas = tk.Canvas(left_frame, bg="#e8f4f8", highlightthickness=1, highlightbackground="#ccc")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.add_point_click)

        right_frame = tk.LabelFrame(
            results_container,
            text="3. Resultados",
            font=("Arial", 10, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(5, 0))
        right_frame.configure(width=350)
        right_frame.pack_propagate(False)

        info_frame = tk.Frame(right_frame, bg="white")
        info_frame.pack(fill=tk.X, pady=5)

        tk.Label(info_frame, text="Distância Total:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w")
        self.lbl_distancia = tk.Label(info_frame, text="0.0 km", bg="white", fg="#0066cc", font=("Arial", 11))
        self.lbl_distancia.pack(anchor="w", pady=2)

        tk.Label(info_frame, text="Tempo Estimado:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.lbl_tempo = tk.Label(info_frame, text="0 min", bg="white", fg="#0066cc", font=("Arial", 11))
        self.lbl_tempo.pack(anchor="w", pady=2)

        tk.Label(info_frame, text="Pontos na Rota:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(10, 0))
        self.lbl_pontos = tk.Label(info_frame, text="0", bg="white", fg="#0066cc", font=("Arial", 11))
        self.lbl_pontos.pack(anchor="w", pady=2)

        tk.Label(right_frame, text="Coordenadas:", bg="white", font=("Arial", 9, "bold")).pack(anchor="w", pady=(15, 5))

        coords_frame = tk.Frame(right_frame, bg="white")
        coords_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(coords_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.coords_listbox = tk.Listbox(coords_frame, yscrollcommand=scrollbar.set, font=("Courier", 9), bg="#f9f9f9")
        self.coords_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.coords_listbox.yview)

        control_frame = tk.Frame(right_frame, bg="white")
        control_frame.pack(fill=tk.X, pady=(10, 0))

        tk.Button(control_frame, text="Adicionar Ponto", command=self.add_point_manual, bg="#28a745", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Limpar Mapa", command=self.clear_map, bg="#dc3545", fg="white", font=("Arial", 9)).pack(fill=tk.X, pady=2)
        tk.Button(control_frame, text="Otimizar Rota", command=self.optimize_route, bg="#ffc107", fg="black", font=("Arial", 9)).pack(fill=tk.X, pady=2)

    def add_point_click(self, event):
        x, y = event.x, event.y
        self.points.append((x, y))
        self.draw_points()
        self.update_info()

    def add_point_manual(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Adicionar Ponto")
        dialog.geometry("300x150")
        dialog.configure(bg="white")

        tk.Label(dialog, text="Latitude:", bg="white").pack(pady=5)
        lat_entry = tk.Entry(dialog)
        lat_entry.pack()

        tk.Label(dialog, text="Longitude:", bg="white").pack(pady=5)
        lon_entry = tk.Entry(dialog)
        lon_entry.pack()

        def add():
            try:
                lat = float(lat_entry.get())
                lon = float(lon_entry.get())
                x = (lon + 180) * self.canvas.winfo_width() / 360
                y = (90 - lat) * self.canvas.winfo_height() / 180
                self.points.append((x, y))
                self.coords_listbox.insert(tk.END, f"({lat:.4f}, {lon:.4f})")
                self.draw_points()
                self.update_info()
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Erro", "Coordenadas inválidas!")

        tk.Button(dialog, text="Adicionar", command=add, bg="#28a745", fg="white").pack(pady=10)

    def draw_points(self):
        self.canvas.delete("all")
        w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        for i in range(0, w, 50):
            self.canvas.create_line(i, 0, i, h, fill="#d0e8f0", width=1)
        for i in range(0, h, 50):
            self.canvas.create_line(0, i, w, i, fill="#d0e8f0", width=1)
        if len(self.route) > 1:
            for i in range(len(self.route) - 1):
                x1, y1 = self.route[i]
                x2, y2 = self.route[i + 1]
                self.canvas.create_line(x1, y1, x2, y2, fill="#0066cc", width=3, arrow=tk.LAST)
        for i, (x, y) in enumerate(self.points):
            color = "#ff0000" if i == 0 else "#00ff00" if i == len(self.points) - 1 else "#0066cc"
            self.canvas.create_oval(x - 6, y - 6, x + 6, y + 6, fill=color, outline="white", width=2)
            self.canvas.create_text(x, y - 15, text=str(i + 1), font=("Arial", 9, "bold"), fill=color)

    def calculate_distance(self):
        if len(self.route) < 2:
            return 0
        total = 0
        for i in range(len(self.route) - 1):
            x1, y1 = self.route[i]
            x2, y2 = self.route[i + 1]
            total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        return total * 0.1

    def update_info(self):
        dist = self.calculate_distance()
        self.lbl_distancia.config(text=f"{dist:.2f} km")
        velocidades = {"car": 60, "bike": 20, "pedestrian": 5, "truck": 50}
        vel = velocidades.get(self.modo_viagem.get(), 60)
        tempo = (dist / vel) * 60 if dist > 0 else 0
        self.lbl_tempo.config(text=f"{tempo:.0f} min")
        self.lbl_pontos.config(text=str(len(self.points)))

    def encontrar_caminho(self):
        try:
            lat1 = float(self.lat_inicial.get())
            lon1 = float(self.lon_inicial.get())
            lat2 = float(self.lat_final.get())
            lon2 = float(self.lon_final.get())

            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
            x1 = (lon1 + 180) * w / 360
            y1 = (90 - lat1) * h / 180
            x2 = (lon2 + 180) * w / 360
            y2 = (90 - lat2) * h / 180

            self.points = [(x1, y1), (x2, y2)]
            self.route = self.points.copy()
            self.coords_listbox.delete(0, tk.END)
            self.coords_listbox.insert(tk.END, f"Início: ({lat1:.4f}, {lon1:.4f})")
            self.coords_listbox.insert(tk.END, f"Fim: ({lat2:.4f}, {lon2:.4f})")

            self.draw_points()
            self.update_info()
            messagebox.showinfo("Sucesso", f"Rota calculada usando {self.algoritmo.get()}!")

        except ValueError:
            messagebox.showerror("Erro", "Coordenadas inválidas!")

    def optimize_route(self):
        if len(self.points) < 2:
            messagebox.showwarning("Aviso", "Adicione pelo menos 2 pontos!")
            return
        unvisited = self.points[1:]
        route = [self.points[0]]
        current = self.points[0]
        while unvisited:
            nearest = min(unvisited, key=lambda p: math.sqrt((p[0] - current[0]) ** 2 + (p[1] - current[1]) ** 2))
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        self.route = route
        self.draw_points()
        self.update_info()
        messagebox.showinfo("Sucesso", "Rota otimizada!")

    def clear_map(self):
        self.points = []
        self.route = []
        self.coords_listbox.delete(0, tk.END)
        self.draw_points()
        self.update_info()


if __name__ == "__main__":
    root = tk.Tk()
    app = RouteOptimizerGUI(root)
    root.mainloop()
