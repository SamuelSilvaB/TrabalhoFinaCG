import numpy as np
from geometria import add_tile, centralizar_cubo, add_esfera, add_aura

def build_grid():
    SIZE = 1.0
    GRID = 8
    LIGHT = (0.78, 0.86, 0.90)
    DARK = (0.38, 0.52, 0.60)
    PISO_COR = (0.3, 0.3, 0.3)

    data = []
    offset = GRID / 2
    piso_tamanho = GRID * SIZE + 25.0

    # Piso
    data += add_tile(-piso_tamanho / 2, -piso_tamanho / 2, piso_tamanho, PISO_COR, h=0.1, ybase=-0.5, com_textura=True)

    # Tabuleiro
    for row in range(GRID):
        for col in range(GRID):
            color = LIGHT if (row + col) % 2 == 0 else DARK
            data += add_tile(col - offset, row - offset, SIZE, color, h=0.9, ybase=0.0)

    return np.array(data, dtype=np.float32)

def gerar_vertices_pecas(tabuleiro):
    """Recebe o objeto Tabuleiro e gera os vértices das peças e auras."""
    vertices = []

    # Mostrar casas de movimento (se houver peça selecionada)
    if tabuleiro.peca_selecionada is not None and not tabuleiro.peca_selecionada.movido:
        for linha, coluna in tabuleiro.casas_alcancaveis(tabuleiro.peca_selecionada):
            casa_x = coluna - 4
            casa_z = linha - 4
            vertices += add_aura(casa_x + 0.5, casa_z + 0.5, raio=0.25, y=0.91, cor=(0.2, 0.6, 1.0))

    # Desenhar peças
    for peca in tabuleiro.pecas:
        x = peca.x_visual
        z = peca.z_visual

        # aura da peça selecionada
        if peca == tabuleiro.peca_selecionada:
            vertices += add_aura(x + 0.5, z + 0.5, raio=0.55, cor=(1.0, 1.0, 0.0))

        if peca.tipo == "cubo":
            vertices += centralizar_cubo(x, z, 0.6, (1.0, 0.2, 0.2), 0.9 + peca.y_visual)
        elif peca.tipo == "esfera":
            vertices += add_esfera(x + 0.5, 1.2 + peca.y_visual, z + 0.5, 0.35, (0.2, 1.0, 0.2))

    # Mostrar casas disponíveis para ataque
    if tabuleiro.modo_ataque and tabuleiro.peca_selecionada is not None:
        for linha, coluna in tabuleiro.casas_atacaveis(tabuleiro.peca_selecionada):
            x = coluna - 4
            z = linha - 4
            vertices += add_aura(x + 0.5, z + 0.5, raio=0.3, cor=(1.0, 0.0, 0.0))

    return np.array(vertices, dtype=np.float32)