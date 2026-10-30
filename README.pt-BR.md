# Arc Posture Review

[![Release](https://img.shields.io/github/v/release/fabiotreze/arc-posture-review)](https://github.com/fabiotreze/arc-posture-review/releases)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-EF9421.svg)](LICENSE-DOCS)

[English](README.md) · **Português**

Avaliação somente leitura da postura de segurança de **servidores habilitados pelo Azure Arc** e do **SQL Server habilitado pelo Azure Arc**. Um coletor PowerShell somente leitura gera um pacote de evidências; o motor v4 transforma esse pacote em uma avaliação determinística e em um relatório HTML bilíngue (PT-BR/EN-US) com plano de ação priorizado.

> Projeto pessoal e independente. Não é uma ferramenta oficial da Microsoft. Valide as recomendações na documentação oficial da Microsoft; o uso é de responsabilidade de quem executa. Veja [DISCLAIMER.md](DISCLAIMER.md).

![Relatório v4](docs/images/v4-report.pt-BR.png)

## Início rápido (Azure Cloud Shell · PowerShell)

```powershell
Invoke-WebRequest https://github.com/fabiotreze/arc-posture-review/releases/latest/download/Invoke-ArcPostureReview.ps1 -OutFile Invoke-ArcPostureReview.ps1
./Invoke-ArcPostureReview.ps1
```

| Saída | Conteúdo |
|---|---|
| `arc-posture-review/arc-posture-review-<data>.zip` | Pacote de evidências (resultados, achados, SHA-256 do manifest). O script imprime o SHA-256 do pacote. |
| `arc-posture-review/arc-posture-review-<data>-v4/` | `arc-posture-review.v4.pt-BR.html`, `arc-posture-review.v4.en-US.html`, `assessment.v4.json`, `resource-index.v4.json` |
| `arc-posture-review/arc-posture-review-<data>-v4.zip` | A pasta do relatório v4 compactada (+ `.sha256`): **baixe só este arquivo** do Cloud Shell. |

Escopo: `-Subscriptions <id1>,<id2>` ou `-ManagementGroup <nome>` (padrão: subscription atual). O relatório v4 é gerado por padrão (para pular, use `-NoV4Report`) e precisa de git e Python 3.10+; o Cloud Shell já tem os dois. Se faltarem, a coleta termina normalmente e os comandos manuais são exibidos.

## O que o relatório mostra

- **64 controles** (45 automáticos, 19 documentais) e **11 cenários de segurança**, cada um rastreado Evidência → Observação → Afirmação → Controle → Cenário.
- **Execução primeiro:** indicadores de status, aviso de lacunas de dados, narrativa executiva e plano de ação AGORA na ordem canônica de prioridade, com rastro de evidência recolhível para cada verificação com falha ou em risco.
- **Navegação:** menu fixo com imprimir/expandir/recolher; cada `CHK-xx` leva à linha correspondente em *Checks*; visão Zero Trust × Tier com barras de resultado.
- **Links para o portal Azure** por linha de achado (índice de recursos vinculado ao `runId` e ao SHA-256 do pacote).
- **Antes/depois** somente quando um pacote de baseline é informado (`--baseline`).
- Evidência ausente nunca vira aprovação; caminhos de ataque nunca são afirmados como confirmados.

## Comandos v4

<details>
<summary><b>Gerar o relatório a partir de um pacote existente</b></summary>

```powershell
python assurance/v4/checkpoint5/cli/arc_posture.py evaluate --evidence arc-posture-review-<data>.zip --output assessment.v4.json
python tools/New-ResourceIndex.py --evidence arc-posture-review-<data>.zip --assessment assessment.v4.json --output resource-index.v4.json
python assurance/v4/checkpoint6/report/render_v4.py --input assessment.v4.json --resources resource-index.v4.json --locale pt-BR --output arc-posture-review.v4.pt-BR.html
python assurance/v4/checkpoint6/report/render_v4.py --input assessment.v4.json --resources resource-index.v4.json --locale en-US --output arc-posture-review.v4.en-US.html
```

Execute a partir de um clone deste repositório. No Windows, `py -3` funciona no lugar de `python`.
</details>

<details>
<summary><b>Antes/depois contra um pacote anterior</b></summary>

```powershell
python assurance/v4/checkpoint5/cli/arc_posture.py evaluate --evidence <depois>.zip --baseline <antes>.zip --output assessment.v4.json
```

Depois gere o HTML como acima. As duas entradas precisam ser pacotes do coletor (`.zip`), não relatórios já gerados. Sem `--baseline`, o relatório informa que não houve baseline e não mostra tendência.
</details>

<details>
<summary><b>Executar o coletor localmente (Windows / PowerShell 7)</b></summary>

```powershell
az login
./scripts/Invoke-ArcPostureReview.ps1
```

Revise o script antes de executar. O acesso ao Azure é somente leitura (Azure Resource Graph e comandos de leitura do Azure CLI).
</details>

<details>
<summary><b>Permissões e privacidade (LGPD)</b></summary>

- **Permissões:** Reader nas subscriptions ou no management group. O script verifica as permissões efetivas antes e marca como parciais as verificações afetadas quando falta algo.
- **Dados pessoais:** o pacote e os relatórios contêm dados do ambiente (conta de coleta, `caller` do Activity Log, IDs de principal, nomes de máquinas). Guarde em local com controle de acesso, compartilhe só com pessoas autorizadas e apague ao fim do trabalho. Nunca anexe em issues públicas.
- **Papéis:** a organização dona do ambiente é a controladora dos dados. Este projeto não recebe, não guarda e não trata nenhum dado coletado.
</details>

<details>
<summary><b>Antes de tratar um resultado como final</b></summary>

| Risco | Controle |
|---|---|
| Execução com limite de máquinas oculta achados fora da amostra | Rodada final sem limite (`MaxMachines = 0`) ou escopos completos. |
| `PARTIAL`, `ERROR`, `TODO`, `UNASSESSED` lidos como saudável | Trate como **não avaliado**; corrija permissões/providers e colete de novo. |
| Metadados de versão caíram para tabelas estáticas | Confira a fonte exibida no achado nas release notes atuais da Microsoft. |
</details>

<details>
<summary><b>Análise no navegador (checklist guiado)</b></summary>

O guia HTML offline gera o coletor, registra as decisões do checklist e analisa o `.zip` localmente no navegador (sem rede: `connect-src 'none'`).

- Online: https://fabiotreze.github.io/arc-posture-review/arc-posture-review.pt-BR.html · [English](https://fabiotreze.github.io/arc-posture-review/)
- Offline: [`arc-posture-review.pt-BR.html`](arc-posture-review.pt-BR.html) · [`arc-posture-review.en-US.html`](arc-posture-review.en-US.html)
</details>

<details>
<summary><b>Validar alterações (mantenedores)</b></summary>

```powershell
python -m pip install -r requirements-dev.txt
python tools/Invoke-V4FinalGates.py --profile pr-quality
python tools/Invoke-V4FinalGates.py --profile release
```

Perfis: `pr-quality`, `report-quality`, `release`, `methodology`, `security-regression`. Rodam em uma cópia isolada e não alteram a árvore de trabalho. Os testes Playwright da v4 podem usar o Edge ou Chrome instalado via `ARC_REVIEW_BROWSER` (caminho do executável).
</details>

<details>
<summary><b>Mapa do repositório</b></summary>

```
scripts/Invoke-ArcPostureReview.ps1   coletor somente leitura (gera e compacta o relatório v4 por padrão)
assurance/v4/                         motor, CLI, renderer e gates da v4 (checkpoints)
tools/New-ResourceIndex.py            links do portal Azure no relatório v4
tools/Invoke-V4FinalGates.py          perfis de gate da v4
criteria/checks.*.json                fonte canônica bilíngue das 64 verificações
docs/v4/                              metodologia, modelo de ameaças, registro da revisão de segurança
release/                              manifestos, notas e SHA256SUMS das releases
arc-posture-review.*.html, index.html guia offline e análise no navegador
```
</details>

Metodologia: [docs/v4/methodology-v4.md](docs/v4/methodology-v4.md) · Revisão de segurança: [docs/v4/security-review-record-v4.0.0.md](docs/v4/security-review-record-v4.0.0.md) · Mudanças: [CHANGELOG.md](CHANGELOG.md)

## Contribuições e licença

Dúvidas e correções por [issues](../../issues), citando a documentação oficial da Microsoft; nunca inclua dados de clientes ou do ambiente. Questões de segurança: [SECURITY.md](SECURITY.md).

Código: [MIT](LICENSE). Documentação e textos: [CC BY 4.0](LICENSE-DOCS) — crédito: *"Arc Posture Review" por Fabio Rodrigues Vieira Costa, https://github.com/fabiotreze/arc-posture-review*. Conteúdo de terceiros e marcas (Microsoft, Azure, Azure Arc) continuam com seus donos.
