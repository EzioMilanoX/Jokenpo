import tkinter as tk
import socket

def pegar_ip_local():
    """Tenta descobrir o IP do computador na rede local (Wi-Fi/Cabo)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80)) # Tenta "pingar" o Google
        ip = s.getsockname()[0]    # Pega o IP que foi usado para isso
    except:
        ip = '127.0.0.1'           # Se estiver sem internet, usa localhost
    finally:
        s.close()
    return ip

class ModalEntrada(tk.Toplevel):
    """Caixa de diálogo personalizada para perguntar Nomes e Códigos."""
    def __init__(self, parent, titulo, mensagem):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("350x200")
        self.configure(bg="#1E1E2E")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set() # Trava a janela de trás enquanto essa estiver aberta
        
        self.resultado = None # Variável que vai guardar o que o usuário digitou
        
        tk.Label(self, text=mensagem, font=("Segoe UI", 12), bg="#1E1E2E", fg="#CDD6F4").pack(pady=(25, 10))
        self.entrada = tk.Entry(self, font=("Segoe UI", 14), bg="#313244", fg="#A6E3A1", insertbackground="#CDD6F4", relief=tk.FLAT, justify=tk.CENTER)
        self.entrada.pack(pady=10, padx=30, fill=tk.X)
        self.entrada.focus_set() # Já deixa o cursor piscando na caixa de texto
        
        tk.Button(self, text="Confirmar", font=("Segoe UI", 10, "bold"), bg="#89B4FA", fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", command=self.confirmar).pack(pady=10)
        self.bind("<Return>", lambda e: self.confirmar()) # Permite dar Enter
        self.wait_window(self) 

    def confirmar(self):
        self.resultado = self.entrada.get().strip() # Salva tirando espaços inúteis
        self.destroy() # Fecha a caixinha

class ModalAviso(tk.Toplevel):
    """Caixa de diálogo para avisar quem ganhou a rodada ou se empatou."""
    def __init__(self, parent, titulo, mensagem, cor_destaque="#89B4FA"):
        super().__init__(parent)
        self.title(titulo)
        self.geometry("400x220")
        self.configure(bg="#1E1E2E")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()
        
        tk.Label(self, text=mensagem, font=("Segoe UI", 12), bg="#1E1E2E", fg="#CDD6F4", justify=tk.CENTER).pack(expand=True, padx=20, pady=20)
        tk.Button(self, text="OK", font=("Segoe UI", 10, "bold"), bg=cor_destaque, fg="#1E1E2E", relief=tk.FLAT, cursor="hand2", width=15, command=self.destroy).pack(pady=(0, 20))
        self.bind("<Return>", lambda e: self.destroy())
        self.wait_window(self)