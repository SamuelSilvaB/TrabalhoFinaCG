import math
from OpenGL.GL import *

def add_cube(x, y, z, size, color):
    x0, x1 = x, x + size
    y0, y1 = y, y + size
    z0, z1 = z, z + size

    r, g, b = color

    top = (min(r + 0.08, 1.0), min(g + 0.08, 1.0), min(b + 0.08, 1.0))
    side = (r * 0.72, g * 0.72, b * 0.72)

    tr, tg, tb = top
    sr, sg, sb = side

    return [
        # top
        x0, y1, z0, tr, tg, tb,
        x1, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,
        x0, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,
        x0, y1, z1, tr, tg, tb,
        # side -Z
        x0, y0, z1, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x0, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,
        # side +X
        x1, y0, z0, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x1, y0, z0, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,
        # side -X
        x0, y0, z1, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x0, y0, z1, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,
        # side +Z
        x1, y0, z0, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x1, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,
    ]

def centralizar_cubo(tile_x, tile_z, cube_size, color, y=0.9):
    x = tile_x + (1.0 - cube_size) / 2
    z = tile_z + (1.0 - cube_size) / 2
    return add_cube(x, y, z, cube_size, color)

def add_paralelepipedo(x, y, z, largura, altura, profundidade, cor):
    x0, x1 = x, x + largura
    y0, y1 = y, y + altura
    z0, z1 = z, z + profundidade

    r, g, b = cor
    top = (min(r + 0.08, 1.0), min(g + 0.08, 1.0), min(b + 0.08, 1.0))
    side = (r * 0.72, g * 0.72, b * 0.72)
    tr, tg, tb = top
    sr, sg, sb = side

    return [
        # top
        x0, y1, z0, tr, tg, tb,
        x1, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,
        x0, y1, z0, tr, tg, tb,
        x1, y1, z1, tr, tg, tb,
        x0, y1, z1, tr, tg, tb,
        # side -Z
        x0, y0, z1, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x0, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,
        # side +X
        x1, y0, z0, sr, sg, sb,
        x1, y0, z1, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x1, y0, z0, sr, sg, sb,
        x1, y1, z1, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,
        # side -X
        x0, y0, z1, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x0, y0, z1, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x0, y1, z1, sr, sg, sb,
        # side +Z
        x1, y0, z0, sr, sg, sb,
        x0, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x1, y0, z0, sr, sg, sb,
        x0, y1, z0, sr, sg, sb,
        x1, y1, z0, sr, sg, sb,
    ]

def add_esfera(cx, cy, cz, raio, cor, setores=24, camadas=24):
    vertices = []
    r, g, b = cor
    for i in range(camadas):
        camada_angulo1 = math.pi / 2 - i * math.pi / camadas
        camada_angulo2 = math.pi / 2 - (i + 1) * math.pi / camadas
        xy1 = raio * math.cos(camada_angulo1)
        y1 = raio * math.sin(camada_angulo1)
        xy2 = raio * math.cos(camada_angulo2)
        y2 = raio * math.sin(camada_angulo2)
        for j in range(setores):
            setor_angulo1 = j * 2 * math.pi / setores
            setor_angulo2 = (j + 1) * 2 * math.pi / setores
            x1 = xy1 * math.cos(setor_angulo1)
            z1 = xy1 * math.sin(setor_angulo1)
            x2 = xy2 * math.cos(setor_angulo1)
            z2 = xy2 * math.sin(setor_angulo1)
            x3 = xy2 * math.cos(setor_angulo2)
            z3 = xy2 * math.sin(setor_angulo2)
            x4 = xy1 * math.cos(setor_angulo2)
            z4 = xy1 * math.sin(setor_angulo2)
            vertices += [
                cx + x1, cy + y1, cz + z1, r, g, b,
                cx + x2, cy + y2, cz + z2, r, g, b,
                cx + x3, cy + y2, cz + z3, r, g, b,
                cx + x1, cy + y1, cz + z1, r, g, b,
                cx + x3, cy + y2, cz + z3, r, g, b,
                cx + x4, cy + y1, cz + z4, r, g, b,
            ]
    return vertices

def add_aura(cx, cz, raio=0.45, y=0.92, cor=(1.0, 1.0, 0.0), segmentos=32):
    vertices = []
    r, g, b = cor
    for i in range(segmentos):
        a1 = (i / segmentos) * 2 * math.pi
        a2 = ((i + 1) / segmentos) * 2 * math.pi
        vertices += [
            cx, y, cz, r, g, b,
            cx + math.cos(a1) * raio, y, cz + math.sin(a1) * raio, r, g, b,
            cx + math.cos(a2) * raio, y, cz + math.sin(a2) * raio, r, g, b,
        ]
    return vertices

def add_tile(x, z, size, color, h=0.90, ybase=0.0, com_textura=False):
    x0, x1 = x, x + size
    y0, y1 = ybase, ybase + h
    z0, z1 = z, z + size

    r, g, b = color
    top = (min(r + 0.08, 1.0), min(g + 0.08, 1.0), min(b + 0.08, 1.0))
    side = (r * 0.72, g * 0.72, b * 0.72)
    tr, tg, tb = top
    sr, sg, sb = side

    # Mágica: Se for 'com_textura=True', passamos as coordenadas normais.
    # Se for 'False', passamos tudo 0.0 (o que avisa o shader para pintar cor sólida).
    u_esq, v_cim = (0.0, 1.0) if com_textura else (0.0, 0.0)
    u_dir, v_cim = (1.0, 1.0) if com_textura else (0.0, 0.0)
    u_dir, v_bai = (1.0, 0.0) if com_textura else (0.0, 0.0)
    u_esq, v_bai = (0.0, 0.0)

    return [
        # Topo
        x0, y1, z0, tr, tg, tb, u_esq, v_cim,
        x1, y1, z0, tr, tg, tb, u_dir, v_cim,
        x1, y1, z1, tr, tg, tb, u_dir, v_bai,
        x0, y1, z0, tr, tg, tb, u_esq, v_cim,
        x1, y1, z1, tr, tg, tb, u_dir, v_bai,
        x0, y1, z1, tr, tg, tb, u_esq, v_bai,
        # Frente
        x0, y0, z1, sr, sg, sb, 0.0, 0.0,
        x1, y0, z1, sr, sg, sb, 0.0, 0.0,
        x1, y1, z1, sr, sg, sb, 0.0, 0.0,
        x0, y0, z1, sr, sg, sb, 0.0, 0.0,
        x1, y1, z1, sr, sg, sb, 0.0, 0.0,
        x0, y1, z1, sr, sg, sb, 0.0, 0.0,
        # Direita
        x1, y0, z0, sr, sg, sb, 0.0, 0.0,
        x1, y0, z1, sr, sg, sb, 0.0, 0.0,
        x1, y1, z1, sr, sg, sb, 0.0, 0.0,
        x1, y0, z0, sr, sg, sb, 0.0, 0.0,
        x1, y1, z1, sr, sg, sb, 0.0, 0.0,
        x1, y1, z0, sr, sg, sb, 0.0, 0.0,
        # Esquerda
        x0, y0, z1, sr, sg, sb, 0.0, 0.0,
        x0, y0, z0, sr, sg, sb, 0.0, 0.0,
        x0, y1, z0, sr, sg, sb, 0.0, 0.0,
        x0, y0, z1, sr, sg, sb, 0.0, 0.0,
        x0, y1, z0, sr, sg, sb, 0.0, 0.0,
        x0, y1, z1, sr, sg, sb, 0.0, 0.0,
        # Trás
        x1, y0, z0, sr, sg, sb, 0.0, 0.0,
        x0, y0, z0, sr, sg, sb, 0.0, 0.0,
        x0, y1, z0, sr, sg, sb, 0.0, 0.0,
        x1, y0, z0, sr, sg, sb, 0.0, 0.0,
        x0, y1, z0, sr, sg, sb, 0.0, 0.0,
        x1, y1, z0, sr, sg, sb, 0.0, 0.0
    ]