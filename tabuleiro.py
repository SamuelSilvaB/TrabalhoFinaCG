import glfw
from OpenGL.GL import *
import numpy as np
import ctypes
import math

from pecas import *
from utils import lerp, carregar_textura
from renderizacao import build_grid, gerar_vertices_pecas
from geometria import carregar_modelo_base

class Tabuleiro:
    def __init__(self):
        vertices = build_grid()
        self.qtdVertices = len(vertices) // 8

        self.casas = [[None for _ in range(8)] for _ in range(8)]
        self.pecas = []

        # Jogador 1
        self.adicionar_peca(Tanque(0, 6, 6))
        self.adicionar_peca(Atirador(0, 3, 7))
        self.adicionar_peca(Batedor(0, 1, 5))

        # jogador 2
        self.adicionar_peca(Tanque(1, 0, 0))
        self.adicionar_peca(Atirador(1, 3, 2))
        self.adicionar_peca(Batedor(1, 7, 0))

        self.peca_selecionada = None
        self.modo_ataque = False

        self.textura_piso = carregar_textura("woodfloor2.jpg")

        print("Carregando os modelos 3D...")
        self.modelo_soldado = carregar_modelo_base("soldado.glb", escala = 30.0)
        self.modelo_robo = carregar_modelo_base("robozurg.glb", escala = 0.02)

        # Configurar VAO/VBO para o grid (estático)
        self.vaoId = glGenVertexArrays(1)
        glBindVertexArray(self.vaoId)

        self.vboId = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vboId)
        glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

        stride = 8 * 4
        glEnableVertexAttribArray(0) # Posiçao 0
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1) # Cor 1
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2) # Textura UV 2
        glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(24))

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

        pecas_para_remover = []

        for peca in self.pecas:

            # -------------------
            # Movimento
            # -------------------
            if peca.animando:

                peca.tempo_animacao += dt

                t = peca.tempo_animacao / peca.duracao_animacao
                t = min(t, 1.0)

                t = t * t * (3 - 2 * t)

                if t >= 1.0:
                    t = 1.0
                    peca.animando = False

                peca.x_visual = lerp(
                    peca.x_inicial,
                    peca.x_destino,
                    t
                )

                peca.z_visual = lerp(
                    peca.z_inicial,
                    peca.z_destino,
                    t
                )

                if peca.animando:
                    peca.y_visual = (
                        math.sin(t * math.pi)
                        * 0.5
                    )
                else:
                    peca.y_visual = 0.0

            # -------------------
            # Dano
            # -------------------
            if peca.recebendo_dano:

                peca.tempo_dano += dt

                if peca.tempo_dano >= peca.duracao_dano:

                    peca.recebendo_dano = False

                    peca.offset_dano_x = 0.0
                    peca.offset_dano_z = 0.0

                    if peca.morta:
                        pecas_para_remover.append(peca)

                else:

                    intensidade = 0.08

                    if int(peca.tempo_dano * 50) % 2 == 0:
                        peca.offset_dano_x = intensidade
                    else:
                        peca.offset_dano_x = -intensidade

                    peca.offset_dano_z = 0.0

        # -------------------
        # Remove peças mortas
        # -------------------
        for peca in pecas_para_remover:

            if peca in self.pecas:

                self.casas[
                    peca.linha
                ][
                    peca.coluna
                ] = None

                self.pecas.remove(peca)

                print(f"{peca.tipo} removida do jogo")

    def atacar(self, atacante, linha, coluna):

        alvo = self.obter_peca(
            linha,
            coluna
        )

        if atacante.atacou:
            print(
                "Esta peça já atacou neste turno!"
            )
            return False

        if alvo is None:
            return False

        if alvo.morta:
            return False

        if alvo.jogador == atacante.jogador:
            return False

        distancia = (
            abs(linha - atacante.linha)
            +
            abs(coluna - atacante.coluna)
        )

        if distancia == 0:
            return False

        if distancia > atacante.alcance_do_ataque:
            return False

        alvo.vida -= atacante.dano

        print(
            f"{alvo.tipo} recebeu "
            f"{atacante.dano} de dano"
        )

        print(
            f"Vida restante: "
            f"{alvo.vida}"
        )

        alvo.recebendo_dano = True
        alvo.tempo_dano = 0.0

        if alvo.vida <= 0:

            alvo.morta = True

            print(
                f"{alvo.tipo} será destruído"
            )

        print(
            f"{atacante.tipo} atacou "
            f"{alvo.tipo}"
        )

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
        # Textura Carregada
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.textura_piso)

        # Desenhando o grid estático
        glBindVertexArray(self.vaoId)
        glDrawArrays(GL_TRIANGLES, 0, self.qtdVertices)
        glBindVertexArray(0)

        # Desvincula a textura para não afetar as peças dinâmicas
        glBindTexture(GL_TEXTURE_2D, 0)

        # Desenhando peças e auras (dinâmico)
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