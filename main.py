import tkinter as tk
from jogo_gui import JogoGUI

# =================================================================
# INICIALIZAÇÃO DO PROGRAMA
# =================================================================
if __name__ == "__main__":
    janela = tk.Tk()
    janela.resizable(False, False) # Trava o tamanho da janela para não quebrar o visual
    app = JogoGUI(janela)
    janela.mainloop() # Mantém o jogo rodando