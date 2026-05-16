import glfw
from OpenGL.GL import *
import numpy as np
import math
import sys
import ctypes
import os

def add_tile(x, z, size, color, h=0.90, ybase=0.0):
    x0, x1 = x, x + size
    y0, y1 = ybase, ybase + h
    z0, z1 = z, z + size
    r, g, b = color
    top = (min(r + 0.08, 1.0), min(g + 0.08, 1.0), min(b + 0.08, 1.0))
    side = (r * 0.72, g * 0.72, b * 0.72)
    tr, tg, tb = top
    sr, sg, sb = side

    return [
        #topo
        x0, y1, z0, tr, tg, tb, 
        x1, y1, z0, tr, tg, tb, 
        x1, y1, z1, tr, tg, tb,
        x0, y1, z0, tr, tg, tb, 
        x1, y1, z1, tr, tg, tb, 
        x0, y1, z1, tr, tg, tb,
        #frente
        x0, y0, z1, sr, sg, sb, 
        x1, y0, z1, sr, sg, sb, 
        x1, y1, z1, sr, sg, sb,
        x0, y0, z1, sr, sg, sb, 
        x1, y1, z1, sr, sg, sb, 
        x0, y1, z1, sr, sg, sb,
        #direita
        x1, y0, z0, sr, sg, sb, 
        x1, y0, z1, sr, sg, sb, 
        x1, y1, z1, sr, sg, sb,
        x1, y0, z0, sr, sg, sb, 
        x1, y1, z1, sr, sg, sb, 
        x1, y1, z0, sr, sg, sb,
        #esquerda
        x0, y0, z1, sr, sg, sb, 
        x0, y0, z0, sr, sg, sb, 
        x0, y1, z0, sr, sg, sb,
        x0, y0, z1, sr, sg, sb, 
        x0, y1, z0, sr, sg, sb, 
        x0, y1, z1, sr, sg, sb,
        #atrás
        x1, y0, z0, sr, sg, sb, 
        x0, y0, z0, sr, sg, sb, 
        x0, y1, z0, sr, sg, sb,
        x1, y0, z0, sr, sg, sb, 
        x0, y1, z0, sr, sg, sb, 
        x1, y1, z0, sr, sg, sb,
    ]

def build_grid():
    SIZE, GRID = 1.0, 8
    LIGHT, DARK = (0.78, 0.86, 0.90), (0.38, 0.52, 0.60)
    PISO_COR = (0.1, 0.1, 0.1)
    data = []
    offset = GRID / 2

    # Piso
    piso_tamanho = GRID * SIZE + 25.0
    data += add_tile(-piso_tamanho/2, -piso_tamanho/2, piso_tamanho, PISO_COR, h=0.1, ybase=-0.5)

    # Tabuleiro
    for row in range(GRID):
        for col in range(GRID):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            data += add_tile(col - offset, row - offset, SIZE, color, h=0.9, ybase=0.0)
    return np.array(data, dtype=np.float32)

class Tabuleiro:
    def __init__(self):
        vertices = build_grid()
        self.qtdVertices = len(vertices) // 6

        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)
        
        vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        stride = 6 * 4
        glEnableVertexAttribArray(0) # Posição
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1) # Cor
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        
        glBindVertexArray(0)

    def render(self):
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices)
        glBindVertexArray(0)