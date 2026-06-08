import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
import math

from pecas import Peca
from utils import lerp
from renderizacao import build_grid, gerar_vertices_pecas

class Tabuleiro:
    def __init__(self):
        vertices = build_grid()
        self.qtdVertices = len(vertices) // 6

        self.casas = [[None for _ in range(8)] for _ in range(8)]
        self.pecas = []

        self.adicionar_peca(Peca("cubo", 0, 6, 6))
        self.adicionar_peca(Peca("cubo", 0, 3, 7))
        self.adicionar_peca(Peca("cubo", 0, 1, 5))
        self.adicionar_peca(Peca("esfera", 1, 0, 0))
        self.adicionar_peca(Peca("esfera", 1, 3, 2))
        self.adicionar_peca(Peca("esfera", 1, 7, 0))

        self.peca_selecionada = None
        self.modo_ataque = False

        # Configurar VAO/VBO para o grid (estático)
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        stride = 6 * 4
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

        glBindVertexArray(0)

    def adicionar_peca(self, peca):
        self.pecas.append(peca)
        self.casas[peca.linha][peca.coluna] = peca

    def obter_peca(self, linha, coluna):
        for peca in self.pecas:
            if peca.linha == linha and peca.coluna == coluna:
                return peca
        return None

    def mover_peca(self, peca, linha, coluna):
        if peca.movido:
            print("Esta peça já se moveu neste turno!")
            return False
        if linha < 0 or linha > 7 or coluna < 0 or coluna > 7:
            return False
        if self.obter_peca(linha, coluna) is not None:
            return False

        distancia = abs(linha - peca.linha) + abs(coluna - peca.coluna)
        if distancia > peca.movimento:
            print(f"Movimento muito longo ({distancia}) máximo = {peca.movimento}")
            return False

        peca.x_inicial = peca.x_visual
        peca.z_inicial = peca.z_visual
        peca.x_destino = coluna - 4
        peca.z_destino = linha - 4
        peca.tempo_animacao = 0.0
        peca.animando = True
        peca.linha = linha
        peca.coluna = coluna
        peca.movido = True
        return True

    def casas_atacaveis(self, peca):
        casas = []
        alcance = peca.alcance_do_ataque
        for linha in range(8):
            for coluna in range(8):
                distancia = abs(linha - peca.linha) + abs(coluna - peca.coluna)
                if 0 < distancia <= alcance:
                    casas.append((linha, coluna))
        return casas

    def atualizar_animacoes(self, dt):
        for peca in self.pecas:
            if not peca.animando:
                continue
            peca.tempo_animacao += dt
            t = peca.tempo_animacao / peca.duracao_animacao
            t = min(t, 1.0)
            t = t * t * (3 - 2 * t)   # easing
            if t >= 1.0:
                t = 1.0
                peca.animando = False
            peca.x_visual = lerp(peca.x_inicial, peca.x_destino, t)
            peca.z_visual = lerp(peca.z_inicial, peca.z_destino, t)
            if peca.animando:
                peca.y_visual = math.sin(t * math.pi) * 0.5
            else:
                peca.y_visual = 0.0

    def atacar(self, atacante, linha, coluna):
        alvo = self.obter_peca(linha, coluna)
        if atacante.atacou:
            print("Esta peça já atacou neste turno!")
            return False

        if alvo is None or alvo.jogador == atacante.jogador:
            return False
        distancia = abs(linha - atacante.linha) + abs(coluna - atacante.coluna)
        if distancia > atacante.alcance_do_ataque:
            return False
        self.pecas.remove(alvo)
        self.casas[alvo.linha][alvo.coluna] = None
        print(f"{atacante.tipo} atacou {alvo.tipo}")
        atacante.atacou = True
        return True

    def remover_peca(self, peca):
        self.pecas.remove(peca)
        self.casas[peca.linha][peca.coluna] = None

    def casas_alcancaveis(self, peca):
        casas = []
        for linha in range(8):
            for coluna in range(8):
                distancia = abs(linha - peca.linha) + abs(coluna - peca.coluna)
                if distancia <= peca.movimento and self.obter_peca(linha, coluna) is None:
                    casas.append((linha, coluna))
        return casas
    
    def iniciar_turno(self, jogador):
        for peca in self.pecas:
            if peca.jogador == jogador:
                peca.movido = False
                peca.atacou = False
        print(f"Turno do jogador {jogador} começou!")

    def tem_alvos_validos(self, peca):
        """Retorna True se a peça tem pelo menos um inimigo ao alcance de ataque."""
        for linha in range(8):
            for coluna in range(8):
                alvo = self.obter_peca(linha, coluna)
                if alvo and alvo.jogador != peca.jogador:
                    distancia = abs(linha - peca.linha) + abs(coluna - peca.coluna)
                    if distancia <= peca.alcance_do_ataque:
                        return True
        return False

    def turno_acabou(self, jogador):
        """Retorna True se todas as peças do jogador já moveram E atacaram."""
        for peca in self.pecas:
            if peca.jogador == jogador and (not peca.movido or not peca.atacou):
                return False
        return True

    def render(self):
        # Desenha o grid estático
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices)
        glBindVertexArray(0)

        # Desenha peças e auras (dinâmico)
        vertices = gerar_vertices_pecas(self)
        vao = glGenVertexArrays(1)
        vbo = glGenBuffers(1)
        glBindVertexArray(vao)
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

        stride = 6 * 4
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))

        glDrawArrays(GL_TRIANGLES, 0, len(vertices) // 6)

        glBindVertexArray(0)
        glDeleteBuffers(1, [vbo])
        glDeleteVertexArrays(1, [vao])