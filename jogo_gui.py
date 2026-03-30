import tkinter as tk
import socket
import threading
import random
# IMPORTANTE: Importando as classes dos outros arquivos
from estruturas import ListaEncadeada, Rodada
from interface import ModalEntrada, ModalAviso, pegar_ip_local

class JogoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Torneio - Jokenpô")
        self.root.geometry("550x500")
        self.root.configure(bg="#1E1E2E")
        
        # Histórico que não é apagado (guarda os vencedores de todas as partidas)
        self.historico_geral_partidas = []
        
        # MEMÓRIA DA INTELIGÊNCIA ARTIFICIAL (Q-Table)
        # Ela guarda notas. Ex: Se você jogar pedra e ela jogar papel e ganhar, ela anota +1.
        # Como está no __init__, a memória persiste! O robô fica mais inteligente a cada nova partida.
        self.memoria_robo = {
            'pedra': {'pedra': 0, 'papel': 0, 'tesoura': 0},
            'papel': {'pedra': 0, 'papel': 0, 'tesoura': 0},
            'tesoura': {'pedra': 0, 'papel': 0, 'tesoura': 0}
        }
        
        self.conn = None # Guarda a conexão de rede
        self.meu_nome = "Jogador"
        self.modo_jogo = None
        
        self.construir_tela_menu()

    def limpar_tela(self):
        """Apaga tudo que está na janela para desenhar outra tela."""
        for widget in self.root.winfo_children():
            widget.destroy()

    def pedir_meu_nome(self, nome_padrao):
        """Pede o nome. Se o usuário só apertar Enter, usa o nome padrão."""
        dlg = ModalEntrada(self.root, "Seu Nome", "Digite seu nome (ou Enter para padrão):")
        if dlg.resultado and dlg.resultado.strip():
            self.meu_nome = dlg.resultado.strip()
        else:
            self.meu_nome = nome_padrao

    def gerenciar_queda_conexao(self):
        """Acionado se o socket falhar (ex: o amigo fechou o jogo)."""
        if self.modo_jogo == "multi":
            self.conn = None
            ModalAviso(self.root, "Conexão Perdida", "O adversário se desconectou ou saiu da partida.", "#F38BA8")
            self.voltar_ao_menu()

    # ----------------------------------------------------------------
    # TELAS PRINCIPAIS E NAVEGAÇÃO
    # ----------------------------------------------------------------
    def construir_tela_menu(self):
        self.limpar_tela()
        tk.Label(self.root, text="JOKENPÔ - MENU PRINCIPAL", font=("Segoe UI", 18, "bold"), bg="#1E1E2E", fg="#89B4FA").pack(pady=(40, 30))
        
        tk.Button(self.root, text="🤖 Jogar contra Robô (I.A)", font=("Segoe UI", 12, "bold"), bg="#CDD6F4", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", width=25, pady=10, command=self.iniciar_robo).pack(pady=10)
        tk.Button(self.root, text="🌐 Criar Sala (Hospedar)", font=("Segoe UI", 12, "bold"), bg="#A6E3A1", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", width=25, pady=10, command=self.hospedar).pack(pady=10)
        tk.Button(self.root, text="🔗 Entrar em Sala", font=("Segoe UI", 12, "bold"), bg="#F9E2AF", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", width=25, pady=10, command=self.conectar).pack(pady=10)
        tk.Button(self.root, text="📜 Ver Histórico de Partidas", font=("Segoe UI", 12, "bold"), bg="#F38BA8", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", width=25, pady=10, command=self.ver_historico).pack(pady=10)

    def iniciar_nova_partida(self):
        """Prepara o tabuleiro. Reinicia a lista encadeada, mas MANTÉM a rede aberta."""
        self.lista = ListaEncadeada() # Cria uma lista zerada para a nova partida
        self.id_geral_rodadas = 1
        self.minha_jogada = None
        self.jogada_adv = None
        self.limpar_tela()
        self.construir_tela_jogo()
        self.atualizar_tela_inicio_turno()

    # ----------------------------------------------------------------
    # PREPARAÇÃO DOS MODOS (Singleplayer e Multiplayer)
    # ----------------------------------------------------------------
    def iniciar_robo(self):
        self.modo_jogo = "robo"
        self.pedir_meu_nome("Anônimo")
        self.nome_adv = "Robô Hacker 🤖"
        self.iniciar_nova_partida()

    def hospedar(self):
        """Abre a porta do computador e aguarda alguém se conectar."""
        self.modo_jogo = "multi"
        self.is_host = True
        self.pedir_meu_nome("Host")
        
        # Criação do Socket Servidor (Ouvinte)
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', 5050)) # Escuta na porta 5050
        server.listen(1)
        
        codigo_sala = pegar_ip_local().split('.')[-1] # Cria o código curto
        self.limpar_tela()
        tk.Label(self.root, text=f"Aguardando jogador...\n\nCódigo da sua Sala: {codigo_sala}", font=("Segoe UI", 14, "bold"), bg="#1E1E2E", fg="#F38BA8").pack(pady=100)
        self.root.update()

        # accept() trava o código até o cliente bater na porta
        self.conn, addr = server.accept()
        
        # Troca os nomes pela rede assim que conectam
        self.conn.send(self.meu_nome.encode('utf-8'))
        self.nome_adv = self.conn.recv(1024).decode('utf-8')
        
        # Inicia uma Thread (linha de trabalho paralela) para ouvir a rede sem travar a tela
        threading.Thread(target=self.ouvir_rede, daemon=True).start()
        self.iniciar_nova_partida()

    def conectar(self):
        """Bate na porta do Host usando o IP ou o Código da Sala."""
        self.modo_jogo = "multi"
        self.is_host = False
        self.pedir_meu_nome("Cliente")
        
        dlg = ModalEntrada(self.root, "Código", "Digite o Código da Sala:")
        if not dlg.resultado: return
        codigo_sala = dlg.resultado.strip()
        
        # Tentativa de reconstruir o IP do amigo na rede Wi-Fi
        meu_ip = pegar_ip_local()
        partes_ip = meu_ip.split('.')
        partes_ip[-1] = codigo_sala 
        ip_host = '.'.join(partes_ip)
        
        # Exceção para testes na mesma máquina
        if codigo_sala in ["127.0.0.1", "localhost"]: ip_host = "127.0.0.1"
            
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.conn.connect((ip_host, 5050)) # Tenta conectar no Host
            
            # Troca de Nomes
            self.nome_adv = self.conn.recv(1024).decode('utf-8')
            self.conn.send(self.meu_nome.encode('utf-8'))
            
            # Inicia o ouvinte em segundo plano
            threading.Thread(target=self.ouvir_rede, daemon=True).start()
            self.iniciar_nova_partida()
        except:
            ModalAviso(self.root, "Erro", "Não foi possível achar a sala.", "#F38BA8")
            self.construir_tela_menu()

    def ouvir_rede(self):
        """Roda eternamente em 2º plano esperando a jogada do amigo chegar."""
        while self.conn: # Enquanto houver conexão
            try:
                msg = self.conn.recv(1024).decode('utf-8')
                if not msg: # Se a mensagem for vazia, a conexão caiu
                    break
                
                if msg in ['pedra', 'papel', 'tesoura']:
                    self.jogada_adv = msg
                    # Pede para a tela principal (Thread principal) processar o turno
                    self.root.after(0, self.verificar_resolucao)
            except:
                break # Sai do loop se der erro de rede
                
        # Se sair do loop `while`, a conexão caiu ou foi fechada
        if self.conn: 
            self.root.after(0, self.gerenciar_queda_conexao)

    # ----------------------------------------------------------------
    # TELA DE JOGO (Onde a partida acontece)
    # ----------------------------------------------------------------
    def construir_tela_jogo(self):
        self.lbl_placar = tk.Label(self.root, text="", font=("Segoe UI", 18, "bold"), bg="#1E1E2E", fg="#A6E3A1")
        self.lbl_placar.pack(pady=30)
        self.lbl_status = tk.Label(self.root, text="", font=("Segoe UI", 12), bg="#1E1E2E", fg="#CDD6F4")
        self.lbl_status.pack(pady=(15, 30))

        self.frame_botoes = tk.Frame(self.root, bg="#1E1E2E")
        self.frame_botoes.pack()

        self.btn_pedra = self.criar_botao("🪨 Pedra", "pedra")
        self.btn_papel = self.criar_botao("📄 Papel", "papel")
        self.btn_tesoura = self.criar_botao("✂️ Tesoura", "tesoura")

    def criar_botao(self, texto, jogada):
        btn = tk.Button(self.frame_botoes, text=texto, font=("Segoe UI", 12, "bold"), bg="#313244", fg="#CDD6F4", relief=tk.FLAT, cursor="hand2", width=12, pady=10, command=lambda: self.computar_minha_jogada(jogada))
        btn.bind("<Enter>", lambda e: btn.config(bg="#45475A"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#313244"))
        btn.pack(side=tk.LEFT, padx=10)
        return btn

    def atualizar_tela_inicio_turno(self):
        """Consulta a Lista Encadeada e exibe o Placar atualizado."""
        vit_j1, vit_j2 = self.lista.consultar(self.meu_nome, self.nome_adv)
        self.lbl_placar.config(text=f"{self.meu_nome}  {vit_j1}  x  {vit_j2}  {self.nome_adv}")
        self.lbl_status.config(text="Sua vez! Faça sua escolha.")
        
        # Reativa os botões para você poder jogar
        for btn in [self.btn_pedra, self.btn_papel, self.btn_tesoura]:
            btn.config(state=tk.NORMAL, bg="#313244")

    # ----------------------------------------------------------------
    # LÓGICA DO JOGO E INTELIGÊNCIA ARTIFICIAL (IA)
    # ----------------------------------------------------------------
    def computar_minha_jogada(self, escolha):
        """Acionado quando você clica em Pedra, Papel ou Tesoura."""
        self.minha_jogada = escolha
        
        # Desativa seus botões para você não jogar duas vezes
        for btn in [self.btn_pedra, self.btn_papel, self.btn_tesoura]:
            btn.config(state=tk.DISABLED, bg="#181825")
            
        if self.modo_jogo == "multi":
            try:
                self.conn.send(escolha.encode('utf-8')) # Manda a jogada pela rede
                self.lbl_status.config(text=f"Aguardando a jogada de {self.nome_adv}...")
                self.verificar_resolucao()
            except:
                self.gerenciar_queda_conexao()
                
        elif self.modo_jogo == "robo":
            self.lbl_status.config(text="A I.A. está analisando seus padrões...")
            # Um pequeno delay para fingir que a IA está "pensando"
            self.root.after(600, self.jogada_do_robo_inteligente)

    def jogada_do_robo_inteligente(self):
        """
        O Algoritmo de Aprendizado de Máquina (Reinforcement Learning Simplificado).
        Ele checa o que você jogou agora e busca na memória a melhor resposta baseada no passado.
        """
        memoria_dessa_jogada = self.memoria_robo[self.minha_jogada]
        maior_pontuacao = max(memoria_dessa_jogada.values()) # Pega a nota mais alta
        
        # Lista as jogadas que têm essa nota máxima (se for empate, ele pega todas)
        melhores_opcoes = [jogada for jogada, pontos in memoria_dessa_jogada.items() if pontos == maior_pontuacao]
        
        # O robô chuta aleatoriamente entre as melhores opções (se for a 1ª rodada, ele chuta entre as 3)
        self.jogada_adv = random.choice(melhores_opcoes)
        self.verificar_resolucao()

    def verificar_resolucao(self):
        """Checa se ambos já jogaram. Se sim, processa quem ganhou."""
        if self.minha_jogada is not None and self.jogada_adv is not None:
            self.resolver_turno(self.minha_jogada, self.jogada_adv)
            
            # Limpa as variáveis para a próxima rodada
            self.minha_jogada = None
            self.jogada_adv = None

    def resolver_turno(self, minha, adv):
        """Calcula o vencedor, atualiza a Lista Encadeada e pune/recompensa a IA."""
        if minha == adv: resultado = 'Empate'
        else:
            regras = {'pedra': 'tesoura', 'papel': 'pedra', 'tesoura': 'papel'}
            if regras[minha] == adv: resultado = self.meu_nome
            else: resultado = self.nome_adv

        # APRENDIZADO DA I.A.: Recompensa (+1) ou Punição (-1)
        if self.modo_jogo == "robo":
            if resultado == self.nome_adv:
                self.memoria_robo[minha][adv] += 1 # Robô acertou e ganhou de você!
            elif resultado == self.meu_nome:
                self.memoria_robo[minha][adv] -= 1 # Robô perdeu, não vai mais tentar isso.

        # Instancia a Rodada (o Dado)
        rodada_atual = Rodada(self.id_geral_rodadas, self.meu_nome, minha, self.nome_adv, adv, resultado)
        self.lista.adicionar(rodada_atual) # INCLUSÃO na Lista Encadeada

        if resultado == 'Empate':
            self.lista.remover(self.id_geral_rodadas) # EXCLUSÃO na Lista Encadeada
            ModalAviso(self.root, "Empate!", f"Ambos jogaram {minha.capitalize()}.", "#F38BA8")
        else:
            txt = "Você ganhou a rodada!" if resultado == self.meu_nome else f"{self.nome_adv} ganhou!"
            ModalAviso(self.root, "Resultado", f"Você: {minha.capitalize()}\n{self.nome_adv}: {adv.capitalize()}\n\n🏆 {txt}", "#A6E3A1")

        self.id_geral_rodadas += 1

        # Checa se alguém já chegou em 3 vitórias (Melhor de 5)
        vit_j1, vit_j2 = self.lista.consultar(self.meu_nome, self.nome_adv)
        if vit_j1 == 3: self.encerrar_jogo(self.meu_nome)
        elif vit_j2 == 3: self.encerrar_jogo(self.nome_adv)
        else: self.atualizar_tela_inicio_turno()

    # ----------------------------------------------------------------
    # TELA DE FIM DE JOGO E HISTÓRICO GERAL
    # ----------------------------------------------------------------
    def encerrar_jogo(self, vencedor):
        """Puxa o relatório, salva no histórico global e oferece Jogar Novamente."""
        texto_final = self.lista.relatorio(vencedor) # RELATÓRIO da Lista Encadeada
        resumo_partida = f"Partida: {self.meu_nome} vs {self.nome_adv} | Vencedor: {vencedor}"
        self.historico_geral_partidas.append(resumo_partida)
        
        self.limpar_tela()
        tk.Label(self.root, text="FIM DA PARTIDA", font=("Segoe UI", 18, "bold"), bg="#1E1E2E", fg="#F9E2AF").pack(pady=20)
        caixa_texto = tk.Text(self.root, font=("Consolas", 10), bg="#181825", fg="#CDD6F4", relief=tk.FLAT, padx=15, pady=15, height=10)
        caixa_texto.pack(padx=30, fill=tk.BOTH, expand=True)
        caixa_texto.insert(tk.END, texto_final)
        caixa_texto.config(state=tk.DISABLED) 
        
        frame_fim = tk.Frame(self.root, bg="#1E1E2E")
        frame_fim.pack(pady=20)
        
        # AGORA O BOTÃO JOGAR NOVAMENTE ESTÁ DISPONÍVEL PARA MULTIPLAYER TAMBÉM!
        # Ele chama o iniciar_nova_partida() que limpa a lista encadeada sem derrubar a rede.
        tk.Button(frame_fim, text="Jogar Novamente", font=("Segoe UI", 12, "bold"), bg="#A6E3A1", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", command=self.iniciar_nova_partida).pack(side=tk.LEFT, padx=10)
        tk.Button(frame_fim, text="Voltar ao Menu", font=("Segoe UI", 12, "bold"), bg="#F38BA8", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", command=self.voltar_ao_menu).pack(side=tk.LEFT, padx=10)

    def voltar_ao_menu(self):
        """Encerra as redes (se houver) e volta pro menu inicial."""
        if self.conn:
            self.conn.close() # Desconecta
            self.conn = None
        self.construir_tela_menu()

    def ver_historico(self):
        """Tela que lista todas as partidas jogadas desde que o jogo foi aberto."""
        self.limpar_tela()
        tk.Label(self.root, text="HISTÓRICO DE PARTIDAS GERAIS", font=("Segoe UI", 16, "bold"), bg="#1E1E2E", fg="#89B4FA").pack(pady=20)
        caixa_texto = tk.Text(self.root, font=("Segoe UI", 12), bg="#181825", fg="#CDD6F4", relief=tk.FLAT, padx=15, pady=15, height=12)
        caixa_texto.pack(padx=30, fill=tk.BOTH, expand=True)
        
        if len(self.historico_geral_partidas) == 0:
            caixa_texto.insert(tk.END, "Nenhuma partida jogada nesta sessão ainda.")
        else:
            for i, partida in enumerate(self.historico_geral_partidas):
                caixa_texto.insert(tk.END, f"{i+1}. {partida}\n")
                
        caixa_texto.config(state=tk.DISABLED) 
        tk.Button(self.root, text="Voltar ao Menu", font=("Segoe UI", 12, "bold"), bg="#F38BA8", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", command=self.construir_tela_menu).pack(pady=20)

