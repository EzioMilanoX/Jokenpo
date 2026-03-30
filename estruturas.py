
class Rodada:
    """
    Classe que representa a entidade do jogo. 
    Ela guarda todos os dados de um turno que aconteceu.
    """
    def __init__(self, id_rodada, j1_nome, j1_jogada, j2_nome, j2_jogada, resultado):
        self.id_rodada = id_rodada   # Número da rodada (1, 2, 3...)
        self.j1_nome = j1_nome       # Nome do Jogador 1 (ou Host)
        self.j1_jogada = j1_jogada   # O que o J1 jogou
        self.j2_nome = j2_nome       # Nome do Jogador 2 (ou Cliente/Robô)
        self.j2_jogada = j2_jogada   # O que o J2 jogou
        self.resultado = resultado   # Quem ganhou ou se foi 'Empate'

    def __str__(self):
        # Formata como a rodada será lida no relatório
        return f"Rodada {self.id_rodada}: {self.j1_nome} ({self.j1_jogada}) vs {self.j2_nome} ({self.j2_jogada}) | Venceu: {self.resultado}"

class No:
    """
    Classe Nó. 
    Guarda o dado (a Rodada) e o ponteiro para o próximo Nó da fila.
    """
    def __init__(self, valor):
        self.valor = valor    # Recebe o objeto Rodada
        self.proximo = None   # Aponta para o vazio inicialmente

    def mostrar_no(self):
        print(self.valor)

class ListaEncadeada:
    """
    Classe da Lista Encadeada (Linked List).
    Gerencia as rodadas válidas da partida atual.
    """
    def __init__(self):
        self.primeiro = None  # O início da lista (cabeça)

    # REQUISITO 1: INCLUSÃO
    def adicionar(self, valor):
        """Adiciona uma nova rodada no final da lista."""
        novo_no = No(valor)
        if self.primeiro is None:
            self.primeiro = novo_no # Se a lista estiver vazia, ele é o primeiro
        else:
            atual = self.primeiro
            while atual.proximo is not None: # Percorre até achar o último
                atual = atual.proximo
            atual.proximo = novo_no # Pendura o novo nó no final

    # REQUISITO 2: EXCLUSÃO
    def remover(self, id_rodada):
        """Remove um nó específico (usado para anular empates)."""
        atual = self.primeiro
        anterior = None

        # Busca a rodada pelo ID
        while atual is not None and atual.valor.id_rodada != id_rodada:
            anterior = atual
            atual = atual.proximo

        if atual is None: return # Não achou a rodada
        
        # Desconecta o nó da lista (o Python limpa da memória depois)
        if anterior is None:
            self.primeiro = atual.proximo # Removendo o primeiro elemento
        else:
            anterior.proximo = atual.proximo # O anterior "pula" o nó atual
            
    # REQUISITO 3: CONSULTA
    def consultar(self, nome_j1, nome_j2):
        """Varre a lista para contar quantas vitórias cada um tem no momento."""
        vit_j1, vit_j2 = 0, 0
        atual = self.primeiro
        while atual is not None:
            if atual.valor.resultado == nome_j1: 
                vit_j1 += 1
            elif atual.valor.resultado == nome_j2: 
                vit_j2 += 1
            atual = atual.proximo
        return vit_j1, vit_j2

    # REQUISITO 4: RELATÓRIO 
    def relatorio(self, vencedor_final):
        """Gera o texto final do histórico da partida e usa o mostrar_no()"""
        texto = ""
        if self.primeiro is None: return "Sem rodadas válidas."
        
        atual = self.primeiro
        while atual is not None:
            atual.mostrar_no() # Imprime no console
            texto += str(atual.valor) + "\n" # Salva no texto da interface gráfica
            atual = atual.proximo
            
        texto += f"\n🏆 GRANDE CAMPEÃO: {vencedor_final.upper()} 🏆"
        return texto