# 📚 Sebo nas canelas 🏃‍♀️💨

**Sebo nas canelas** é um sistema desktop simples para gerenciar um sebo: cadastro de livros, controle de estoque e registro de vendas.  
Feito em Python usando **CustomTkinter** para a interface e **sqlite3** como banco de dados embarcado. Projetado para uso acadêmico ou para pequenas lojas que precisam de um gerenciador leve e portátil.

---

## Sobre o projeto

### Visão geral
O aplicativo permite:
- Cadastrar livros (título, autor, preço, quantidade, condição).
- Buscar por título / autor / condição.
- Editar e remover livros.
- Registrar vendas (que atualizam o estoque automaticamente).
- Ver histórico de vendas, editar e remover vendas (com recomposição de estoque quando apropriado).

---

## ⚙️ Como rodar o projeto

### Pré-requisitos
- Python **3.10** ou superior instalado no sistema.
- CustomTkinter
  
### Passo a passo
 1.  **Instalar o Python**

     - Acesse o site oficial: [https://www.python.org/downloads](https://www.python.org/downloads)  
     - Baixe a versão mais recente do **Python 3.x** (recomendado 3.10 ou superior).  
     - Após instalar, abra o **Prompt de Comando** e digite:
        ```bash
        python --version
        ```

3. **Salvar o código**
   - Salve o seu código em um arquivo, por exemplo `sebo.py`, na pasta onde quer rodar o app.

4. **Instalar dependência**
   - Abra o terminal / Prompt de Comando e rode:
     ```bash
     pip install customtkinter
     ```

5. **Executar o programa**
   - No terminal, dentro da pasta onde está `sebo.py`, rode:
     ```bash
     python sebo.py
     ```
     (ou `python3 sebo.py` dependendo do seu sistema)

6. **Primeiro uso**
   - Ao abrir, o app criará automaticamente `sebo_livros.db` na mesma pasta.  
   - Teste cadastrando um livro e registrando uma venda para verificar se o fluxo de estoque/histórico está funcionando.
