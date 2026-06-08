class Peca:
    def __init__(self, tipo, jogador, linha, coluna):
        self.tipo = tipo
        self.jogador = jogador
        self.linha = linha
        self.coluna = coluna
        self.movimento = 2          # alcance de movimento
        self.x_visual = coluna - 4
        self.z_visual = linha - 4
        self.animando = False
        self.x_inicial = self.x_visual
        self.z_inicial = self.z_visual
        self.x_destino = self.x_visual
        self.z_destino = self.z_visual
        self.y_visual = 0.0
        self.tempo_animacao = 0.0
        self.duracao_animacao = 0.25
        self.vida = 3
        self.dano = 1
        self.alcance_do_ataque = 1
        self.direcao = (0, -1)
        # Atridutos para saber ose o jogador jamoveu e atacou no turno.
        self.movido = False
        self.atacou = False