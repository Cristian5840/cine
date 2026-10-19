import os
import tkinter as tk
from tkinter import ttk, messagebox

ARCHIVO = "asientos.txt"
FILAS = ["A", "B", "C", "D"]
ASIENTOS_POR_FILA = 5  # 4 filas x 5 asientos = 20 asientos

COLOR_LIBRE = "#4caf50"
COLOR_OCUPADO = "#e53935"


def todos_los_asientos():
    return [f"{fila}{n}" for fila in FILAS for n in range(1, ASIENTOS_POR_FILA + 1)]


def guardar_asientos(estado):
    """Guarda el estado de todos los asientos (uno por línea: asiento <tab> estado)."""
    with open(ARCHIVO, "w", encoding="utf-8") as archivo:
        for asiento in todos_los_asientos():
            texto = "ocupado" if estado[asiento] else "libre"
            archivo.write(f"{asiento}\t{texto}\n")


def leer_asientos():
    """Devuelve un dict {asiento: True si está ocupado}. Si no hay archivo, todo libre."""
    estado = {asiento: False for asiento in todos_los_asientos()}
    if not os.path.exists(ARCHIVO):
        return estado
    with open(ARCHIVO, "r", encoding="utf-8") as archivo:
        for linea in archivo:
            partes = [p.strip() for p in linea.strip().split("\t")]
            if len(partes) == 2 and partes[0] in estado:
                estado[partes[0]] = partes[1] == "ocupado"
    return estado


class AppCine(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Ocupación de asientos - Cine")
        self.geometry("560x520")
        self.minsize(480, 460)

        try:
            self.estado = leer_asientos()
        except OSError as error:
            messagebox.showerror("Error", f"No se pudo leer el archivo: {error}")
            self.estado = {a: False for a in todos_los_asientos()}

        self.etiquetas = {}
        self._crear_pantalla()
        self._crear_sala()
        self._crear_resumen()
        self._crear_botones()
        self._crear_barra_estado()
        self.refrescar()

    # ---------- Interfaz ----------
    def _crear_pantalla(self):
        pantalla = tk.Label(self, text="PANTALLA", bg="#333333", fg="white", font=("Arial", 12, "bold"), pady=6)
        pantalla.pack(fill="x", padx=40, pady=(15, 10))

    def _crear_sala(self):
        marco = ttk.LabelFrame(self, text="Sala (clic en un asiento para cambiar su estado)", padding=10)
        marco.pack(fill="both", expand=True, padx=10, pady=5)

        grilla = ttk.Frame(marco)
        grilla.pack(expand=True)

        for i, fila in enumerate(FILAS):
            ttk.Label(grilla, text=fila, font=("Arial", 11, "bold")).grid(row=i, column=0, padx=8)
            for n in range(1, ASIENTOS_POR_FILA + 1):
                asiento = f"{fila}{n}"
                etiqueta = tk.Label(
                    grilla, text=asiento, width=6, height=2, fg="white",
                    font=("Arial", 10, "bold"), relief="raised", bd=3, cursor="hand2",
                )
                etiqueta.grid(row=i, column=n, padx=4, pady=4)
                etiqueta.bind("<Button-1>", lambda e, a=asiento: self.alternar(a))
                self.etiquetas[asiento] = etiqueta

        leyenda = ttk.Frame(marco)
        leyenda.pack(pady=(10, 0))
        tk.Label(leyenda, text="  ", bg=COLOR_LIBRE).pack(side="left", padx=(0, 4))
        ttk.Label(leyenda, text="Libre").pack(side="left", padx=(0, 15))
        tk.Label(leyenda, text="  ", bg=COLOR_OCUPADO).pack(side="left", padx=(0, 4))
        ttk.Label(leyenda, text="Ocupado").pack(side="left")

    def _crear_resumen(self):
        marco = ttk.LabelFrame(self, text="Resumen", padding=8)
        marco.pack(fill="x", padx=10, pady=5)
        self.var_libres = tk.StringVar()
        self.var_ocupados = tk.StringVar()
        self.var_porcentaje = tk.StringVar()
        ttk.Label(marco, textvariable=self.var_libres).pack(side="left", expand=True)
        ttk.Label(marco, textvariable=self.var_ocupados).pack(side="left", expand=True)
        ttk.Label(marco, textvariable=self.var_porcentaje).pack(side="left", expand=True)

    def _crear_botones(self):
        botones = ttk.Frame(self)
        botones.pack(pady=5)
        ttk.Button(botones, text="Liberar todos", command=self.liberar_todos).pack(side="left", padx=5)
        ttk.Button(botones, text="Ocupar todos", command=self.ocupar_todos).pack(side="left", padx=5)
        ttk.Button(botones, text="Salir", command=self.destroy).pack(side="left", padx=5)

    def _crear_barra_estado(self):
        self.var_estado = tk.StringVar(value="Listo")
        ttk.Label(self, textvariable=self.var_estado, relief="sunken", anchor="w").pack(
            fill="x", side="bottom"
        )

    # ---------- Lógica ----------
    def alternar(self, asiento):
        self.estado[asiento] = not self.estado[asiento]
        if self._guardar():
            texto = "ocupado" if self.estado[asiento] else "libre"
            self.var_estado.set(f"Asiento {asiento} ahora está {texto}.")
        self.refrescar()

    def liberar_todos(self):
        if messagebox.askyesno("Confirmar", "¿Liberar todos los asientos?"):
            self.estado = {a: False for a in todos_los_asientos()}
            self._guardar()
            self.var_estado.set("Todos los asientos fueron liberados.")
            self.refrescar()

    def ocupar_todos(self):
        if messagebox.askyesno("Confirmar", "¿Marcar todos los asientos como ocupados?"):
            self.estado = {a: True for a in todos_los_asientos()}
            self._guardar()
            self.var_estado.set("Todos los asientos fueron marcados como ocupados.")
            self.refrescar()

    def _guardar(self):
        try:
            guardar_asientos(self.estado)
            return True
        except PermissionError:
            messagebox.showerror("Error", "Error de los permisos.")
        except OSError as error:
            messagebox.showerror("Error", f"Problemas con el archivo usando el SO: {error}")
        return False

    def refrescar(self):
        for asiento, etiqueta in self.etiquetas.items():
            etiqueta.config(bg=COLOR_OCUPADO if self.estado[asiento] else COLOR_LIBRE)
        ocupados = sum(self.estado.values())
        total = len(self.estado)
        self.var_libres.set(f"Libres: {total - ocupados}")
        self.var_ocupados.set(f"Ocupados: {ocupados}")
        self.var_porcentaje.set(f"Ocupación: {ocupados / total * 100:.0f}%")


if __name__ == "__main__":
    AppCine().mainloop()