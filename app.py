# app.py — LA APLICACIÓN ÚNICA del laboratorio (MOTOR COMPARTIDO, raíz).
#
# Genérica y agnóstica a la disciplina: la usan macro/ y estadistica/ (y futuras)
# vía `import app`; las etiquetas propias (secciones, títulos, "equilibrio") salen
# de config.SECCIONES/APP_* de la disciplina activa. Un solo punto de entrada
# (python3 main.py) y una sola ventana. El usuario elige un modelo del currículo
# y lo recorre de forma PROGRESIVA y pedagógica:
#
#   pregunta → contexto → supuestos y variables → construcción de cada
#   ecuación → derivación → construcción gráfica CURVA A CURVA → equilibrio →
#   experimentos (shock, E1→E2, mecanismo, ¿por qué?) → experimentación libre
#   (parámetros → ecuaciones → curvas → equilibrio → resultados, en vivo) →
#   comparación de políticas → limitaciones y conexión con el siguiente modelo.
#
# Navegación mínima: tres botones (⌂ / ◀ / ▶) y el teclado (←/→, ↑/↓, Enter,
# M para volver al menú). Cálculo, comparación, sensibilidad y láminas ocurren
# por dentro — el usuario nunca ve un comando.

import textwrap

import matplotlib.pyplot as plt
from matplotlib.widgets import Button, Slider

import base
import config
import graficos
import laboratorio

# app.py es MOTOR COMPARTIDO (raíz): el recorrido pedagógico es genérico (se
# construye desde la Ficha). Las etiquetas propias de cada disciplina —secciones,
# títulos, la palabra "equilibrio"— se leen de config (config.SECCIONES,
# config.APP_*), que resuelve a la disciplina activa por el sys.path.

_TINTA = "#222222"


def _wrap(texto, ancho):
    return "\n".join(textwrap.wrap(texto, ancho))


def _construir_pasos(m):
    """La secuencia pedagógica del modelo, generada desde su ficha."""
    F = m.ficha
    pasos = [("portada", None)]
    if F:
        pasos.append(("contexto", None))
        pasos.append(("supuestos", None))
        for i in range(len(F.ecuaciones)):
            pasos.append(("ecuacion", i))
        if F.derivacion:
            pasos.append(("derivacion", None))
    n_lineas = len(m.curvas(m.dict_params()).get("lineas", {}))
    for i in range(1, n_lineas + 1):
        pasos.append(("curva", i))
    pasos.append(("equilibrio", None))
    for i in range(len(m.escenarios)):
        pasos.append(("experimento", i))
    pasos.append(("libre", None))
    if len(m.escenarios) >= 2:
        pasos.append(("comparacion", None))
    if F and (F.limitaciones or F.evolucion):
        pasos.append(("cierre", None))
    return pasos


def _titulo_paso(m, tipo, dato):
    F = m.ficha
    if tipo == "ecuacion":
        return (f"Construcción del modelo — ecuación {dato + 1}: "
                f"{F.ecuaciones[dato].nombre}")
    if tipo == "curva":
        return f"Construcción del gráfico — curva {dato}"
    if tipo == "experimento":
        return f"Experimento: {m.escenarios[dato].nombre}"
    return {"portada": "La pregunta",
            "contexto": "Contexto histórico y autores",
            "supuestos": "Supuestos y variables",
            "derivacion": "Derivación, paso a paso",
            "equilibrio": config.APP_PASO_RESULTADOS,
            "libre": "Experimentación libre",
            "comparacion": config.APP_PASO_COMPARACION,
            "cierre": "Límites del modelo y el camino que abre"}[tipo]


class Laboratorio:
    def __init__(self, modelos):
        self.modelos = modelos
        self.en_menu = True
        self.cursor = 0                 # selección en el menú
        self.m = None                   # modelo activo
        self.pasos, self.i_paso = [], 0
        self._verif = {}                # id → (superadas, total)
        self._libre = None              # refs del paso de experimentación libre
        self._dyn = []                  # widgets dinámicos (mantener referencias)

    # ── ciclo de vida ────────────────────────────────────────────────────
    def mostrar(self):
        self.fig = plt.figure(figsize=(13.6, 8.9))
        try:
            self.fig.canvas.manager.set_window_title(config.APP_VENTANA)
        except Exception:
            pass
        self.ax_a = self.fig.add_axes([0.045, 0.015, 0.11, 0.046])
        self.ax_b = self.fig.add_axes([0.170, 0.015, 0.13, 0.046])
        self.ax_c = self.fig.add_axes([0.815, 0.015, 0.14, 0.046])
        self.b_a = Button(self.ax_a, "", color="#EDEFF3", hovercolor="#DDE2EA")
        self.b_b = Button(self.ax_b, "", color="#EDEFF3", hovercolor="#DDE2EA")
        self.b_c = Button(self.ax_c, "", color=config.AZUL, hovercolor="#2E5496")
        self.b_c.label.set_color("white")
        for boton in (self.b_a, self.b_b, self.b_c):
            boton.label.set_fontfamily("DejaVu Sans")   # glifos ⌂◀▶▲▼ (no están en STIX)
        self.b_a.on_clicked(self._accion_a)
        self.b_b.on_clicked(self._accion_b)
        self.b_c.on_clicked(self._accion_c)
        self.fig.canvas.mpl_connect("key_press_event", self._tecla)
        self._render()
        plt.show()

    # ── acciones ─────────────────────────────────────────────────────────
    def _accion_a(self, _=None):        # menú: ▲ · recorrido: ⌂ modelos
        if self.en_menu:
            self.cursor = max(0, self.cursor - 1)
        else:
            self.en_menu = True
        self._render()

    def _accion_b(self, _=None):        # menú: ▼ · recorrido: ◀ anterior
        if self.en_menu:
            self.cursor = min(len(self.modelos) - 1, self.cursor + 1)
        elif self.i_paso > 0:
            self.i_paso -= 1
        self._render()

    def _accion_c(self, _=None):        # menú: entrar · recorrido: ▶ / siguiente modelo
        if self.en_menu:
            self._entrar(self.cursor)
        elif self.i_paso < len(self.pasos) - 1:
            self.i_paso += 1
            self._render()
        else:                           # último paso → siguiente modelo del currículo
            idx = self.modelos.index(self.m)
            if idx < len(self.modelos) - 1:
                self._entrar(idx + 1)
            else:
                self.en_menu = True
                self._render()

    def _entrar(self, idx):
        self.m = self.modelos[idx]
        self.cursor = idx
        if self.m.id not in self._verif:
            checks = base.verificar(self.m)
            self._verif[self.m.id] = (sum(1 for _, ok, _ in checks if ok), len(checks))
        self.pasos = _construir_pasos(self.m)
        self.i_paso = 0
        self.en_menu = False
        self._render()

    def _tecla(self, ev):
        if ev.key in ("right", "enter") and not self.en_menu:
            self._accion_c()
        elif ev.key == "enter" and self.en_menu:
            self._accion_c()
        elif ev.key == "left" and not self.en_menu:
            self._accion_b()
        elif ev.key == "up" and self.en_menu:
            self._accion_a()
        elif ev.key == "down" and self.en_menu:
            self._accion_b()
        elif ev.key in ("m", "escape") and not self.en_menu:
            self._accion_a()

    # ── infraestructura de render ────────────────────────────────────────
    def _limpiar(self):
        fijos = {self.ax_a, self.ax_b, self.ax_c}
        for ax in list(self.fig.axes):
            if ax not in fijos:
                ax.remove()
        for t in list(self.fig.texts):
            t.remove()
        self._dyn.clear()
        self._libre = None

    def _panel(self, rect):
        ax = self.fig.add_axes(rect)
        ax.axis("off")
        return ax

    def _cabecera(self, titulo, sub=""):
        self.fig.text(0.045, 0.972, config.APP_NOMBRE,
                      fontsize=9, color=config.GRIS, fontweight="bold")
        self.fig.text(0.045, 0.935, titulo, fontsize=16, color=config.AZUL,
                      fontweight="bold")
        if sub:
            self.fig.text(0.045, 0.905, sub, fontsize=10.5, color=_TINTA)

    def _texto(self, x, y, s, tam=10.5, color=_TINTA, **kw):
        return self.fig.text(x, y, s, fontsize=tam, color=color, va="top",
                             linespacing=1.65, **kw)

    def _botones(self, a, b, c):
        for boton, etq in ((self.b_a, a), (self.b_b, b), (self.b_c, c)):
            boton.label.set_text(etq)

    # ── render principal ─────────────────────────────────────────────────
    def _render(self):
        self._limpiar()
        if self.en_menu:
            self._render_menu()
        else:
            self._render_paso()
        self.fig.canvas.draw_idle()

    def _render_menu(self):
        self._cabecera(config.APP_TITULO, config.APP_RECORRIDO)
        y, nivel_previo = 0.855, None
        ini = max(0, self.cursor - 12)
        for i, m in enumerate(self.modelos[ini:ini + 20], start=ini):
            if m.nivel != nivel_previo:
                nivel_previo = m.nivel
                self.fig.text(0.06, y, f"{config.APP_UNIDAD_NIVEL} {m.nivel} — {config.SECCIONES.get(m.nivel, '')}",
                              fontsize=10, color=config.ROJO, fontweight="bold")
                y -= 0.028
            sel = (i == self.cursor)
            marca = "» " if sel else "   "
            self.fig.text(0.075, y, f"{marca}{m.id}  {m.nombre}",
                          fontsize=10, color=config.AZUL if sel else _TINTA,
                          fontweight="bold" if sel else "normal")
            y -= 0.0255
        if ini + 20 < len(self.modelos):
            self.fig.text(0.075, y, "⋮  (baja para ver más modelos)",
                          fontsize=9, color=config.GRIS)
        m = self.modelos[self.cursor]
        if m.ficha and m.ficha.pregunta:
            self.fig.text(0.045, 0.118, _wrap(f"« {m.ficha.pregunta} »", 120),
                          fontsize=11, color=config.AZUL, style="italic")
        self._botones("▲ Subir", "▼ Bajar", "Entrar  ▶")

    def _render_paso(self):
        m, F = self.m, self.m.ficha
        tipo, dato = self.pasos[self.i_paso]
        prog = f"Paso {self.i_paso + 1}/{len(self.pasos)} — {_titulo_paso(m, tipo, dato)}"
        self._cabecera(f"{m.nombre}   ·   {config.APP_UNIDAD_NIVEL.lower()} {m.nivel} · {m.id}", prog)
        getattr(self, f"_paso_{tipo}")(dato)
        ultimo = self.i_paso == len(self.pasos) - 1
        self._botones("⌂ Modelos", "◀ Anterior",
                      "Siguiente modelo ▶" if ultimo else "Siguiente ▶")

    # ── pasos ────────────────────────────────────────────────────────────
    def _paso_portada(self, _):
        m, F = self.m, self.m.ficha
        if F and F.pregunta:
            self._texto(0.10, 0.76, _wrap(f"« {F.pregunta} »", 78), 17, config.AZUL,
                        style="italic")
        ok, tot = self._verif[m.id]
        self._texto(0.10, 0.50,
                    f"Experimentos disponibles: {len(m.escenarios)}\n"
                    f"Verificaciones internas del modelo: {ok}/{tot} superadas\n"
                    f"Procedencia: {_wrap(F.procedencia, 90) if F else '—'}", 10.5)
        self._texto(0.10, 0.24, "Usa los botones (o las flechas del teclado) para "
                                "avanzar por el recorrido.", 10, config.GRIS)

    def _paso_contexto(self, _):
        F = self.m.ficha
        self._texto(0.065, 0.84, "CONTEXTO HISTÓRICO", 11, config.AZUL, fontweight="bold")
        self._texto(0.065, 0.80, _wrap(F.contexto, 108), 11)
        self._texto(0.065, 0.40, "AUTORES Y ESCUELAS", 11, config.AZUL, fontweight="bold")
        self._texto(0.065, 0.36, _wrap(F.autores, 108), 11)

    def _paso_supuestos(self, _):
        F = self.m.ficha
        self._texto(0.065, 0.84, "SUPUESTOS", 11, config.AZUL, fontweight="bold")
        y = 0.80
        for s in F.supuestos:
            self._texto(0.075, y, _wrap(f"•  {s}", 100), 10.5)
            y -= 0.045 + 0.023 * (len(s) // 100)
        if F.variables:
            y -= 0.02
            self._texto(0.065, y, "VARIABLES", 11, config.AZUL, fontweight="bold")
            y -= 0.04
            for simbolo, desc in F.variables:
                self._texto(0.075, y, f"{simbolo:<14} {desc}", 10.5)
                y -= 0.036

    def _paso_ecuacion(self, i):
        F = self.m.ficha
        e = F.ecuaciones[i]
        for j in range(i):                        # lo ya construido, arriba y pequeño
            self._texto(0.10, 0.86 - 0.045 * j,
                        f"${F.ecuaciones[j].latex}$" if laboratorio._math_seguro(F.ecuaciones[j].latex)
                        else F.ecuaciones[j].nombre, 10, config.GRIS)
        centro = laboratorio._math_seguro(e.latex)
        self._texto(0.50, 0.62, centro or e.nombre, 20, config.AZUL, ha="center")
        self._texto(0.14, 0.44, _wrap(e.significado, 92), 11.5)

    def _paso_derivacion(self, _):
        F = self.m.ficha
        y = 0.80
        for i, paso in enumerate(F.derivacion, 1):
            linea = laboratorio._math_seguro(paso)
            self._texto(0.12, y, f"{i}.", 11, config.GRIS)
            self._texto(0.16, y, linea if linea else paso, 14, config.AZUL)
            y -= 0.115

    def _paso_curva(self, i):
        m = self.m
        ax = self.fig.add_axes([0.055, 0.14, 0.56, 0.72])
        datos = graficos._dibujar(ax, m, m.dict_params(), hasta_lineas=i,
                                  con_equilibrio=False, con_puntos=False,
                                  con_anotacion=False)
        nombres = list(datos.get("lineas", {}).keys())
        lado = self._panel([0.65, 0.14, 0.32, 0.72])
        lado.text(0.0, 1.00, "SE AÑADE", fontsize=11, color=config.AZUL,
                  fontweight="bold", va="top", transform=lado.transAxes)
        if i <= len(nombres):
            lado.text(0.0, 0.94, _wrap(nombres[i - 1], 40), fontsize=11.5,
                      color=_TINTA, va="top", linespacing=1.6,
                      transform=lado.transAxes)
        if i > 1:
            ya = "\n".join(f"•  {n}" for n in nombres[:i - 1])
            lado.text(0.0, 0.80, "YA EN EL GRÁFICO", fontsize=10.5,
                      color=config.AZUL, fontweight="bold", va="top",
                      transform=lado.transAxes)
            lado.text(0.0, 0.74, ya, fontsize=9.5, color=_TINTA, va="top",
                      linespacing=1.8, transform=lado.transAxes)

    def _paso_equilibrio(self, _):
        m = self.m
        ax = self.fig.add_axes([0.055, 0.14, 0.56, 0.72])
        graficos._dibujar(ax, m, m.dict_params())
        lado = self._panel([0.65, 0.40, 0.33, 0.46])
        filas = [(k, base.fmt(v), "", "") for k, v in m.calcular().items()
                 if isinstance(v, (int, float))][:9]
        laboratorio._tabla_resultados(lado, filas)
        if m.ficha and m.ficha.equilibrio:
            abajo = self._panel([0.65, 0.12, 0.33, 0.26])
            laboratorio._panel_texto(abajo, config.APP_PANEL_RESULTADOS,
                                     _wrap(m.ficha.equilibrio, 52), 9)

    def _paso_experimento(self, i):
        m = self.m
        esc = m.escenarios[i]
        params0 = m.dict_params()
        params1 = dict(params0, **esc.cambios)
        cambios = ", ".join(f"{k}: {base.fmt(m.parametro(k).valor)} → {base.fmt(v)}"
                            for k, v in esc.cambios.items())
        self.fig.text(0.045, 0.875, f"Experimento:  {esc.descripcion}   ({cambios})",
                      fontsize=10.5, color=config.ROJO)
        ax = self.fig.add_axes([0.055, 0.14, 0.55, 0.68])
        graficos._dibujar(ax, m, params1)
        graficos.marcar_transicion(ax, m, params0, params1)
        lado = self._panel([0.64, 0.46, 0.34, 0.38])
        laboratorio._tabla_resultados(lado, laboratorio._filas_delta(m, esc, maximo=7))
        cuerpo = laboratorio._texto_mecanismo(esc, ancho=50)
        if esc.lectura:
            cuerpo += "\n\n¿Por qué?  " + _wrap(esc.lectura, 50)
        abajo = self._panel([0.64, 0.075, 0.34, 0.37])
        laboratorio._panel_texto(abajo, "MECANISMO", cuerpo, 9)

    def _paso_libre(self, _):
        m = self.m
        claves = []
        for esc in m.escenarios:
            for k in esc.cambios:
                if k not in claves:
                    claves.append(k)
        claves = (claves or [p.nombre for p in m.parametros])[:5]
        ax = self.fig.add_axes([0.055, 0.34, 0.56, 0.53])
        graficos._dibujar(ax, m, m.dict_params())
        eqs = self._panel([0.65, 0.56, 0.33, 0.30])
        t_e = laboratorio._panel_texto(eqs, "ECUACIONES (en vivo)",
                                       laboratorio._texto_ecuaciones(m, m.dict_params()), 10)
        res = self._panel([0.65, 0.20, 0.33, 0.32])
        t_r = laboratorio._panel_texto(res, "CAMBIO FRENTE A LA BASE", "—", 9.5)

        sliders = []
        base_params = m.dict_params()
        y0 = 0.255
        for j, k in enumerate(claves):
            p = m.parametro(k)
            eje = self.fig.add_axes([0.11, y0 - 0.042 * j, 0.38, 0.026])
            s = Slider(eje, p.etiqueta or k, p.minimo, p.maximo,
                       valinit=p.valor, valstep=p.paso, color=config.AZUL2)
            s.label.set_fontsize(8.5)
            s.valtext.set_fontsize(8.5)
            sliders.append((k, s))
            self._dyn.append(s)

        res_base = m.calcular()

        def _actualizar(_=None):
            cambios = {k: s.val for k, s in sliders}
            params = dict(base_params, **cambios)
            graficos._dibujar(ax, m, params)
            t_e.set_text(laboratorio._texto_ecuaciones(m, params))
            res_new = m.calcular(**cambios)
            filas = []
            for kk, v0 in list(res_base.items())[:7]:
                v1 = res_new.get(kk)
                if isinstance(v0, (int, float)) and isinstance(v1, (int, float)):
                    filas.append(f"{kk}:  {base.fmt(v0)} → {base.fmt(v1)}  "
                                 f"({base.signo(v1 - v0)} {base.fmt(abs(v1 - v0))})")
            t_r.set_text("\n".join(filas))
            self.fig.canvas.draw_idle()

        for _k, s in sliders:
            s.on_changed(_actualizar)
        _actualizar()

        ax_r = self.fig.add_axes([0.65, 0.075, 0.15, 0.042])
        b_r = Button(ax_r, "Restablecer", color="#EDEFF3", hovercolor="#DDE2EA")
        ax_g = self.fig.add_axes([0.82, 0.075, 0.16, 0.042])
        b_g = Button(ax_g, "Guardar lámina", color="#EDEFF3", hovercolor="#DDE2EA")
        self._dyn += [b_r, b_g]

        def _reset(_):
            for k, s in sliders:
                s.reset()

        def _guardar(_):
            cambios = {k: s.val for k, s in sliders
                       if abs(s.val - base_params[k]) > 1e-12}
            esc = base.Escenario("experimento_libre", "cambios manuales en el laboratorio",
                                 cambios or {claves[0]: base_params[claves[0]]})
            destino = config.DIR_SALIDAS / "capturas"
            destino.mkdir(parents=True, exist_ok=True)
            ruta = destino / f"{m.id}_experimento_libre.png"
            laboratorio.lamina(m, esc, ruta)
            b_g.label.set_text("lámina guardada")
            self.fig.canvas.draw_idle()

        b_r.on_clicked(_reset)
        b_g.on_clicked(_guardar)

    def _paso_comparacion(self, _):
        m = self.m
        magnitudes, columnas = base.comparar(m, [e.nombre for e in m.escenarios])
        nombres = list(columnas)
        lado = self._panel([0.06, 0.14, 0.90, 0.70])
        filas = [[k] + [base.fmt(columnas[n][k]) for n in nombres] for k in magnitudes[:9]]
        tabla = lado.table(cellText=filas, colLabels=["magnitud"] + nombres,
                           loc="upper center",
                           bbox=[0.0, 0.30, 1.0, 0.66])
        tabla.auto_set_font_size(False)
        tabla.set_fontsize(9)
        for (fila, col), celda in tabla.get_celld().items():
            celda.set_edgecolor(config.GRIS); celda.set_linewidth(0.5)
            if fila == 0:
                celda.set_text_props(color="white", fontweight="bold")
                celda.set_facecolor(config.AZUL)
            elif col == 0:
                celda.set_text_props(ha="left")
        lecturas = "\n".join(f"«{e.nombre}»  —  {_wrap(e.descripcion, 95)}"
                             for e in m.escenarios)
        lado.text(0.0, 0.22, lecturas, fontsize=9.5, color=_TINTA, va="top",
                  linespacing=1.7, transform=lado.transAxes)

    def _paso_cierre(self, _):
        F = self.m.ficha
        self._texto(0.065, 0.84, "LIMITACIONES — dónde deja de funcionar", 11,
                    config.ROJO, fontweight="bold")
        y = 0.80
        for l in F.limitaciones:
            self._texto(0.075, y, _wrap(f"•  {l}", 100), 10)
            y -= 0.042 + 0.021 * (len(l) // 100)
        if F.evolucion:
            y -= 0.02
            self._texto(0.065, y, "EL CAMINO QUE ABRE", 11, config.AZUL, fontweight="bold")
            self._texto(0.065, y - 0.04, _wrap(F.evolucion, 105), 10.5)


def ejecutar(modelos):
    """Punto de entrada de la aplicación única del laboratorio."""
    Laboratorio(modelos).mostrar()
