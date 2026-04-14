import json
import os
import hashlib
from datetime import datetime
import tkinter as tk
from tkinter import messagebox

ARQUIVO = "banco_dados.json"

# -------- SEGURANÇA --------
def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

# -------- BANCO DE DADOS --------
def carregar_dados():
    if not os.path.exists(ARQUIVO):
        return {}
    with open(ARQUIVO, "r") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO, "w") as f:
        json.dump(dados, f, indent=4)

dados = carregar_dados()
usuario_logado = None

# -------- ANIMAÇÃO --------
def fade_in(janela, alpha=0):
    if alpha < 1:
        alpha += 0.05
        janela.attributes("-alpha", alpha)
        janela.after(30, lambda: fade_in(janela, alpha))

# -------- BOTÃO MODERNO --------
def botao(frame, texto, comando):
    b = tk.Button(
        frame,
        text=texto,
        bg="#1f1f1f",
        fg="white",
        bd=0,
        width=12,
        height=2,
        command=comando
    )
    b.bind("<Enter>", lambda e: b.config(bg="#333"))
    b.bind("<Leave>", lambda e: b.config(bg="#1f1f1f"))
    return b

# -------- REGISTRO --------
def registrar():
    user = entry_user.get()
    senha = entry_senha.get()

    if not user or not senha:
        messagebox.showerror("Erro", "Preencha tudo!")
        return

    if user in dados:
        messagebox.showerror("Erro", "Usuário já existe!")
        return

    dados[user] = {
        "senha": hash_senha(senha),
        "saldo": 0,
        "historico": []
    }

    salvar_dados(dados)
    messagebox.showinfo("Sucesso", "Conta criada!")

# -------- LOGIN --------
def login():
    global usuario_logado
    user = entry_user.get()
    senha = hash_senha(entry_senha.get())

    if user in dados and dados[user]["senha"] == senha:
        usuario_logado = user
        abrir_menu()
    else:
        messagebox.showerror("Erro", "Login inválido!")

# -------- MENU --------
def abrir_menu():
    janela = tk.Toplevel(root)
    janela.geometry("360x520")
    janela.configure(bg="#0f0f0f")

    # animação
    janela.attributes("-alpha", 0)
    fade_in(janela)

    # saldo
    saldo_label = tk.Label(
        janela,
        text="R$ 0.00",
        fg="#00ff88",
        bg="#0f0f0f",
        font=("Arial", 24, "bold")
    )
    saldo_label.pack(pady=20)

    def atualizar():
        saldo = dados[usuario_logado]["saldo"]
        saldo_label.config(text=f"R$ {saldo:.2f}")

    def registrar_hist(msg):
        agora = datetime.now().strftime("%d/%m %H:%M")
        dados[usuario_logado]["historico"].append(f"[{agora}] {msg}")

    # área dinâmica
    frame = tk.Frame(janela, bg="#0f0f0f")
    frame.pack()

    def limpar():
        for w in frame.winfo_children():
            w.destroy()

    # depositar
    def depositar():
        limpar()

        tk.Label(frame, text="Valor", fg="white", bg="#0f0f0f").pack()
        e = tk.Entry(frame)
        e.pack(pady=5)

        def confirmar():
            try:
                v = float(e.get())
                dados[usuario_logado]["saldo"] += v
                registrar_hist(f"+{v}")
                salvar_dados(dados)
                atualizar()
            except:
                messagebox.showerror("Erro", "Valor inválido")

        botao(frame, "Confirmar", confirmar).pack(pady=5)

    # transferir
    def transferir():
        limpar()

        tk.Label(frame, text="Destino", fg="white", bg="#0f0f0f").pack()
        d = tk.Entry(frame)
        d.pack(pady=5)

        tk.Label(frame, text="Valor", fg="white", bg="#0f0f0f").pack()
        v = tk.Entry(frame)
        v.pack(pady=5)

        def confirmar():
            try:
                valor = float(v.get())
                dest = d.get()

                if dest not in dados:
                    raise Exception("Usuário não existe")

                if valor > dados[usuario_logado]["saldo"]:
                    raise Exception("Saldo insuficiente")

                dados[usuario_logado]["saldo"] -= valor
                dados[dest]["saldo"] += valor

                registrar_hist(f"→ {dest} -{valor}")
                salvar_dados(dados)
                atualizar()

            except Exception as e:
                messagebox.showerror("Erro", str(e))

        botao(frame, "Confirmar", confirmar).pack(pady=5)

    # histórico
    def historico():
        limpar()

        texto = "\n".join(dados[usuario_logado]["historico"])
        tk.Label(
            frame,
            text=texto or "Sem histórico",
            fg="white",
            bg="#0f0f0f",
            justify="left"
        ).pack()

    # botões
    frame_btn = tk.Frame(janela, bg="#0f0f0f")
    frame_btn.pack(pady=20)

    botao(frame_btn, "Depositar", depositar).grid(row=0, column=0, padx=5)
    botao(frame_btn, "Transferir", transferir).grid(row=0, column=1, padx=5)
    botao(frame_btn, "Histórico", historico).grid(row=0, column=2, padx=5)

    atualizar()

# -------- LOGIN UI --------
root = tk.Tk()
root.title("Banco Python")
root.geometry("260x220")
root.configure(bg="#0f0f0f")

tk.Label(root, text="Usuário", fg="white", bg="#0f0f0f").pack()
entry_user = tk.Entry(root)
entry_user.pack()

tk.Label(root, text="Senha", fg="white", bg="#0f0f0f").pack()
entry_senha = tk.Entry(root, show="*")
entry_senha.pack()

tk.Button(root, text="Login", command=login).pack(pady=5)
tk.Button(root, text="Registrar", command=registrar).pack(pady=5)

root.mainloop()
