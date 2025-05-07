import pygame
import sys
import math
from queue import PriorityQueue
import random 

pygame.init()

LARGURA = 800
ALTURA = 600
TAMANHO_CELULA = 40
LINHAS = ALTURA // TAMANHO_CELULA
COLUNAS = LARGURA // TAMANHO_CELULA

BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
VERMELHO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (0, 0, 255)

tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Tower Defense")

class Torre:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.raio_curto = 2
        self.raio_longo = 4

    def desenhar(self):
        pos = (self.x * TAMANHO_CELULA + TAMANHO_CELULA // 2,
               self.y * TAMANHO_CELULA + TAMANHO_CELULA //2)
        
        superficie_longo = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        superficie_curto = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        
        pygame.draw.circle(superficie_longo, (230, 190, 255, 100), pos, self.raio_longo * TAMANHO_CELULA)
        pygame.draw.circle(superficie_curto, (147, 112, 219, 150), pos, self.raio_curto * TAMANHO_CELULA)
        
        tela.blit(superficie_longo, (0, 0))
        tela.blit(superficie_curto, (0, 0))
        pygame.draw.circle(tela, VERMELHO, pos, TAMANHO_CELULA // 2)

    def calcular_dano(self, x, y):
        distancia = math.sqrt((self.x - x)**2 + (self.y - y)**2)
        if distancia <= self.raio_curto:
            return 20
        elif distancia <= self.raio_longo:
            return 10
        return 0

class Jogo:
    def __init__(self):
        self.torres = []
        for _ in range(5):
            x = random.randint(0, COLUNAS-1)
            y = random.randint(0, LINHAS-1)
            while (x < 2 and y == LINHAS // 2) or (x > COLUNAS-3 and y == LINHAS // 2):
                x = random.randint(0, COLUNAS-1)
                y = random.randint(0, LINHAS-1)
            self.torres.append(Torre(x, y))
        
        self.inicio = (0, LINHAS // 2)
        self.fim = (19, LINHAS // 2)
        self.nos_explorados = 0
        self.pontos_perdidos = 0

    def heuristica(self, pos1, pos2):
        x1, y1 = pos1
        x2, y2 = pos2
        return abs(x1 - x2) + abs(y1 - y2)

    def obter_vizinhos(self, pos):
        x, y = pos
        vizinhos = []
        direcoes = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        
        for dx, dy in direcoes:
            novo_x, novo_y = x + dx, y + dy
            if 0 <= novo_x < COLUNAS and 0 <= novo_y < LINHAS:
                vizinhos.append((novo_x, novo_y))
        return vizinhos

    def encontrar_caminho(self):
        fronteira = PriorityQueue()
        fronteira.put((0, self.inicio))
        veio_de = {self.inicio: None}
        custo_ate_agora = {self.inicio: 0}
        self.nos_explorados = 0

        while not fronteira.empty():
            atual = fronteira.get()[1]
            self.nos_explorados += 1

            if atual == self.fim:
                self.pontos_perdidos = custo_ate_agora[atual]
                break

            for proximo in self.obter_vizinhos(atual):
                dano = 0 if proximo == self.fim else sum(torre.calcular_dano(*proximo) for torre in self.torres)
                novo_custo = custo_ate_agora[atual] + dano

                if proximo not in custo_ate_agora or novo_custo < custo_ate_agora[proximo]:
                    custo_ate_agora[proximo] = novo_custo
                    prioridade = novo_custo + self.heuristica(proximo, self.fim)
                    fronteira.put((prioridade, proximo))
                    veio_de[proximo] = atual

        return self.reconstruir_caminho(veio_de)

    def desenhar(self):
        for x in range(0, LARGURA, TAMANHO_CELULA):
            pygame.draw.line(tela, PRETO, (x, 0), (x, ALTURA))
        for y in range(0, ALTURA, TAMANHO_CELULA):
            pygame.draw.line(tela, PRETO, (0, y), (LARGURA, y))

        for torre in self.torres:
            torre.desenhar()

        pygame.draw.rect(tela, VERDE, (self.inicio[0] * TAMANHO_CELULA,
                                     self.inicio[1] * TAMANHO_CELULA,
                                     TAMANHO_CELULA, TAMANHO_CELULA))
        pygame.draw.rect(tela, AZUL, (self.fim[0] * TAMANHO_CELULA,
                                    self.fim[1] * TAMANHO_CELULA,
                                    TAMANHO_CELULA, TAMANHO_CELULA))

        fonte = pygame.font.Font(None, 36)
        info_pontos = fonte.render(f'Pontos Perdidos: {self.pontos_perdidos}', True, PRETO)
        info_nos = fonte.render(f'Nós Explorados: {self.nos_explorados}', True, PRETO)
        tela.blit(info_pontos, (10, 10))
        tela.blit(info_nos, (10, 50))

    def reconstruir_caminho(self, veio_de):
        atual = self.fim
        caminho = []
        while atual is not None:
            caminho.append(atual)
            atual = veio_de.get(atual)
        return caminho[::-1]

def main():
    jogo = Jogo()
    clock = pygame.time.Clock()
    caminho = jogo.encontrar_caminho()
    fonte = pygame.font.Font(None, 24)
    
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        tela.fill(BRANCO)
        jogo.desenhar()

        if caminho:
            for i in range(len(caminho) - 1):
                pos1 = (caminho[i][0] * TAMANHO_CELULA + TAMANHO_CELULA // 2,
                       caminho[i][1] * TAMANHO_CELULA + TAMANHO_CELULA // 2)
                pos2 = (caminho[i + 1][0] * TAMANHO_CELULA + TAMANHO_CELULA // 2,
                       caminho[i + 1][1] * TAMANHO_CELULA + TAMANHO_CELULA // 2)
                pygame.draw.line(tela, VERDE, pos1, pos2, 2)
                
                if caminho[i] != jogo.fim and caminho[i] != jogo.inicio:
                    dano = sum(torre.calcular_dano(caminho[i][0], caminho[i][1]) for torre in jogo.torres)
                    if dano > 0:
                        texto_dano = fonte.render(f'-{dano}', True, VERMELHO)
                        tela.blit(texto_dano, (caminho[i][0] * TAMANHO_CELULA + 5,
                                             caminho[i][1] * TAMANHO_CELULA + 5))

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()