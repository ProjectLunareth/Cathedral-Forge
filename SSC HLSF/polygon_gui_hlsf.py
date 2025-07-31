import sys
import numpy as np
from vispy import app, gloo
from vispy.util.transforms import rotate, translate

# Constants
PHI = 0.618
MAX_LEVELS = 7

vertex_shader = """
uniform mat4 u_model;
uniform mat4 u_view;
uniform mat4 u_projection;
attribute vec2 a_position;
void main() {
    gl_Position = u_projection * u_view * u_model * vec4(a_position, 0.0, 1.0);
}
"""

fragment_shader = """
uniform vec4 u_color;
void main() {
    gl_FragColor = u_color;
}
"""

def create_regular_polygon(sides, radius=1.0):
    angles = np.linspace(0, 2 * np.pi, sides, endpoint=False)
    return np.c_[np.cos(angles), np.sin(angles)] * radius

class HexagonCanvas(app.Canvas):
    def __init__(self):
        app.Canvas.__init__(self, keys='interactive', size=(800, 800))
        self.program = gloo.Program(vertex_shader, fragment_shader)
        self.vertices = create_regular_polygon(6)
        self.translate = np.array([0.0, 0.0])
        self.zoom = 1.0
        self.level = 0
        self.build_buffers()

        gloo.set_viewport(0, 0, *self.physical_size)
        self.timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.show()

    def build_buffers(self):
        self.program['a_position'] = self.vertices.astype(np.float32)
        self.program['u_color'] = 1.0, 0.5, 0.2, 0.8

    def on_draw(self, event):
        gloo.clear('black')
        self.render_recursive(self.translate, 1.0, 0)

    def render_recursive(self, center, radius, depth):
        if depth > MAX_LEVELS:
            return

        transform = np.eye(4, dtype=np.float32)
        transform[:2, 3] = center * self.zoom
        transform[:2, :2] *= radius * self.zoom
        self.program['u_model'] = transform
        self.program.draw('triangle_fan')

        angle_step = 2 * np.pi / 6
        for i in range(6):
            angle = i * angle_step
            offset = center + radius * np.array([np.cos(angle), np.sin(angle)])
            self.render_recursive(offset, radius * PHI, depth + 1)

    def on_mouse_wheel(self, event):
        self.zoom *= 1.1 if event.delta[1] > 0 else 0.9
        self.update()

    def on_mouse_move(self, event):
        if event.is_dragging:
            dx, dy = event.delta
            self.translate += np.array([dx, -dy]) / 100.0
            self.update()

    def on_timer(self, event):
        self.update()

if __name__ == '__main__':
    canvas = HexagonCanvas()
    app.run()
