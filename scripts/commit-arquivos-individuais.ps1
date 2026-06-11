<#
Cria um commit separado para cada arquivo alterado ou novo.

Uso:
  powershell -ExecutionPolicy Bypass -File scripts/commit-arquivos-individuais.ps1
  powershell -ExecutionPolicy Bypass -File scripts/commit-arquivos-individuais.ps1 -Tipo feat
  powershell -ExecutionPolicy Bypass -File scripts/commit-arquivos-individuais.ps1 -WhatIf
#>

param(
    [string]$Tipo = "feat",
    [switch]$WhatIf
)

$ErrorActionPreference = "Stop"

function Get-ResumoArquivo {
    param([string]$Arquivo)

    $nome = Split-Path $Arquivo -Leaf

    if ($Arquivo -like "templates/*") {
        return @(
            "Resumo: melhora a apresentacao visual do template $nome",
            "Funcoes: organiza layout, botoes, tabelas e componentes Bootstrap",
            "Impacto: mantem URLs e regras existentes sem alterar backend"
        )
    }

    if ($Arquivo -like "static/css/*") {
        return @(
            "Resumo: centraliza estilos visuais do sistema",
            "Funcoes: define cards, navbar, tabelas, formularios e responsividade",
            "Impacto: melhora consistencia visual sem novas dependencias"
        )
    }

    if ($Arquivo -like "relatorios/*") {
        return @(
            "Resumo: ajusta apoio visual dos relatorios",
            "Funcoes: prepara dados usados pelos cards e telas de fechamento",
            "Impacto: preserva consultas e regras de negocio"
        )
    }

    if ($Arquivo -like "usuarios/management/commands/*") {
        return @(
            "Resumo: adiciona comando de apoio para usuarios de teste",
            "Funcoes: cria ou atualiza contas padrao para apresentacao",
            "Impacto: facilita preparar o ambiente apos clonar o projeto"
        )
    }

    if ($Arquivo -eq ".gitignore") {
        return @(
            "Resumo: atualiza regras de arquivos ignorados",
            "Funcoes: evita versionar ambiente virtual, banco local, caches e logs",
            "Impacto: deixa o repositorio mais limpo para o GitHub"
        )
    }

    if ($Arquivo -like "scripts/*") {
        return @(
            "Resumo: adiciona automacao para commits individuais",
            "Funcoes: cria commits separados por arquivo com mensagens formatadas",
            "Impacto: melhora organizacao do historico no GitHub"
        )
    }

    return @(
        "Resumo: atualiza $nome",
        "Funcoes: mantem o arquivo alinhado com o projeto",
        "Impacto: preserva o funcionamento existente"
    )
}

function Get-TituloCommit {
    param(
        [string]$Tipo,
        [string]$Arquivo
    )

    $nome = Split-Path $Arquivo -Leaf
    $semExtensao = [System.IO.Path]::GetFileNameWithoutExtension($nome)

    if ($Arquivo -eq ".gitignore") {
        return "chore: update gitignore"
    }

    if ($Arquivo -like "scripts/*") {
        return "chore: add individual commit script"
    }

    return "$Tipo`: update $semExtensao"
}

git rev-parse --is-inside-work-tree *> $null

$arquivosAlterados = git diff --name-only --diff-filter=ACMR
$arquivosStaged = git diff --cached --name-only --diff-filter=ACMR
$arquivosNovos = git ls-files --others --exclude-standard

$arquivos = @($arquivosAlterados + $arquivosStaged + $arquivosNovos) |
    Where-Object {
        $_ -and
        $_ -notmatch "^venv/" -and
        $_ -notmatch "^db\.sqlite3$"
    } |
    Sort-Object -Unique

if (-not $arquivos) {
    Write-Host "Nenhum arquivo pendente para commit."
    exit 0
}

foreach ($arquivo in $arquivos) {
    $titulo = Get-TituloCommit -Tipo $Tipo -Arquivo $arquivo
    $detalhes = Get-ResumoArquivo -Arquivo $arquivo

    $mensagem = @(
        $titulo,
        "",
        "- $($detalhes[0])",
        "- $($detalhes[1])",
        "- $($detalhes[2])"
    ) -join [Environment]::NewLine

    if ($WhatIf) {
        Write-Host "DRY RUN: git add -- $arquivo"
        Write-Host "DRY RUN: git commit -m"
        Write-Host $mensagem
        Write-Host ""
        continue
    }

    $arquivoMensagem = New-TemporaryFile
    Set-Content -Path $arquivoMensagem -Value $mensagem -Encoding UTF8

    try {
        git add -- $arquivo
        git commit -F $arquivoMensagem
    }
    finally {
        Remove-Item -LiteralPath $arquivoMensagem -Force -ErrorAction SilentlyContinue
    }
}
