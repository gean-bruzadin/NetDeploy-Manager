import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

class App:
    """
    Classe principal que encapsula toda a lógica e a interface gráfica da aplicação.
    """
    def __init__(self, root):
        self.root = root
        self.root.title("Gerador de Script de Instalação")
        self.root.geometry("750x500")
        self.root.minsize(600, 400) # Define um tamanho mínimo para a janela

        # Lista para armazenar os programas
        self.programas = []

        self.criar_widgets()

    def criar_widgets(self):
        """
        Cria todos os componentes (widgets) da interface gráfica.
        """
        # --- Frame para a unidade de destino ---
        frame_unidade = tk.Frame(self.root, pady=10)
        frame_unidade.pack(fill=tk.X, padx=10)

        tk.Label(frame_unidade, text="Salvar script em:").pack(side=tk.LEFT)
        self.entrada_unidade = tk.Entry(frame_unidade)
        self.entrada_unidade.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5)
        self.entrada_unidade.insert(0, "C:\\Temp")  # Sugestão de valor padrão
        
        btn_procurar_pasta = tk.Button(frame_unidade, text="Procurar...", command=self.procurar_pasta_destino)
        btn_procurar_pasta.pack(side=tk.LEFT)

        # --- Frame para a lista de programas ---
        frame_lista = tk.Frame(self.root, padx=10)
        frame_lista.pack(pady=5, fill=tk.BOTH, expand=True)

        self.lista = tk.Listbox(frame_lista, height=15)
        self.lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scroll = tk.Scrollbar(frame_lista, command=self.lista.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.lista.config(yscrollcommand=scroll.set)

        # --- Frame para os botões ---
        frame_botoes = tk.Frame(self.root, pady=10)
        frame_botoes.pack()

        btn_add = tk.Button(frame_botoes, text="Adicionar Programa", command=self.adicionar_programa, width=25, height=2)
        btn_add.pack(side=tk.LEFT, padx=10)
        
        btn_remover = tk.Button(frame_botoes, text="Remover Selecionado", command=self.remover_programa, width=25, height=2)
        btn_remover.pack(side=tk.LEFT, padx=10)

        btn_gerar = tk.Button(frame_botoes, text="Gerar Script PowerShell", command=self.gerar_script, width=25, height=2, bg="#4CAF50", fg="white")
        btn_gerar.pack(side=tk.LEFT, padx=10)

    def procurar_pasta_destino(self):
        """Abre um diálogo para o usuário selecionar uma pasta."""
        pasta_selecionada = filedialog.askdirectory(title="Selecione a pasta para salvar o script")
        if pasta_selecionada:
            self.entrada_unidade.delete(0, tk.END)
            self.entrada_unidade.insert(0, pasta_selecionada)

    def adicionar_programa(self):
        """
        Abre diálogos para adicionar um novo programa à lista.
        """
        nome = simpledialog.askstring("Nome do Programa", "Digite o nome do programa:")
        if not nome:
            return
        
        caminho = filedialog.askopenfilename(title="Selecione o instalador", filetypes=[("Executáveis", "*.exe;*.msi"), ("Todos os arquivos", "*.*")])
        if not caminho:
            return
        
        args = simpledialog.askstring("Argumentos", "Digite os argumentos de instalação silenciosa (ex: /S, /quiet, /qn):", initialvalue="/S")
        if args is None:  # Usuário clicou em "Cancelar"
            return
        
        self.programas.append({"Nome": nome, "Caminho": caminho, "Args": args})
        self.atualizar_lista()

    def remover_programa(self):
        """Remove o programa selecionado da lista."""
        selecionado = self.lista.curselection()
        if not selecionado:
            messagebox.showwarning("Aviso", "Nenhum programa selecionado para remover.")
            return

        indice = selecionado[0]
        del self.programas[indice]
        self.atualizar_lista()


    def atualizar_lista(self):
        """
        Limpa e atualiza a Listbox com os programas da lista interna.
        """
        self.lista.delete(0, tk.END)
        for i, prog in enumerate(self.programas):
            self.lista.insert(tk.END, f"{i+1}. {prog['Nome']} | Args: {prog['Args']} | Caminho: {prog['Caminho']}")

    def gerar_script(self):
        """
        Gera o script PowerShell final com base nos programas adicionados.
        """
        pasta_destino = self.entrada_unidade.get().strip()
        if not pasta_destino or not os.path.isdir(pasta_destino):
            messagebox.showwarning("Aviso", f"O caminho de destino '{pasta_destino}' não é uma pasta válida!")
            return

        if not self.programas:
            messagebox.showwarning("Aviso", "Nenhum programa foi adicionado à lista!")
            return

        # Define o caminho do script base
        try:
            base_dir = os.path.dirname(__file__)
        except NameError:
            base_dir = os.getcwd()
        caminho_origem = os.path.join(base_dir, "script_base.ps1")

        # Cria o script base se ele não existir
        if not os.path.exists(caminho_origem):
            try:
                with open(caminho_origem, "w", encoding="utf-8-sig") as f:
                    f.write("# Script base gerado automaticamente.\n")
                    f.write("Write-Host 'Iniciando script de configuração...' -ForegroundColor Cyan\n")
            except Exception as e:
                messagebox.showerror("Erro", f"Não foi possível criar 'script_base.ps1': {e}")
                return
        
        caminho_saida = os.path.join(pasta_destino, "instalar_programas.ps1")

        try:
            with open(caminho_origem, "r", encoding="utf-8-sig") as f_origem:
                conteudo = f_origem.read()

            conteudo += "\n\n# --- Bloco de Instalação Gerado Automaticamente ---\n"
            conteudo += "# Lista de programas (Nome, Caminho, Argumentos)\n"
            conteudo += "$programas = @(\n"
            for prog in self.programas:
                # Escapa as aspas simples para o PowerShell
                nome = prog['Nome'].replace("'", "''")
                caminho = prog['Caminho'].replace("'", "''")
                args = prog['Args'].replace("'", "''")
                # Usa objetos personalizados do PowerShell para maior clareza
                conteudo += f"    [PSCustomObject]@{{Nome = '{nome}'; Caminho = '{caminho}'; Args = '{args}'}},\n"
            
            # Remove a última vírgula
            if conteudo.endswith(",\n"):
                conteudo = conteudo[:-2] + "\n"
            conteudo += ")\n"

            # Adiciona o loop de instalação mais robusto
            conteudo += """
# Loop para instalar os programas
Write-Host "Iniciando processo de instalação..." -ForegroundColor Green

foreach ($prog in $programas) {
    if (Test-Path $prog.Caminho) {
        Write-Host "Instalando $($prog.Nome)..." -ForegroundColor Yellow
        try {
            Start-Process -FilePath $prog.Caminho -ArgumentList $prog.Args -Wait -ErrorAction Stop
            Write-Host "$($prog.Nome) instalado com sucesso." -ForegroundColor Green
        } catch {
            Write-Host "ERRO ao instalar $($prog.Nome): $_" -ForegroundColor Red
        }
    } else {
        Write-Host "ARQUIVO NÃO ENCONTRADO para $($prog.Nome) em $($prog.Caminho)" -ForegroundColor Red
    }
}

Write-Host "Processo de instalação concluído." -ForegroundColor Green
"""

            with open(caminho_saida, "w", encoding="utf-8-sig") as f_destino:
                f_destino.write(conteudo)

            messagebox.showinfo("Sucesso", f"Script gerado com sucesso em:\n{caminho_saida}")
        
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao gerar o script: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
