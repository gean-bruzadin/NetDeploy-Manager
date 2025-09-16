# =========================================
# Script: instalar_programas.ps1
# Função: Instalar múltiplos programas em modo silencioso (direto da rede)
# =========================================

# Caminho da pasta compartilhada na rede
$CaminhoRede = "Z:\"

# Desbloqueia todos os arquivos da pasta (remove flag de segurança)
Write-Host "Removendo bloqueio de segurança dos arquivos em $CaminhoRede..."
Get-ChildItem -Path $CaminhoRede -Recurse -File | Unblock-File -ErrorAction SilentlyContinue
Write-Host "Arquivos desbloqueados com sucesso!"
Write-Host "-----------------------------------------"

# Lista de programas (Nome, Caminho, Argumentos)
$programas = @(
    @{ Nome = "7-Zip"; Caminho = "Z:\7z.exe"; Args = "/S" },
    @{ Nome = "Notepad++"; Caminho = "Z:\npp.8.8.5.Installer.x64.exe"; Args = "/S" },
    @{ Nome = "VLC"; Caminho = "Z:\vlc-3.0.21-win64.exe"; Args = "/S" },
    @{ Nome = "TeamViewer"; Caminho = "Z:\TeamViewer_Setup_x64.exe"; Args = "/S" }
)

# Loop para instalar
foreach ($prog in $programas) {
    if (Test-Path $prog.Caminho) {
        Write-Host "Iniciando instalação silenciosa de $($prog.Nome)..."

        try {
            # Executa direto da rede em modo silencioso
            Start-Process -FilePath $prog.Caminho -ArgumentList $prog.Args -Wait

            Write-Host "Instalação de $($prog.Nome) concluída!"
        }
        catch {
            Write-Host "Erro ao instalar $($prog.Nome): $_"
        }

        Write-Host "-----------------------------------------"
    } else {
        Write-Host "Arquivo não encontrado: $($prog.Caminho)"
    }
}

Write-Host "Todas as instalações foram concluídas!"