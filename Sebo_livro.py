import sqlite3
from datetime import datetime
import customtkinter as ctk
from tkinter import messagebox, ttk, simpledialog

# --- BANCO DE DADOS ---------------------------------------------------------------------------------------------------------------------------
conn = sqlite3.connect("sebo_livros.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS livros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    autor TEXT NOT NULL,
    preco REAL NOT NULL,
    quantidade_estoque INTEGER NOT NULL,
    condicao TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS vendas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    quantidade INTEGER NOT NULL,
    data_venda TEXT NOT NULL,
    valor_total REAL NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livros(id)
)
""")
conn.commit()

# --- FUNÇÕES ---------------------------------------------------------------------------------------------------------------------------
def cadastrar_livro():
    titulo = campo_titulo.get().strip()
    autor = campo_autor.get().strip()
    preco = campo_preco.get().strip()
    quantidade = campo_quantidade.get().strip()
    condicao = combobox_condicao.get().strip()

    if not (titulo and autor and preco and quantidade and condicao):
        messagebox.showwarning("Erro", "Preencha todos os campos!")
        return

    try:
        preco_float = float(preco)
        quantidade_int = int(quantidade)
    except ValueError:
        messagebox.showwarning("Erro", "Preço ou quantidade inválidos.")
        return

    cursor.execute(
        "INSERT INTO livros (titulo, autor, preco, quantidade_estoque, condicao) VALUES (?, ?, ?, ?, ?)",
        (titulo, autor, preco_float, quantidade_int, condicao)
    )
    conn.commit()
    messagebox.showinfo("Sucesso", f"Livro '{titulo}' ({condicao}) cadastrado no sebo!")
    limpar_campos()
    mostrar_livros()


def mostrar_livros(texto_busca=None):
    for linha in tabela_livros.get_children():
        tabela_livros.delete(linha)

    if texto_busca:
        busca = f"%{texto_busca}%"
        cursor.execute("SELECT * FROM livros WHERE titulo LIKE ? OR autor LIKE ? OR condicao LIKE ?", (busca, busca, busca))
    else:
        cursor.execute("SELECT * FROM livros")

    livros = cursor.fetchall()
    for livro in livros:
        tabela_livros.insert("", ctk.END, values=livro)


def buscar_livros():
    texto = campo_busca.get().strip()
    mostrar_livros(texto if texto else None)


def limpar_busca():
    campo_busca.delete(0, ctk.END)
    mostrar_livros()


def selecionar_livro(event=None):
    selecionados = tabela_livros.selection()
    if not selecionados:
        return

    livro = tabela_livros.item(selecionados[0])['values']

    campo_titulo.delete(0, "end")
    campo_titulo.insert(0, livro[1])

    campo_autor.delete(0, "end")
    campo_autor.insert(0, livro[2])

    campo_preco.delete(0, "end")
    campo_preco.insert(0, f"{float(livro[3]):.2f}")

    campo_quantidade.delete(0, "end")
    campo_quantidade.insert(0, str(livro[4]))

    combobox_condicao.set(livro[5])


def editar_livro():
    item_selecionado = tabela_livros.selection()
    if not item_selecionado:
        messagebox.showwarning("Erro", "Selecione um livro para editar.")
        return
    livro = tabela_livros.item(item_selecionado)['values']
    id_livro = livro[0]

    titulo = campo_titulo.get().strip()
    autor = campo_autor.get().strip()
    preco = campo_preco.get().strip()
    quantidade = campo_quantidade.get().strip()
    condicao = combobox_condicao.get().strip()

    if not (titulo and autor and preco and quantidade and condicao):
        messagebox.showwarning("Erro", "Preencha todos os campos antes de salvar.")
        return

    try:
        preco_float = float(preco)
        quantidade_int = int(quantidade)
    except ValueError:
        messagebox.showwarning("Erro", "Preço ou quantidade inválidos.")
        return

    cursor.execute(
        "UPDATE livros SET titulo=?, autor=?, preco=?, quantidade_estoque=?, condicao=? WHERE id=?",
        (titulo, autor, preco_float, quantidade_int, condicao, id_livro)
    )
    conn.commit()
    messagebox.showinfo("Atualizado", f"Livro '{titulo}' atualizado com sucesso!")
    mostrar_livros()


def remover_livro():
    item_selecionado = tabela_livros.selection()
    if not item_selecionado:
        messagebox.showwarning("Erro", "Selecione um livro para remover.")
        return

    livro = tabela_livros.item(item_selecionado)["values"]
    id_livro = livro[0]

    confirmar = messagebox.askyesno("Remover", f"Tem certeza que deseja excluir o livro '{livro[1]}' ({livro[5]})?")
    if confirmar:
        cursor.execute("DELETE FROM vendas WHERE id_livro=?", (id_livro,))
        cursor.execute("DELETE FROM livros WHERE id=?", (id_livro,))
        conn.commit()
        mostrar_livros()
        mostrar_vendas()
        messagebox.showinfo("Removido", f"Livro '{livro[1]}' removido com sucesso!")


def registrar_venda():
    try:
        id_livro = int(campo_id_venda.get())
        quantidade = int(campo_quantidade_venda.get())
    except ValueError:
        messagebox.showwarning("Erro", "Digite valores válidos para ID e quantidade.")
        return

    cursor.execute("SELECT quantidade_estoque, preco, titulo, condicao FROM livros WHERE id=?", (id_livro,))
    livro = cursor.fetchone()

    if not livro:
        messagebox.showerror("Erro", "Livro não encontrado.")
        return

    if livro[0] >= quantidade and quantidade > 0:
        novo_estoque = livro[0] - quantidade
        total_venda = quantidade * livro[1]
        cursor.execute("UPDATE livros SET quantidade_estoque=? WHERE id=?", (novo_estoque, id_livro))

        data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO vendas (id_livro, quantidade, data_venda, valor_total) VALUES (?, ?, ?, ?)",
                       (id_livro, quantidade, data_atual, total_venda))
        conn.commit()

        messagebox.showinfo("Venda registrada",
                            f"{quantidade}x '{livro[2]}' ({livro[3]}) | Total: R$ {total_venda:.2f}")
        campo_id_venda.delete(0, ctk.END)
        campo_quantidade_venda.delete(0, ctk.END)
        mostrar_livros()
        mostrar_vendas()
    else:
        messagebox.showerror("Erro", "Estoque insuficiente ou quantidade inválida.")


def mostrar_vendas():
    for linha in tabela_vendas.get_children():
        tabela_vendas.delete(linha)

    cursor.execute("""
        SELECT v.id, l.titulo, l.condicao, v.quantidade, v.valor_total, v.data_venda, v.id_livro
        FROM vendas v JOIN livros l ON v.id_livro = l.id
    """)
    vendas = cursor.fetchall()
    for venda in vendas:
        tabela_vendas.insert("", ctk.END, values=venda[:-1] + (venda[-1],))


def remover_venda():
    item_selecionado = tabela_vendas.selection()
    if not item_selecionado:
        messagebox.showwarning("Erro", "Selecione uma venda para remover.")
        return
    venda = tabela_vendas.item(item_selecionado)['values']
    id_venda = venda[0]
    titulo = venda[1]
    quantidade = venda[3]

    confirmar = messagebox.askyesno("Remover Venda", f"Remover a venda #{id_venda} de '{titulo}' (qtd: {quantidade})? Isso irá recompor o estoque.")
    if not confirmar:
        return

    cursor.execute("SELECT id_livro FROM vendas WHERE id=?", (id_venda,))
    resultado = cursor.fetchone()
    if resultado:
        id_livro = resultado[0]
        cursor.execute("UPDATE livros SET quantidade_estoque = quantidade_estoque + (SELECT quantidade FROM vendas WHERE id=?) WHERE id=?", (id_venda, id_livro))

    cursor.execute("DELETE FROM vendas WHERE id=?", (id_venda,))
    conn.commit()
    mostrar_vendas()
    mostrar_livros()
    messagebox.showinfo("Removido", "Venda removida e estoque atualizado.")


def editar_venda():
    item_selecionado = tabela_vendas.selection()
    if not item_selecionado:
        messagebox.showwarning("Erro", "Selecione uma venda para editar.")
        return
    venda = tabela_vendas.item(item_selecionado)['values']
    id_venda = venda[0]

    cursor.execute("SELECT id_livro, quantidade FROM vendas WHERE id=?", (id_venda,))
    resultado = cursor.fetchone()
    if not resultado:
        messagebox.showerror("Erro", "Venda não encontrada no banco.")
        return
    id_livro, quantidade_atual = resultado

    try:
        nova_quantidade = simpledialog.askinteger("Editar Venda", f"Quantidade atual: {quantidade_atual}\nDigite a nova quantidade:", minvalue=1)
    except Exception:
        return
    if nova_quantidade is None:
        return

    if nova_quantidade == quantidade_atual:
        return

    cursor.execute("SELECT quantidade_estoque FROM livros WHERE id=?", (id_livro,))
    estoque = cursor.fetchone()
    if not estoque:
        messagebox.showerror("Erro", "Livro vinculado não encontrado.")
        return
    estoque_atual = estoque[0]

    estoque_disponivel = estoque_atual + quantidade_atual
    if nova_quantidade > estoque_disponivel:
        messagebox.showerror("Erro", "Estoque insuficiente para alterar a venda.")
        return

    novo_estoque = estoque_disponivel - nova_quantidade

    cursor.execute("SELECT preco FROM livros WHERE id=?", (id_livro,))
    preco_livro = cursor.fetchone()
    if not preco_livro:
        messagebox.showerror("Erro", "Preço do livro não encontrado.")
        return
    preco = preco_livro[0]
    novo_total = nova_quantidade * preco

    cursor.execute("UPDATE livros SET quantidade_estoque=? WHERE id=?", (novo_estoque, id_livro))
    cursor.execute("UPDATE vendas SET quantidade=?, valor_total=?, data_venda=? WHERE id=?",
                   (nova_quantidade, novo_total, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_venda))
    conn.commit()
    mostrar_vendas()
    mostrar_livros()
    messagebox.showinfo("Atualizado", "Venda alterada com sucesso.")


def limpar_campos():
    campo_titulo.delete(0, ctk.END)
    campo_autor.delete(0, ctk.END)
    campo_preco.delete(0, ctk.END)
    campo_quantidade.delete(0, ctk.END)
    combobox_condicao.set("")

# --- INTERFACE COM CUSTOMTKINTER ---------------------------------------------------------------------------------------------------------------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

janela = ctk.CTk()
janela.title("📚 Sebo nas canelas")
janela.geometry("1050x780")

# --- CADASTRO E BUSCA -------------------------------------------------------------------------------------------------------------------------------
frame_superior = ctk.CTkFrame(janela)         
frame_superior.pack(fill="x", padx=15, pady=10)

# --- BUSCA -----------------------------------------------------------------------------------------------------------------------------------------------
ctk.CTkLabel(frame_superior, text="Buscar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
campo_busca = ctk.CTkEntry(frame_superior, width=250)
campo_busca.grid(row=0, column=1, padx=5, pady=5)
botao_buscar = ctk.CTkButton(frame_superior, text="Pesquisar 🔍", command=buscar_livros)
botao_buscar.grid(row=0, column=2, padx=5)
botao_limpar_busca = ctk.CTkButton(frame_superior, text="Limpar", command=limpar_busca)
botao_limpar_busca.grid(row=0, column=3, padx=5)

# --- CAMPOS DE CADASTRO E EDICAO ---------------------------------------------------------------------------------------------------------------------------
ctk.CTkLabel(frame_superior, text="Título:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
campo_titulo = ctk.CTkEntry(frame_superior, width=300)
campo_titulo.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

ctk.CTkLabel(frame_superior, text="Autor:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
campo_autor = ctk.CTkEntry(frame_superior, width=200)
campo_autor.grid(row=2, column=1, padx=5, pady=5, sticky="w")

ctk.CTkLabel(frame_superior, text="Preço:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
campo_preco = ctk.CTkEntry(frame_superior, width=100)
campo_preco.grid(row=2, column=3, padx=5, pady=5, sticky="w")

ctk.CTkLabel(frame_superior, text="Quantidade:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
campo_quantidade = ctk.CTkEntry(frame_superior, width=80)
campo_quantidade.grid(row=3, column=1, padx=5, pady=5, sticky="w")

ctk.CTkLabel(frame_superior, text="Condição:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
combobox_condicao = ctk.CTkComboBox(frame_superior, values=["Novo", "Seminovo", "Usado"], width=130, state="readonly")
combobox_condicao.grid(row=3, column=3, padx=5, pady=5, sticky="w")

# --- LALINHAR BOTOES ------------------------------------------------------------------------------------------------------------------------------
btn_frame = ctk.CTkFrame(frame_superior, fg_color="transparent")
btn_frame.grid(row=1, column=4, rowspan=3, padx=8, pady=6, sticky="n")

btn_cadastrar = ctk.CTkButton(btn_frame, text="Cadastrar 📥", width=140, command=cadastrar_livro)
btn_cadastrar.grid(row=0, column=0, padx=6, pady=6)

btn_editar = ctk.CTkButton(btn_frame, text="Editar ✏️", width=140, command=editar_livro)
btn_editar.grid(row=1, column=0, padx=6, pady=6)

btn_limpar = ctk.CTkButton(btn_frame, text="Limpar Campos", width=140, command=limpar_campos)
btn_limpar.grid(row=2, column=0, padx=6, pady=6)

btn_remover = ctk.CTkButton(btn_frame, text="Remover 🗑️", width=140, command=remover_livro)
btn_remover.grid(row=3, column=0, padx=6, pady=6)

# --- LISTA ESTOQUE ------------------------------------------------------------------------------------------------------------------------------
frame_lista = ctk.CTkFrame(janela)
frame_lista.pack(fill="both", expand=True, padx=15, pady=10)

estilo = ttk.Style()
estilo.configure("Treeview", font=("Calibri", 13))
estilo.configure("Treeview.Heading", font=("Calibri", 14, "bold"))

colunas = ("ID", "Título", "Autor", "Preço", "Qtd Estoque", "Condição")
tabela_livros = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)
for coluna in colunas:
    tabela_livros.heading(coluna, text=coluna)
    tabela_livros.column(coluna, anchor="center")

tabela_livros.pack(fill="both", expand=True)

tabela_livros.bind('<Double-1>', selecionar_livro)

# --- REGISTRO VENDA ------------------------------------------------------------------------------------------------------------------------------
frame_venda = ctk.CTkFrame(janela)
frame_venda.pack(fill="x", padx=15, pady=10)

ctk.CTkLabel(frame_venda, text="ID Livro: ").grid(row=0, column=0, padx=5, pady=5)
campo_id_venda = ctk.CTkEntry(frame_venda, width=50)
campo_id_venda.grid(row=0, column=1, padx=5, pady=5)

ctk.CTkLabel(frame_venda, text="Quantidade: ").grid(row=0, column=2, padx=5, pady=5)
campo_quantidade_venda = ctk.CTkEntry(frame_venda, width=50)
campo_quantidade_venda.grid(row=0, column=3, padx=5, pady=5)

botao_venda = ctk.CTkButton(frame_venda, text="Registrar Venda ✅", command=registrar_venda)
botao_venda.grid(row=0, column=4, padx=10, pady=5)

# --- HISTÓRICO DE VENDAS ------------------------------------------------------------------------------------------------------------------------------
frame_historico_vendas = ctk.CTkFrame(janela)
frame_historico_vendas.pack(fill="both", expand=True, padx=15, pady=10)

colunas_vendas = ("ID Venda", "Título Livro", "Condição", "Quantidade", "Valor Total", "Data")
tabela_vendas = ttk.Treeview(frame_historico_vendas, columns=colunas_vendas, show="headings", height=8)
for coluna in colunas_vendas:
    tabela_vendas.heading(coluna, text=coluna)
    tabela_vendas.column(coluna, anchor="center")
tabela_vendas.pack(fill="both", expand=True)

# --- BOTOES PARA EDITAR E REMOVER VENDAS -------------------------------------------------------------------------------------------------------------------
frame_botoes_vendas = ctk.CTkFrame(janela)
frame_botoes_vendas.pack(fill="x", padx=15)

botao_editar_venda = ctk.CTkButton(frame_botoes_vendas, text="Editar Venda ✏️", command=editar_venda)
botao_editar_venda.grid(row=0, column=0, padx=5, pady=8)

botao_remover_venda = ctk.CTkButton(frame_botoes_vendas, text="Remover Venda 🗑️", command=remover_venda)
botao_remover_venda.grid(row=0, column=1, padx=5, pady=8)

# --- INICIALIZAÇÃO ------------------------------------------------------------------------------------------------------------------------------
mostrar_livros()
mostrar_vendas()
janela.mainloop()
