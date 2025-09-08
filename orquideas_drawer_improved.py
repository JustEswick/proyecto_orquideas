import turtle
import json

class SvgAnimator:
    def __init__(self, json_file):
        # --- Carga y configuración inicial ---
        print("Cargando datos del JSON de alta calidad...")
        with open(json_file, 'r', encoding='utf-8') as f:
            self.regions = json.load(f)
        
        # Centrar y escalar el dibujo (lógica ya conocida)
        self.scale, self.center_x, self.center_y = self._calculate_bounds()

        # --- Configuración de la pantalla y el lápiz ---
        self.screen = turtle.Screen()
        self.screen.title("Animando SVG de Alta Calidad")
        self.screen.setup(800, 800)
        self.screen.bgcolor("black")
        self.screen.tracer(0) # ¡Crucial! Desactivamos el repintado automático

        self.t = turtle.Turtle()
        self.t.hideturtle()
        self.t.speed(0)
        
        self.current_region_index = 0
        print("Configuración completa. ¡Iniciando animación!")

    def _calculate_bounds(self):
        all_points = [(p[0], p[1]) for r in self.regions for p in r['contour']]
        if not all_points: return 1, 0, 0
        min_x, max_x = min(p[0] for p in all_points), max(p[0] for p in all_points)
        min_y, max_y = min(p[1] for p in all_points), max(p[1] for p in all_points)
        img_width, img_height = max_x - min_x, max_y - min_y
        scale = min(700 / img_width, 700 / img_height) if img_width > 0 and img_height > 0 else 1
        center_x, center_y = (min_x + max_x) / 2, (min_y + max_y) / 2
        return scale, center_x, center_y

    def _transform_point(self, point):
        """Aplica la escala y centrado a un solo punto."""
        x = (point[0] - self.center_x) * self.scale
        y = (self.center_y - point[1]) * self.scale
        return x, y

    def _draw_next_region(self):
        # Condición de parada: si ya dibujamos todo, terminamos.
        if self.current_region_index >= len(self.regions):
            print("🎨 ¡Animación completada! Haz clic en la ventana para salir.")
            self.screen.update() # Aseguramos un último repintado
            self.screen.exitonclick() # Mantiene la ventana abierta hasta que se hace clic
            return

        # Obtener la región actual
        region = self.regions[self.current_region_index]
        points = region['contour']
        
        # Configurar color
        color = '#{:02x}{:02x}{:02x}'.format(*region['color'])
        self.t.color(color, color)

        # Dibujar la forma completa
        if points:
            self.t.penup()
            self.t.goto(self._transform_point(points[0]))
            self.t.pendown()
            self.t.begin_fill()
            for point in points[1:]:
                self.t.goto(self._transform_point(point))
            self.t.goto(self._transform_point(points[0])) # Cerrar la forma
            self.t.end_fill()

        # Actualizar la pantalla para mostrar la nueva forma
        self.screen.update()

        # Incrementar el índice y programar el siguiente dibujo
        self.current_region_index += 1
        # Delay de 10ms antes de dibujar la siguiente forma
        self.screen.ontimer(self._draw_next_region, 10) 

    def animate(self):
        # Iniciar el ciclo de animación
        self._draw_next_region()
        self.screen.mainloop()

if __name__ == "__main__":
    animator = SvgAnimator("orquideas_hq.json")
    animator.animate()