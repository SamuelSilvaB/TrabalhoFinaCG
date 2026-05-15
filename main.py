
# Chão quadriculado estilo Into the Breach (OpenGL + GLFW)
# Dependências:
#     pip install glfw PyOpenGL numpy

# Controles:
# - Mouse esquerdo arrasta para girar
# - Setas ajustam câmera
# - ESC sai


import glfw
from OpenGL.GL import *
import numpy as np
import math
import sys
import ctypes
import os

def read_shader_file(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    shader_path = os.path.join(base_dir, filename)

    with open(shader_path, "r", encoding="utf-8") as file:
        return file.read()
    
def compile_shader(src, shader_type):
    shader = glCreateShader(shader_type)
    glShaderSource(shader, src)
    glCompileShader(shader)

    if not glGetShaderiv(shader, GL_COMPILE_STATUS):
        raise RuntimeError(glGetShaderInfoLog(shader).decode())

    return shader


def create_program():
    vs_source = read_shader_file("vertex_shader.glsl")
    fs_source = read_shader_file("fragment_shader.glsl")

    vs = compile_shader(vs_source, GL_VERTEX_SHADER)
    fs = compile_shader(fs_source, GL_FRAGMENT_SHADER)

    program = glCreateProgram()
    glAttachShader(program, vs)
    glAttachShader(program, fs)
    glLinkProgram(program)

    if not glGetProgramiv(program, GL_LINK_STATUS):
        raise RuntimeError(glGetProgramInfoLog(program).decode())

    glDeleteShader(vs)
    glDeleteShader(fs)

    return program


def add_tile(x, z, size, color):
    # agora cada tile vira um bloco com espessura
    h = 0.90

    x0 = x
    x1 = x + size
    y0 = 0.0
    y1 = h
    z0 = z
    z1 = z + size

    r, g, b = color

    # topo um pouco mais claro para dar sensação de volume
    top = (min(r + 0.08, 1.0), min(g + 0.08, 1.0), min(b + 0.08, 1.0))
    side = (r * 0.72, g * 0.72, b * 0.72)

    tr, tg, tb = top
    sr, sg, sb = side

    vertices = [
        # topo
        x0, y1, z0, tr, tg, tb,
        x1, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,

        x0, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,
        x0, y1, z1, tr, tg, tb,

        # frente
        x0, y0, z1, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,

        x0, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,

        # direita
        x1, y0, z0, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,

        x1, y0, z0, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,

        # esquerda
        x0, y0, z1, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,

        x0, y0, z1, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,

        # trás
        x1, y0, z0, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,

        x1, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,
    ]

    return vertices


def build_grid():
    SIZE = 1.0
    GRID = 8

    LIGHT = (0.78, 0.86, 0.90)
    DARK = (0.38, 0.52, 0.60)

    data = []

    offset = GRID / 2

    for row in range(GRID):
        for col in range(GRID):
            color = LIGHT if (row + col) % 2 == 0 else DARK

            x = col - offset
            z = row - offset

            data += add_tile(x, z, SIZE, color)

    return np.array(data, dtype=np.float32)


def upload(vertices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)

    glBindVertexArray(vao)
    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    stride = 6 * 4

    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
    glEnableVertexAttribArray(0)

    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
    glEnableVertexAttribArray(1)

    glBindVertexArray(0)

    return vao, len(vertices) // 6


def ortho(left, right, bottom, top, near, far):
    return np.array([
        [2 / (right - left), 0, 0, -(right + left) / (right - left)],
        [0, 2 / (top - bottom), 0, -(top + bottom) / (top - bottom)],
        [0, 0, -2 / (far - near), -(far + near) / (far - near)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


def look_at(eye, center, up):
    f = center - eye
    f = f / np.linalg.norm(f)

    s = np.cross(f, up)
    s = s / np.linalg.norm(s)

    u = np.cross(s, f)

    return np.array([
        [s[0], s[1], s[2], -np.dot(s, eye)],
        [u[0], u[1], u[2], -np.dot(u, eye)],
        [-f[0], -f[1], -f[2], np.dot(f, eye)],
        [0, 0, 0, 1],
    ], dtype=np.float32)


def get_mvp(angle, elev, aspect):
    target = np.array([0.0, 0.0, 0.0], dtype=np.float32)
    dist = 12.0

    eye = target + dist * np.array([
        math.cos(elev) * math.sin(angle),
        math.sin(elev),
        math.cos(elev) * math.cos(angle)
    ], dtype=np.float32)

    V = look_at(eye, target, np.array([0.0, 1.0, 0.0], dtype=np.float32))
    P = ortho(-6 * aspect, 6 * aspect, -6, 6, 0.1, 100.0)

    return (P @ V).astype(np.float32)


def main():
    if not glfw.init():
        sys.exit("Erro ao iniciar GLFW")

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    window = glfw.create_window(1000, 700, "Grid estilo Into the Breach", None, None)

    if not window:
        glfw.terminate()
        sys.exit("Erro ao criar janela")

    glfw.make_context_current(window)

    program = create_program()
    vertices = build_grid()
    vao, count = upload(vertices)

    glClearColor(0.08, 0.10, 0.14, 1.0)
    glEnable(GL_DEPTH_TEST)

    angle = math.radians(45)
    elev = math.radians(35)

    loc = glGetUniformLocation(program, "uMVP")

    while not glfw.window_should_close(window):
        glfw.poll_events()

        if glfw.get_key(window, glfw.KEY_LEFT) == glfw.PRESS:
            angle -= 0.02
        if glfw.get_key(window, glfw.KEY_RIGHT) == glfw.PRESS:
            angle += 0.02
        if glfw.get_key(window, glfw.KEY_UP) == glfw.PRESS:
            elev = min(math.radians(80), elev + 0.02)
        if glfw.get_key(window, glfw.KEY_DOWN) == glfw.PRESS:
            elev = max(math.radians(10), elev - 0.02)

        w, h = glfw.get_framebuffer_size(window)
        glViewport(0, 0, w, h)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        mvp = get_mvp(angle, elev, w / h)

        glUseProgram(program)
        glUniformMatrix4fv(loc, 1, GL_TRUE, mvp)

        glBindVertexArray(vao)
        glDrawArrays(GL_TRIANGLES, 0, count)

        glfw.swap_buffers(window)

    glfw.terminate()


if __name__ == "__main__":
    main()
