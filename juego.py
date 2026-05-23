#!/usr/bin/env python3
"""
Juego de Dominó - Python con Tkinter
Modos: Humano vs Máquina, Máquina vs Máquina, Humano+Máquina vs Máquina+Máquina
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
from typing import Optional


# ─── Colores y estilos ───────────────────────────────────────────
BG        = "#1a1a2e"
PANEL     = "#16213e"
ACCENT    = "#e94560"
GOLD      = "#f5a623"
GREEN     = "#27ae60"
TILE_BG   = "#fdf6e3"
TILE_SEL  = "#ffe08a"
TEXT_DARK = "#1a1a2e"
TEXT_LITE = "#ecf0f1"
BORDER    = "#0f3460"


# ─── Clase Ficha ────────────────────────────────────────────────
class Ficha:
    def __init__(self, a: int, b: int):
        self.a = a
        self.b = b


    def es_doble(self):
        return self.a == self.b

    def voltear(self):
        self.a, self.b = self.b, self.a

    def puntos(self):
        return self.a + self.b

    def __repr__(self):
        return f"[{self.a}|{self.b}]"

    def __eq__(self, other):
        return isinstance(other, Ficha) and {self.a, self.b} == {other.a, other.b}


# ─── Lógica del Juego ───────────────────────────────────────────
class JuegoDomino:
    def __init__(self, modo: str, nombres: list, nivel: str = 'normal'):
        """
        modo: '1v1', '2v2', 'mvm'
        nombres: lista de nombres por jugador
        """
        self.modo = modo
        self.nombres = nombres
        self.num_jugadores = 4 if modo == '2v2' else 2
        self.manos = [[] for _ in range(self.num_jugadores)]
        self.tablero: list[Ficha] = []
        self.extremo_izq: Optional[int] = None
        self.extremo_der: Optional[int] = None
        self.turno = 0
        self.pasa_consecutivo = 0
        self.ganador = None
        self.log: list[str] = []
        self.nivel = nivel  # 'facil' | 'normal' | 'dificil'
        self._repartir()

    def _repartir(self):
        fichas = [Ficha(i, j) for i in range(7) for j in range(i, 7)]
        random.shuffle(fichas)
        por_jugador = 7 if self.num_jugadores == 2 else 7
        for i in range(self.num_jugadores):
            self.manos[i] = fichas[i*por_jugador:(i+1)*por_jugador]
        # primer turno: quien tenga el [6|6]
        for idx, mano in enumerate(self.manos):
            for f in mano:
                if f.a == 6 and f.b == 6:
                    self.turno = idx
                    return

    def fichas_jugables(self, jugador: int) -> list[Ficha]:
        if not self.tablero:
            return self.manos[jugador]
        jugables = []
        for f in self.manos[jugador]:
            if f.a == self.extremo_izq or f.b == self.extremo_izq:
                jugables.append(f)
            elif f.a == self.extremo_der or f.b == self.extremo_der:
                jugables.append(f)
        return jugables

    def jugar_ficha(self, jugador: int, ficha: Ficha, lado: str = 'auto') -> bool:
        """lado: 'izq', 'der', 'auto'"""
        if ficha not in self.manos[jugador]:
            return False

        if not self.tablero:
            self.tablero.append(ficha)
            self.extremo_izq = ficha.a
            self.extremo_der = ficha.b
            self.manos[jugador].remove(ficha)
            self.log.append(f"{self.nombres[jugador]} juega {ficha}")
            self._siguiente_turno()
            return True

        # intentar colocar
        colocada = False
        if lado == 'izq' or lado == 'auto':
            if ficha.b == self.extremo_izq:
                self.tablero.insert(0, ficha)
                self.extremo_izq = ficha.a
                colocada = True
            elif ficha.a == self.extremo_izq:
                ficha.voltear()
                self.tablero.insert(0, ficha)
                self.extremo_izq = ficha.a
                colocada = True

        if not colocada and (lado == 'der' or lado == 'auto'):
            if ficha.a == self.extremo_der:
                self.tablero.append(ficha)
                self.extremo_der = ficha.b
                colocada = True
            elif ficha.b == self.extremo_der:
                ficha.voltear()
                self.tablero.append(ficha)
                self.extremo_der = ficha.b
                colocada = True

        if colocada:
            self.manos[jugador].remove(ficha)
            self.log.append(f"{self.nombres[jugador]} juega {ficha}")
            self.pasa_consecutivo = 0
            if not self.manos[jugador]:
                self.ganador = jugador
            else:
                self._siguiente_turno()
        return colocada

    def pasar(self, jugador: int):
        self.pasa_consecutivo += 1
        self.log.append(f"{self.nombres[jugador]} pasa")
        if self.pasa_consecutivo >= self.num_jugadores:
            # todos pasaron → tranca
            self._resolver_tranca()
        else:
            self._siguiente_turno()

    def _siguiente_turno(self):
        self.turno = (self.turno + 1) % self.num_jugadores

    def _resolver_tranca(self):
        # gana quien tenga menos puntos
        puntos = [sum(f.puntos() for f in mano) for mano in self.manos]
        self.ganador = puntos.index(min(puntos))
        self.log.append(f"¡Tranca! Gana {self.nombres[self.ganador]} con {puntos[self.ganador]} pts")

    def ia_jugar(self, jugador: int) -> bool:
        """IA ajustable por nivel:
        - 'facil': juega aleatoriamente
        - 'normal': estrategia previa (dobles y mayor puntaje)
        - 'dificil': intenta minimizar opciones del siguiente rival
        """
        jugables = self.fichas_jugables(jugador)
        if not jugables:
            self.pasar(jugador)
            return False

        nivel = getattr(self, 'nivel', 'normal')
        if nivel == 'facil':
            ficha = random.choice(jugables)
            self.jugar_ficha(jugador, ficha, 'auto')
            return True

        if nivel == 'normal':
            jugables.sort(key=lambda f: (f.es_doble(), f.puntos()), reverse=True)
            ficha = jugables[0]
            self.jugar_ficha(jugador, ficha, 'auto')
            return True

        # dificil: minimizar opciones del siguiente jugador (heurística simple)
        opponent = (jugador + 1) % self.num_jugadores
        best_f = None
        best_score = None
        best_tie = None
        for f in jugables:
            possible_exts = []
            if not self.tablero:
                possible_exts.append((f.a, f.b))
            else:
                # izquierda
                if f.b == self.extremo_izq:
                    possible_exts.append((f.a, self.extremo_der))
                elif f.a == self.extremo_izq:
                    possible_exts.append((f.b, self.extremo_der))
                # derecha
                if f.a == self.extremo_der:
                    possible_exts.append((self.extremo_izq, f.b))
                elif f.b == self.extremo_der:
                    possible_exts.append((self.extremo_izq, f.a))

            # para cada posible extremo calcular cuántas fichas del rival encajarían
            score = None
            for (nl, nr) in possible_exts:
                cnt = 0
                for of in self.manos[opponent]:
                    if of.a == nl or of.b == nl or of.a == nr or of.b == nr:
                        cnt += 1
                if score is None or cnt < score:
                    score = cnt

            # si no hubo colocación posible (debería no pasar), asignar gran score
            if score is None:
                score = 999

            # elegir ficha con menor score; en empate preferir dobles y mayor puntaje
            tie_key = (not f.es_doble(), -f.puntos())
            if best_score is None or score < best_score or (score == best_score and tie_key < best_tie):
                best_score = score
                best_f = f
                best_tie = tie_key

        if best_f:
            self.jugar_ficha(jugador, best_f, 'auto')
            return True

        # fallback
        jugables.sort(key=lambda f: (f.es_doble(), f.puntos()), reverse=True)
        ficha = jugables[0]
        self.jugar_ficha(jugador, ficha, 'auto')
        return True

    def es_turno_ia(self) -> bool:
        """¿El turno actual es de la IA?"""
        if self.modo == 'mvm':
            return True
        if self.modo == '1v1':
            return self.turno == 1  # jugador 0 = humano, 1 = IA
        if self.modo == '2v2':
            # modo Tú + Máquina vs 2 Máquinas: jugador 0 = humano, 1-3 = IA
            return self.turno in (1, 2, 3)
        return False


# ─── Interfaz Gráfica ────────────────────────────────────────────
class DominoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🁣 DOMINÓ SOLO PRO")
        self.configure(bg=BG)
        self.resizable(True, True)
        self.geometry("1100x750")
        self.juego: Optional[JuegoDomino] = None
        self.ficha_sel: Optional[Ficha] = None
        self.nivel_var = tk.StringVar(value='normal')
        self._mostrar_menu()

    # ── MENÚ ────────────────────────────────────────────────────
    def _mostrar_menu(self):
        self._limpiar()
        frame = tk.Frame(self, bg=BG)
        frame.place(relx=.5, rely=.5, anchor='center')

        tk.Label(frame, text="DOMINÓ SOLO PRO", font=("Georgia", 52, "bold"),
                 fg=ACCENT, bg=BG).pack(pady=(0, 4))
        tk.Label(frame, text="Elige tu modo de juego", font=("Georgia", 16),
                 fg=GOLD, bg=BG).pack(pady=(0, 30))

        modos = [
            ("🧑  vs  🤖", "Humano vs Máquina",   "1v1"),
            ("🤖  vs  🤖", "Máquina vs Máquina",   "mvm"),
            ("🧑🤖 vs 🤖🤖", "Tú + Máquina vs 2 Máquinas", "2v2"),
        ]
        for emoji, desc, key in modos:
            btn_f = tk.Frame(frame, bg=PANEL, padx=20, pady=12,
                             relief='flat', bd=0)
            btn_f.pack(fill='x', pady=6)
            tk.Label(btn_f, text=emoji, font=("", 22), bg=PANEL,
                     fg=TEXT_LITE).pack(side='left', padx=(0, 14))
            info = tk.Frame(btn_f, bg=PANEL)
            info.pack(side='left', expand=True, fill='x')
            tk.Label(info, text=desc, font=("Georgia", 13, "bold"),
                     bg=PANEL, fg=TEXT_LITE, anchor='w').pack(anchor='w')
            tk.Button(btn_f, text="JUGAR →", font=("Georgia", 11, "bold"),
                      bg=ACCENT, fg='white', relief='flat', cursor='hand2',
                      padx=12, pady=4,
                      command=lambda m=key: self._iniciar(m)).pack(side='right')

        # Selección de nivel
        nivel_frame = tk.Frame(frame, bg=BG)
        nivel_frame.pack(pady=(0, 12))
        tk.Label(nivel_frame, text="Nivel:", font=("Georgia", 11),
                 fg=TEXT_LITE, bg=BG).pack(side='left', padx=(0, 8))
        niveles = [("Fácil", 'facil'), ("Normal", 'normal'), ("Difícil", 'dificil')]
        for label, val in niveles:
            tk.Radiobutton(nivel_frame, text=label, variable=self.nivel_var,
                           value=val, bg=BG, fg=TEXT_LITE, selectcolor=PANEL,
                           activebackground=BG, font=("Georgia", 10)).pack(side='left', padx=6)
        tk.Label(frame, text="© 2024 Dominó Python", font=("", 9),
                 fg="#555", bg=BG).pack(pady=(30, 0))

    def _iniciar(self, modo: str):
        if modo == '1v1':
            nombres = ["Tú", "Máquina"]
        elif modo == 'mvm':
            nombres = ["IA-1", "IA-2"]
        else:
            nombres = ["Tú", "IA-Aliado", "IA-Rival1", "IA-Rival2"]

        self.juego = JuegoDomino(modo, nombres, nivel=self.nivel_var.get())
        self.ficha_sel = None
        self._construir_ui()
        self._actualizar_ui()

        if modo == 'mvm':
            self._ciclo_ia()
        elif self.juego.es_turno_ia():
            self.after(800, self._paso_ia)

    # ── UI PRINCIPAL ─────────────────────────────────────────────
    def _construir_ui(self):
        self._limpiar()

        # Barra superior
        top = tk.Frame(self, bg=BORDER, height=50)
        top.pack(fill='x')
        tk.Label(top, text="🁣 DOMINÓ", font=("Georgia", 18, "bold"),
                 fg=ACCENT, bg=BORDER).pack(side='left', padx=16, pady=8)
        tk.Button(top, text="⟵ Menú", font=("Georgia", 11),
                  bg=PANEL, fg=TEXT_LITE, relief='flat', cursor='hand2',
                  padx=10, command=self._mostrar_menu).pack(side='right', padx=10, pady=8)

        # Contenedor principal
        main = tk.Frame(self, bg=BG)
        main.pack(fill='both', expand=True, padx=10, pady=6)

        # Panel izquierdo: tablero + manos ocultas
        left = tk.Frame(main, bg=BG)
        left.pack(side='left', fill='both', expand=True)

        # Turno / estado
        self.lbl_turno = tk.Label(left, text="", font=("Georgia", 13, "bold"),
                                   fg=GOLD, bg=BG)
        self.lbl_turno.pack(pady=(4, 2))
        self.lbl_nivel = tk.Label(left, text=f"Nivel: {self.nivel_var.get().capitalize()}",
                      font=("Georgia", 10), fg=TEXT_LITE, bg=BG)
        self.lbl_nivel.pack(pady=(0, 6))

        # Tablero (canvas scrollable)
        board_frame = tk.Frame(left, bg=PANEL, bd=2, relief='sunken')
        board_frame.pack(fill='both', expand=True, padx=4, pady=4)

        self.board_canvas = tk.Canvas(board_frame, bg=PANEL,
                                      highlightthickness=0, height=220)
        sb = tk.Scrollbar(board_frame, orient='horizontal',
                          command=self.board_canvas.xview)
        self.board_canvas.configure(xscrollcommand=sb.set)
        sb.pack(side='bottom', fill='x')
        self.board_canvas.pack(fill='both', expand=True)

        # Mano del jugador humano
        self.mano_frame = tk.Frame(left, bg=BG)
        self.mano_frame.pack(fill='x', pady=4)
        self.lbl_mano = tk.Label(left, text="Tu mano:", font=("Georgia", 11),
                                  fg=TEXT_LITE, bg=BG)
        self.lbl_mano.pack()
        self.lbl_valores = tk.Label(left, text="", font=("Georgia", 10), fg=GOLD, bg=BG)
        self.lbl_valores.pack(pady=(0, 4))

        # Botón pasar
        btn_row = tk.Frame(left, bg=BG)
        btn_row.pack(pady=4)
        self.btn_pasar = tk.Button(btn_row, text="Pasar turno",
                                    font=("Georgia", 11, "bold"),
                                    bg="#555", fg='white', relief='flat',
                                    cursor='hand2', padx=14, pady=5,
                                    command=self._humano_pasa)
        self.btn_pasar.pack(side='left', padx=6)

        self.btn_jugar = tk.Button(btn_row, text="Jugar ficha ▶",
                                    font=("Georgia", 11, "bold"),
                                    bg=GREEN, fg='white', relief='flat',
                                    cursor='hand2', padx=14, pady=5,
                                    command=self._humano_juega)
        self.btn_jugar.pack(side='left', padx=6)

        # Panel derecho: log + manos IA
        right = tk.Frame(main, bg=PANEL, width=240)
        right.pack(side='right', fill='y', padx=(6, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Registro", font=("Georgia", 12, "bold"),
                 fg=GOLD, bg=PANEL).pack(pady=(8, 2))

        log_frame = tk.Frame(right, bg=PANEL)
        log_frame.pack(fill='both', expand=True, padx=6)
        self.log_text = tk.Text(log_frame, bg="#0d1b2a", fg="#aee", width=28,
                                font=("Courier", 9), state='disabled',
                                relief='flat', bd=0, wrap='word')
        log_sb = tk.Scrollbar(log_frame, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_sb.set)
        log_sb.pack(side='right', fill='y')
        self.log_text.pack(fill='both', expand=True)

        # Fichas IA (ocultas)
        self.lbl_ia = {}
        for i, nombre in enumerate(self.juego.nombres):
            if nombre == "Tú":
                continue
            lbl = tk.Label(right, text=f"{nombre}: ? fichas",
                           font=("Georgia", 10), fg=TEXT_LITE, bg=PANEL)
            lbl.pack(pady=2)
            self.lbl_ia[i] = lbl

    # ── ACTUALIZAR UI ────────────────────────────────────────────
    def _actualizar_ui(self):
        if not self.juego:
            return
        j = self.juego

        # Turno
        nombre_turno = j.nombres[j.turno]
        self.lbl_turno.config(text=f"Turno: {nombre_turno}")
        # mostrar nivel
        if hasattr(self, 'lbl_nivel'):
            self.lbl_nivel.config(text=f"Nivel: {self.nivel_var.get().capitalize()}")

        # Tablero en canvas
        self._dibujar_tablero()

        # Mano humana
        for w in self.mano_frame.winfo_children():
            w.destroy()

        humano_idx = None
        for i, n in enumerate(j.nombres):
            if n == "Tú":
                humano_idx = i
                break

        # mostrar números válidos para jugar
        if not j.tablero:
            self.lbl_valores.config(text="Números válidos: Cualquiera (tablero vacío)")
        else:
            self.lbl_valores.config(text=f"Números válidos: {j.extremo_izq}  |  {j.extremo_der}")

        def _draw_tile(canvas, ficha, x, y, w=60, h=90, highlight=None):
            # fondo
            canvas.create_rectangle(x, y, x+w, y+h, fill=TILE_BG, outline=highlight or '#bbb', width=2)
            # división
            canvas.create_line(x, y+h//2, x+w, y+h//2, fill="#aaa", width=1)
            # pips positions relative
            def draw_pips(val, cx, cy, ww, hh):
                # predefinidas posiciones (3x2 grid)
                spots = [
                    (cx-ww*0.3, cy-hh*0.25), (cx+ww*0.3, cy-hh*0.25),
                    (cx-ww*0.3, cy),            (cx+ww*0.3, cy),
                    (cx-ww*0.3, cy+hh*0.25),(cx+ww*0.3, cy+hh*0.25)
                ]
                mapping = {
                    0: [],
                    1: [2],
                    2: [0,5],
                    3: [0,2,5],
                    4: [0,1,4,5],
                    5: [0,1,2,4,5],
                    6: [0,1,2,3,4,5]
                }
                r = 4
                for idx in mapping.get(val, []):
                    px, py = spots[idx]
                    canvas.create_oval(px-r, py-r, px+r, py+r, fill=TEXT_DARK, outline=TEXT_DARK)

            # top half
            draw_pips(ficha.a, x+w//2, y+h//4, w, h//2)
            # bottom half
            draw_pips(ficha.b, x+w//2, y+3*h//4, w, h//2)

        if humano_idx is not None:
            jugables = j.fichas_jugables(humano_idx)
            for ficha in j.manos[humano_idx]:
                es_sel = (ficha == self.ficha_sel)
                is_jugable = ficha in jugables
                highlight = ACCENT if es_sel else (GREEN if is_jugable else '#bbb')
                frame = tk.Canvas(self.mano_frame, width=64, height=94, bg=BG, highlightthickness=0)
                _draw_tile(frame, ficha, 2, 2, w=60, h=90, highlight=highlight)
                # mostrar pequeño badge con numero que coincide
                if j.tablero:
                    badges = []
                    if ficha.a == j.extremo_izq or ficha.b == j.extremo_izq:
                        badges.append(str(j.extremo_izq))
                    if ficha.a == j.extremo_der or ficha.b == j.extremo_der:
                        badges.append(str(j.extremo_der))
                    if badges:
                        frame.create_rectangle(40, 4, 60, 20, fill=ACCENT, outline='')
                        frame.create_text(50, 12, text=','.join(badges), fill='white', font=("Georgia", 8, "bold"))

                frame.pack(side='left', padx=6)
                frame.bind('<Button-1>', lambda e, f=ficha: self._seleccionar(f))

        # Botones activos solo si es turno humano
        es_mi_turno = (humano_idx is not None and j.turno == humano_idx)
        state = 'normal' if es_mi_turno else 'disabled'
        self.btn_pasar.config(state=state)
        self.btn_jugar.config(state=state)

        # Fichas IA
        for i, lbl in self.lbl_ia.items():
            lbl.config(text=f"{j.nombres[i]}: {len(j.manos[i])} fichas")

        # Log
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        for linea in j.log[-60:]:
            self.log_text.insert('end', linea + "\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def _dibujar_tablero(self):
        c = self.board_canvas
        c.delete('all')
        j = self.juego
        if not j.tablero:
            c.create_text(400, 110, text="Tablero vacío — ¡empieza jugando!",
                          fill="#555", font=("Georgia", 13))
            return

        x, y = 10, 60
        w, h = 50, 80
        gap = 4
        for ficha in j.tablero:
            # sombra
            c.create_rectangle(x+3, y+3, x+w+3, y+h+3, fill="#000", outline="")
            # ficha
            c.create_rectangle(x, y, x+w, y+h, fill=TILE_BG, outline="#bbb", width=1)
            c.create_line(x, y+h//2, x+w, y+h//2, fill="#aaa", width=1)
            # dibujar pips para cada mitad
            def _draw_pips(canvas, val, cx, cy, ww, hh):
                spots = [
                    (cx-ww*0.3, cy-hh*0.25), (cx+ww*0.3, cy-hh*0.25),
                    (cx-ww*0.3, cy),            (cx+ww*0.3, cy),
                    (cx-ww*0.3, cy+hh*0.25),(cx+ww*0.3, cy+hh*0.25)
                ]
                mapping = {
                    0: [],
                    1: [2],
                    2: [0,5],
                    3: [0,2,5],
                    4: [0,1,4,5],
                    5: [0,1,2,4,5],
                    6: [0,1,2,3,4,5]
                }
                r = 3
                for idx in mapping.get(val, []):
                    px, py = spots[idx]
                    canvas.create_oval(px-r, py-r, px+r, py+r, fill=TEXT_DARK, outline=TEXT_DARK)

            _draw_pips(c, ficha.a, x+w//2, y+h//4, w, h//2)
            _draw_pips(c, ficha.b, x+w//2, y+3*h//4, w, h//2)
            x += w + gap

        total_w = x + 10
        c.configure(scrollregion=(0, 0, max(total_w, 800), 200))
        c.xview_moveto(1.0)

        # extremos
        c.create_text(14, 14, text=f"◄ {j.extremo_izq}",
                      fill=GOLD, font=("Georgia", 11, "bold"), anchor='w')
        c.create_text(c.winfo_width()-14 if c.winfo_width() > 1 else 780,
                      14, text=f"{j.extremo_der} ►",
                      fill=GOLD, font=("Georgia", 11, "bold"), anchor='e')

    # ── ACCIONES HUMANO ──────────────────────────────────────────
    def _seleccionar(self, ficha: Ficha):
        self.ficha_sel = ficha
        self._actualizar_ui()

    def _humano_juega(self):
        j = self.juego
        if not self.ficha_sel:
            messagebox.showinfo("Dominó", "Selecciona una ficha primero.")
            return
        humano_idx = j.nombres.index("Tú")
        ok = j.jugar_ficha(humano_idx, self.ficha_sel, 'auto')
        if not ok:
            messagebox.showwarning("Dominó",
                "Esa ficha no encaja en ningún extremo del tablero.")
            return
        self.ficha_sel = None
        self._actualizar_ui()
        self._verificar_fin()
        if not j.ganador and j.es_turno_ia():
            self.after(700, self._paso_ia)

    def _humano_pasa(self):
        j = self.juego
        jugables = j.fichas_jugables(j.turno)
        if jugables:
            messagebox.showinfo("Dominó",
                "Aún tienes fichas jugables. ¡Debes jugar!")
            return
        j.pasar(j.turno)
        self._actualizar_ui()
        self._verificar_fin()
        if not j.ganador and j.es_turno_ia():
            self.after(700, self._paso_ia)

    # ── IA ───────────────────────────────────────────────────────
    def _paso_ia(self):
        j = self.juego
        if j.ganador:
            return
        j.ia_jugar(j.turno)
        self._actualizar_ui()
        self._verificar_fin()
        if not j.ganador and j.es_turno_ia():
            self.after(700, self._paso_ia)

    def _ciclo_ia(self):
        """Ciclo automático para modo Máquina vs Máquina."""
        j = self.juego
        if j.ganador:
            self._verificar_fin()
            return
        j.ia_jugar(j.turno)
        self._actualizar_ui()
        if not j.ganador:
            self.after(600, self._ciclo_ia)
        else:
            self._verificar_fin()

    # ── FIN DEL JUEGO ────────────────────────────────────────────
    def _verificar_fin(self):
        j = self.juego
        if j.ganador is not None:
            nombre = j.nombres[j.ganador]
            resp = messagebox.askyesno("Fin del juego",
                f"🏆 ¡Ganó {nombre}!\n\n¿Quieres jugar otra partida?")
            if resp:
                self._iniciar(j.modo)
            else:
                self._mostrar_menu()

    # ── UTILIDADES ───────────────────────────────────────────────
    def _limpiar(self):
        for w in self.winfo_children():
            w.destroy()


# ─── MAIN ────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = DominoApp()
    app.mainloop()