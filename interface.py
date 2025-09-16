import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import os

# Lista para armazenar os programas
programas = []

# Função para buscar caminho de arquivo
def buscar_programa():
    caminho = filedialog.askopenfilename(title="Selecione o instalador")
    return caminho

# Função para adicionar programa
def adicionar_programa():
    nome = simpledialog.askstring("Nome do Programa", "Digite o nome do programa:")
    if not nome:
        return
    
    caminho = buscar_programa()
    if not caminho:
        return
    
    args = simpledialog.askstring("Argumentos", "Digite os argumentos (ex: /S):", initialvalue="/S")
    if not args:
        args = ""
    
    programas.append({"Nome": nome, "Caminho": caminho, "Args": args})
    atualizar_lista()

# Atualizar a lista na interface
def atualizar_lista():
    lista.delete(0, tk.END)
    for prog in programas:
        lista.insert(tk.END, f"{prog['Nome']} | {prog['Caminho']} | {prog['Args']}")

# Gerar script PowerShell
def gerar_script():
    unidade = entrada_unidade.get().strip()
    if not unidade:
        messagebox.showwarning("Aviso", "Informe a unidade onde o script será salvo!")
        return

    if not programas:
        messagebox.showwarning("Aviso", "Nenhum programa adicionado!")
        return

    script = [
        "# =========================================",
        "# Script: instalar_programas.ps1",
        "# Função: Instalar múltiplos programas em modo silencioso (copiando p/ TEMP)",
        "# =========================================",
        "",
        "# Lista de programas (Nome, Caminho, Argumentos)",
        "$programas = @("
    ]

    for prog in programas:
        script.append(
            f'    @{{ Nome = "{prog["Nome"]}"; Caminho = "{prog["Caminho"]}"; Args = "{prog["Args"]}" }},'
        )

    # Remove a vírgula do último item
    if script[-1].endswith(","):
        script[-1] = script[-1][:-1]

    script.append(")")
    script.append("")
    script.append("# Loop para instalar")
    script.append("foreach ($prog in $programas) {")
    script.append("    if (Test-Path $prog.Caminho) {")
    script.append("        Write-Host \"Preparando instalação de $($prog.Nome)...\"")
    script.append("")
    script.append("        try {")
    script.append("            $Destino = Join-Path $env:TEMP (Split-Path $prog.Caminho -Leaf)")
    script.append("            Copy-Item $prog.Caminho $Destino -Force")
    script.append("            Unblock-File -Path $Destino -ErrorAction SilentlyContinue")
    script.append("            Write-Host \"Iniciando instalação silenciosa de $($prog.Nome)...\"")
    script.append("            Start-Process -FilePath $Destino -ArgumentList $prog.Args -Wait")
    script.append("            Remove-Item $Destino -Force")
    script.append("            Write-Host \"Instalação de $($prog.Nome) concluída!\"")
    script.append("        }")
    script.append("        catch {")
    script.append("            Write-Host \"Erro ao instalar $($prog.Nome): $_\"")
    script.append("        }")
    script.append("        Write-Host \"-----------------------------------------\"")
    script.append("    } else {")
    script.append("        Write-Host \"Arquivo não encontrado: $($prog.Caminho)\"")
    script.append("    }")
    script.append("}")
    script.append("")
    script.append("Write-Host \"Todas as instalações foram concluídas!\"")

    # Salvar script na unidade escolhida
    caminho_saida = os.path.join(unidade, "instalar_programas.ps1")
    try:
        with open(caminho_saida, "w", encoding="utf-8") as f:
            f.write("\n".join(script))
        messagebox.showinfo("Sucesso", f"Script gerado em:\n{caminho_saida}")
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar script: {e}")


# ================== INTERFACE ==================
root = tk.Tk()
root.title("Editor Script - TCC Noite")
root.geometry("700x500")

# Unidade
frame_unidade = tk.Frame(root)
frame_unidade.pack(pady=10)
tk.Label(frame_unidade, text="Unidade de destino do script:").pack(side=tk.LEFT)
entrada_unidade = tk.Entry(frame_unidade, width=20)
entrada_unidade.pack(side=tk.LEFT, padx=5)
entrada_unidade.insert(0, "C:\\")  # valor padrão

# Lista de programas
frame_lista = tk.Frame(root)
frame_lista.pack(pady=10, fill=tk.BOTH, expand=True)
lista = tk.Listbox(frame_lista, width=90, height=15)
lista.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scroll = tk.Scrollbar(frame_lista, command=lista.yview)
scroll.pack(side=tk.RIGHT, fill=tk.Y)
lista.config(yscrollcommand=scroll.set)

# Botões
frame_botoes = tk.Frame(root)
frame_botoes.pack(pady=10)
btn_add = tk.Button(frame_botoes, text="Add +", command=adicionar_programa, width=15)
btn_add.pack(side=tk.LEFT, padx=5)
btn_gerar = tk.Button(frame_botoes, text="Atualizar Script", command=gerar_script, width=20)
btn_gerar.pack(side=tk.LEFT, padx=5)

root.mainloop()
