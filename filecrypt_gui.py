import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import tkinter.font as tkFont
import filecrypt_core as fc
from PIL import Image, ImageTk, ImageSequence
import os
import sys

# ---------- Função para localizar recursos (GIF) mesmo dentro do exe ----------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # PyInstaller cria pasta temporária
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- Funções de criptografia ----------
def choose_key():
    path = filedialog.askopenfilename(title="Selecione o arquivo de chave (key.bin)")
    if path:
        entry_key.delete(0, tk.END)
        entry_key.insert(0, path)

def choose_input():
    path = filedialog.askopenfilename(title="Selecione o arquivo para criptografar/descriptografar")
    if path:
        entry_input.delete(0, tk.END)
        entry_input.insert(0, path)

def choose_output_dir():
    path = filedialog.askdirectory(title="Escolha o diretório de saída")
    if path:
        entry_output.delete(0, tk.END)
        entry_output.insert(0, path)

def generate_key():
    out_path = filedialog.asksaveasfilename(defaultextension=".bin", title="Salvar chave como")
    if out_path:
        fc.gen_key(Path(out_path))
        messagebox.showinfo("Sucesso", f"Chave criada: {out_path}")

def encrypt_action():
    try:
        key = fc.load_key(Path(entry_key.get()))
        infile = Path(entry_input.get())
        outdir = Path(entry_output.get())
        outfile = outdir / (infile.name + ".enc")
        fc.encrypt_file(key, infile, outfile)
        messagebox.showinfo("Sucesso", f"Arquivo criptografado: {outfile}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

def decrypt_action():
    try:
        key = fc.load_key(Path(entry_key.get()))
        infile = Path(entry_input.get())
        outdir = Path(entry_output.get())
        outfile = fc.decrypt_file(key, infile, outdir)
        messagebox.showinfo("Sucesso", f"Arquivo descriptografado: {outfile}")
    except Exception as e:
        messagebox.showerror("Erro", str(e))

# ---------- Inicialização da GUI ----------
root = tk.Tk()
root.title("Criptografia de Arquivos")
root.geometry("700x600")
root.resizable(False, False)
root.configure(bg="#070e25")  # fundo total da janela

# ---------- Fontes e configurações ----------
font_label = tkFont.Font(family="Helvetica", size=14)
font_entry = tkFont.Font(family="Helvetica", size=14)
font_button = tkFont.Font(family="Helvetica", size=13, weight="bold")
entry_width = 44
pad_x = 8
pad_y = 6

# ---------- Frame central ----------
main_frame = tk.Frame(root, bg="#070e25")
main_frame.place(relx=0.5, rely=0.0, anchor="n")

# ---------- Campos ----------
tk.Label(main_frame, text="Chave (key.bin):", font=font_label, bg="#070e25", fg="white")\
    .grid(row=0, column=0, columnspan=2, sticky="w", pady=(20,10))
entry_key = tk.Entry(main_frame, width=entry_width, font=font_entry, bg="#1a1f38", fg="white", insertbackground="white")
entry_key.grid(row=1, column=0, padx=(0,10), pady=(0,15), sticky="w")
tk.Button(main_frame, text="Procurar", command=choose_key, font=font_button, width=10, bg="#1e234a", fg="white")\
    .grid(row=1, column=1, sticky="w", ipady=6)

tk.Label(main_frame, text="Arquivo de entrada:", font=font_label, bg="#070e25", fg="white")\
    .grid(row=2, column=0, columnspan=2, sticky="w", pady=(10,10))
entry_input = tk.Entry(main_frame, width=entry_width, font=font_entry, bg="#1a1f38", fg="white", insertbackground="white")
entry_input.grid(row=3, column=0, padx=(0,10), pady=(0,15), sticky="w")
tk.Button(main_frame, text="Procurar", command=choose_input, font=font_button, width=10, bg="#1e234a", fg="white")\
    .grid(row=3, column=1, sticky="w", ipady=6)

tk.Label(main_frame, text="Diretório de saída:", font=font_label, bg="#070e25", fg="white")\
    .grid(row=4, column=0, columnspan=2, sticky="w", pady=(10,10))
entry_output = tk.Entry(main_frame, width=entry_width, font=font_entry, bg="#1a1f38", fg="white", insertbackground="white")
entry_output.grid(row=5, column=0, padx=(0,10), pady=(0,15), sticky="w")
tk.Button(main_frame, text="Escolher", command=choose_output_dir, font=font_button, width=10, bg="#1e234a", fg="white")\
    .grid(row=5, column=1, sticky="w", ipady=6)

# ---------- Botões ----------
btn_frame = tk.Frame(main_frame, bg="#070e25")
btn_frame.grid(row=6, column=0, columnspan=2, pady=(30,0))

tk.Button(btn_frame, text="Gerar Nova Chave", command=generate_key, bg="#1e234a", fg="white", font=font_button, width=18)\
    .pack(side='left', padx=6, pady=0, ipadx=4, ipady=8)
tk.Button(btn_frame, text="Criptografar", command=encrypt_action, bg="#2d6e41", fg="white", font=font_button, width=18)\
    .pack(side='left', padx=6, pady=0, ipadx=4, ipady=8)
tk.Button(btn_frame, text="Descriptografar", command=decrypt_action, bg="#345280", fg="white", font=font_button, width=18)\
    .pack(side='left', padx=6, pady=0, ipadx=4, ipady=8)

# ---------- GIF ----------
gif_file = resource_path("imgs/gifcadeado.gif")
gif = Image.open(gif_file)
frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA")) for frame in ImageSequence.Iterator(gif)]
gif_label = tk.Label(root, bg="#070e25")
gif_label.place(relx=0.5, rely=0.95, anchor='s')

def animate(counter=0):
    gif_label.config(image=frames[counter])
    root.after(100, animate, (counter+1) % len(frames))

animate(0)

# ---------- Ajuste de colunas ----------
main_frame.grid_columnconfigure(0, weight=0)
main_frame.grid_columnconfigure(1, weight=0)

root.mainloop()
