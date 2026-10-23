# Changelog

## [3.7.0] — 2026-10-23

### Changed
- **Machine limit now prioritizes risk:** with `-MaxMachines N`, the sample starts with the machines most likely to hide problems, then follows resource group and name. Risk signals: Expired or Disconnected status, legacy OS (Windows Server 2008/2012, then 2016), Connected Machine agent below 1.61, SQL Server detected, and a criticality tag (`criticality`/`tier` = high, critical or Tier 0). The log and the analysis state how many sampled machines carry a risk signal and recommend a full run (or one per resource group) for the final assessment.

### Mudanças (pt-BR)
- O limite de máquinas passa a priorizar risco: desconectadas, SO legado, agente abaixo de 1.61, SQL Server e tag de criticidade entram primeiro na amostra.

## [3.6.1] — 2026-10-23

### Fixed
- The script from versions 3.5.1 and 3.6.0 stopped at start with *"The term 'else' is not recognized"*: a log line had been placed between `if` and `else`. Use 3.6.1 or later.
- New automated check in the build: `else`, `elseif`, `catch` and `finally` must follow the closing brace of the previous block.

### Mudanças (pt-BR)
- Correção: o script das versões 3.5.1 e 3.6.0 parava no início com o erro de `else` não reconhecido. Use a 3.6.1 ou posterior.

## [3.6.0] — 2026-10-23

### Added
- **Machine limit (`-MaxMachines`, "Machine limit" in the UI):** for large estates, evaluates only the first N machines (by resource group and name). Per-machine data and the per-machine Defender plan calls are limited to the sample; the summary, the analysis and `results.json` state "Sample: N of M machines". Subscription-level data (roles, policies, Defender recommendations) still covers the whole scope. 0 = all (default).
- Summary by severity in the quick read (High, Medium, Low: items to address, FAIL, WARN, PASS).
- "Back to the analysis" button after opening a check or the guide from the analysis.
- Collected statuses are applied to the checklist when the package loads, without overwriting statuses you set; the button became "Reapply collected status".

### Fixed
- Script reviewed with PSScriptAnalyzer (code scanning): empty `catch` blocks now log the error in verbose mode (`-Verbose`); functions renamed to standard PowerShell verbs (`Write-Result`, `Add-PermGap`, `Get-ArcWorkspaceId`); unused variable removed; the parameters `ActivityDays`, `RequiredTags` and `AllowedRegions` are written to the log. No change to the checks or results.
- The checklist record and the Markdown report list every check in the loaded package (not only the checks selected in this session), with the collected status.

### Changed
- Code scanning excludes two style rules on purpose: positional parameters (the script style) and `Write-Host` (operator progress output).
- The release automation runs only for numeric tags (`vX.Y.Z` with digits).
- Dependabot groups action updates into one pull request per month.
- **One saved file:** "Save analysis" now includes, at the end, the checklist record (status, collection evidence and notes for every selected check, plus session notes). "Save report (.html)" creates the same file when a package is loaded; without a package it creates only the checklist record. The old "full report" repeated the analysis and was removed. The README describes each output file.

### Mudanças (pt-BR)
- Script revisado pelo PSScriptAnalyzer: `catch` registra o erro com `-Verbose`, funções com verbos padrão, variável sem uso removida, parâmetros no log. As verificações não mudaram.
- Novo limite de máquinas (MaxMachines) para ambientes grandes, com aviso de amostra; resumo por severidade; botão para voltar à análise; status da coleta aplicados ao carregar o pacote.
- Code scanning ignora duas regras de estilo intencionais; release só com tags numéricas; Dependabot agrupado.
- O registro do checklist e o relatório .md trazem todas as verificações do pacote carregado, com o status coletado.
- Um único arquivo salvo: a análise passa a trazer no final o registro do checklist (status, evidência e notas de cada verificação); o antigo relatório completo, que repetia a análise, foi removido.

## [3.5.0] — 2026-10-23

### Changed
- **Kit index on the Defender for Cloud Secure Score model:** each control is worth points by severity (High 3, Medium 2, Low 1) and scores by the share of healthy machines; checks with the same root cause (endpoint protection, telemetry, OS baseline, local agent configuration) form one control and count once; controls without assessment are left out. When the finding is not per machine, PASS = 100%, WARN = 50%, FAIL = 0.
- **Quick read** at the top of the analysis: kit index with its coverage (checks evaluated, documentary pending), official Secure Score, and the three biggest gains (like the Secure Score potential increase).
- **"What to do now" is one row per action**, grouping checks with the same cause, with findings, gain and owner; the step-by-step moved into Priorities, so it is no longer repeated.
- A high-severity FAIL is always an immediate action.
- New indicators: Defender for Servers, compliant OS baseline, periodic patch assessment, telemetry (DCR).

### Fixed
- Compliance text said MCSB v1; it now says v2.
- Layers outside the compliance measure (customer decision, program, FinOps) no longer show a percentage.
- A WARN with no item count shows "1 gap" instead of "0 findings".

### Mudanças (pt-BR)
- Índice do kit no modelo do Secure Score: pontos por severidade, proporção de máquinas saudáveis e causas comuns contadas uma vez.
- Leitura rápida no topo (cobertura, Secure Score, maiores ganhos); plano de ação em uma linha por ação; FAIL de severidade alta sempre imediato; novos indicadores.
- Correções: MCSB v2 no texto, camadas fora da conformidade sem percentual, "1 lacuna" em vez de "0 achado(s)".

## [3.4.0] — 2026-10-23

### Added
- **CHK-63 Defender for Servers per Arc machine:** reads the Defender for Servers plan on each `Microsoft.HybridCompute/machines` resource (resource-level Pricings API, read-only GET) and compares it with the subscription plan. FAIL if a machine has no plan (Free); WARN if the machine plan differs from the subscription (set on the machine itself); PASS if every machine inherits the subscription plan.
- The analysis lists the plan per machine (tier, subplan, inherited or set on the machine, enabled extensions).
- Release badge in the README.
- GitHub Actions: a release is published automatically when a `vX.Y.Z` tag is pushed (notes from this CHANGELOG, script attached); PSScriptAnalyzer results in Security > Code scanning; Dependabot keeps the actions up to date.

### Changed
- The cost estimate (CHK-53) uses the actual plan of each machine when it was read.
- The script's `az rest` allowlist accepts one more read-only call: the Defender plan of an Arc machine.

### Fixed
- Roles not in the built-in map are labeled "Unmapped role (ID)" instead of "Custom/unknown" (many are built-in roles that do not affect the checks).
- CHK-40 (AMA without DCR) is N/A when no connected machine has the Azure Monitor Agent, instead of PASS.
- CHK-41 (Sentinel) states how many workspaces receive Arc machine data, consistent with the Arc-centric scope of CHK-45.

### Mudanças (pt-BR)
- Nova verificação CHK-63: plano do Defender for Servers lido em cada máquina Arc. FAIL sem plano (Free); WARN se diferente da subscription; PASS se todas herdam.
- A estimativa de custo usa o plano real de cada máquina; selo de release no README.
- Correções: papéis fora do mapa aparecem como "não mapeado"; CHK-40 vira N/A sem AMA; CHK-41 informa quantos workspaces recebem dados do Arc.

## [3.3.0] — 2026-10-23

### Changed
- **Arc-centric scope:** every check now starts from the collected `Microsoft.HybridCompute/machines`. Role assignments, policy assignments, Key Vaults and Log Analytics workspaces are evaluated only when they reach the Arc machines (management group, the machines' subscription or resource group, or workspaces that receive Arc data through a DCR). Resources from other resource groups are counted as "outside the Arc scope (ignored)" instead of affecting the result. Secure Score is labeled as a subscription-wide measure.
- **Microsoft Cloud Security Benchmark v2 (preview):** control IDs updated to MCSB v2. The Governance and strategy (GS) domain, removed in v2, was remapped to Asset management, Posture and vulnerability management and Privileged access (CHK-02, 03, 04, 05, 16, 50, 52). Framework mappings now cite CIS Controls v8.1, NIST SP 800-53 Rev.5, PCI-DSS v4, NIST CSF 2.0, ISO 27001:2022 and SOC 2. The published Arc-enabled servers baseline still uses v1; control IDs are unchanged between versions.

### Added
- Coverage inventory by MCSB v2 domain (Appendix J), including the domains with no checks and why (backup, DevOps and AI are outside the Arc-enabled servers scope).
- References: all MCSB v2 domains and mappings, Arc regulatory compliance controls, Windows Server 2025 security baseline, Best Practices Assessment, Windows Recovery Environment (WinRE).
- Release check that confirms the same version in the HTML, guide, script, CHANGELOG and CITATION.
- Saved analysis and report files now include the language, like the README: `arc-posture-review-analysis-<date>.pt-BR.html` / `.en-US.html`, and `arc-posture-review-report.pt-BR.md` / `.json`.

### Fixed
- Role checks (CHK-10, 11, 25) did not see built-in roles: Resource Graph does not return built-in role definitions per subscription, so role names came back empty. Built-in roles are now resolved by their published fixed IDs; unknown custom roles are labeled with their ID.

### Mudanças (pt-BR)
- Escopo centrado no Azure Arc: papéis, policies, Key Vaults e workspaces só contam quando alcançam as máquinas Arc; o resto aparece como ignorado.
- Controles atualizados para o MCSB v2 (preview); o domínio Governança e estratégia foi remapeado; inventário de cobertura por domínio do MCSB v2; novas referências.
- Arquivos salvos com o idioma no nome (.pt-BR / .en-US); correção: papéis built-in agora são reconhecidos nas verificações de RBAC.

## [3.2.0] — 2026-10-23

### Added
- 8 new checks (54 → 62; automated 38 → 43, documentary 16 → 19). Existing IDs are unchanged; the new ones are CHK-55 to CHK-62:
  - CHK-55 **OS security baseline** — Azure compute security baseline (Windows/Linux) assigned and compliant per machine (Machine Configuration).
  - CHK-56 **Local administrators audit** — Machine Configuration audit of the local Administrators group.
  - CHK-57 **Healthy antivirus and EDR** — Defender for Cloud endpoint protection recommendations plus MDE extension presence.
  - CHK-58 **Insights and telemetry per machine** — performance, VM Insights/dependency map, events/Syslog, security events and Change Tracking via DCRs.
  - CHK-59 **Map of Arc capabilities in use** — extensions, periodic patch assessment, Machine Configuration, Windows Server Management benefits, Hotpatch and ESU.
  - CHK-60 **Windows LAPS**, CHK-61 **System disk encryption (BitLocker/dm-crypt)**, CHK-62 **Conditional Access and MFA for Azure administrators** (documentary).
- New read-only collection `gcComp` (Machine Configuration assignment compliance), covered by the existing Reader permission.
- **Coverage inventory** in the guide (Appendix J): totals per domain, automated/documentary, severity, assessment layer and decision tree, with the change from the previous version.
- References: Windows Server Management enabled by Azure Arc, Hotpatch, Windows/Linux security baselines, VM Insights, Change Tracking, Windows LAPS, BitLocker, Conditional Access and mandatory MFA.

### Fixed
- CHK-29 (agent version) failed with an evaluation error in v3.1.0 (`cves` column outside the result object). Found in a lab run and fixed; the collector now passes an automated check for this class of error.
- The full report generated without a loaded package now states that automated checks show as TODO.
- CHK-57 matched unrelated Defender recommendations (for example a removable drive scan setting) and failed on low severity items. It now matches whole words and fails only on high or medium severity; low severity gives a warning.

### Changed
- English version shows ERROR, PARTIAL, MISSING and UNKNOWN instead of the Portuguese status codes (package codes unchanged, older packages still accepted).

### Mudanças (pt-BR)
- 8 verificações novas (54 → 62): baseline de segurança do SO, auditoria de administradores locais, antivírus e EDR, insights e telemetria, mapa de recursos do Arc, Windows LAPS, criptografia de disco e Acesso Condicional/MFA.
- Inventário de cobertura por versão no guia (Anexo J); status em inglês na versão en-US.
- Correção: o CHK-29 (versão do agente) dava erro de avaliação na v3.1.0; relatório sem pacote carregado agora avisa que as automáticas ficam TODO.

## [3.1.0] — 2026-10-23

### Added
- Agent security floor **1.61**: the collector (CHK-29) and the ALR-03 alert query mark older agents as vulnerable, listing the CVEs (CVE-2025-49692, CVE-2025-26627, CVE-2025-55316, CVE-2026-26117).
- CVE table in the guide (OPS-05) with affected and fixed versions, plus agent (CVE-2025-58724), SQL extension (CVE-2026-62895) and Microsoft-hosted service CVEs (for example CVE-2026-24302, no server action), and a monthly CVE follow-up.
- Services catalog: the daily `azcmagent` scheduled task, the GPO deployment scheduled task and the delayed-start agent services.
- Onboarding hardening (REQ-08): service principal limited to *Azure Connected Machine Onboarding*, short-lived secrets, GPO and deployment task removed after onboarding.
- References: CAF hybrid and multicloud landing zone and the Arc-enabled servers design areas, *choose the Azure Arc service*, privileged access rapid modernization plan, and public security research cited as context. The hybrid CAF articles are flagged as deprecated by Microsoft (removal planned for 2026-10-30), with the Azure Architecture Center hybrid guidance as the current alternative.

### Fixed
- "Expand all" / "Collapse all" now show their active state; open section headers are highlighted.
- Agent version table no longer breaks the analysis when a package is loaded.
- Remaining Portuguese labels in the English build.

### Validation
- 72 automated UI tests (Playwright) pass in both languages.

### Mudanças (pt-BR)
- Piso de segurança do agente 1.61 (CHK-29 e ALR-03) com as CVEs; tabela de CVEs no OPS-05 (agente, extensão SQL e serviço hospedado).
- Tarefas agendadas do agente e da implantação por GPO, e serviços com início atrasado, no catálogo de serviços.
- Endurecimento do onboarding (service principal e GPO); referências do CAF híbrido.
- Botões Expandir/Recolher tudo com estado ativo; correção ao carregar o pacote; 72 testes de interface aprovados nos dois idiomas.

## [3.0.0] — 2026-10-23

First public release as **Arc Posture Review** (previously an internal working name).

### Changed
- New name everywhere: repository `arc-posture-review`, script `Invoke-ArcPostureReview.ps1`, package `arc-posture-review-*.zip`, files `arc-posture-review.en-US.html` / `.pt-BR.html` (`index.html` is the English version), guides `docs/guide.en-US.md` / `docs/guide.pt-BR.md`.
- Lean repository: ready-to-use HTML files, standalone script and guides only.
- "Start here" map with clickable decision cards and every decision tree drawn as a Yes/No flowchart (tables collapsed).
- Content origin, AI-assistance and user-responsibility notices in the guide, the reports, README and DISCLAIMER.
- Results highlighted with the Advisor / Defender for Cloud palette: status chips with icon + text + color, severity dots, KPI cards, status and severity colored inside tables; AA contrast, dark mode, high contrast (forced colors) and reduced motion.
- Package compatibility is now checked by schema: packages from v2.x are still accepted (with a version warning); only newer schemas are rejected.
- Browser storage key renamed (old saved fields are not loaded).
- README and DISCLAIMER in English with Portuguese versions.

### Mudanças (pt-BR)
- Novo nome em tudo (repositório, script, pacote, arquivos e guias); `index.html` é a versão em inglês; repositório enxuto.
- "Comece aqui" com cartões clicáveis e árvores em fluxograma Sim/Não.
- Avisos de origem do conteúdo, uso de IA e responsabilidade do usuário.
- Resultados destacados com a paleta do Advisor / Defender for Cloud, acessíveis (ícone, texto e cor; contraste AA; modo escuro; alto contraste).
- Pacotes da v2.x continuam aceitos (com aviso de versão).

## [2.6.0] — 2026-10-23

### Adicionado
- Versão em inglês (en-US) gerada da mesma fonte, em arquivos separados (`*.pt-BR.html` e `*.en-US.html`, `docs/playbook.md` e `docs/playbook.en-US.md`), com link entre as duas.
- Validação do pacote ao carregar: origem (ferramenta e versão), estrutura de resultados, SHA-256 de cada arquivo contra o manifest, arquivos fora do manifest, caminhos inválidos e limites de tamanho; pacote alterado é rejeitado e não pode ser aplicado ao checklist.
- O script imprime o SHA-256 do .zip no final e grava `<pacote>.zip.sha256`; o checklist mostra o hash do arquivo carregado para comparação.
- Causa "dependência ausente no SO (Python)" para extensões com falha (MDE.Linux e atualização de SO no Linux), com orientação no plano de ação.

### Alterado
- Tabelas da análise e do relatório com rótulos de coluna legíveis.
- Revisão ortográfica do texto em português.

## [2.5.0] — 2026-10-22

### Alterado
- Método explícito e público: ciclo de sustentação de postura do CAF Secure (avaliar, medir, priorizar, remediar e automatizar, reportar), medido contra o MCSB v1 no Defender for Cloud.
- Cada verificação passa a ter camada (1 MCSB · 2 Baseline do SO · 3 Requisito do Arc · 4 Decisão do cliente · Programa · FinOps), controle MCSB v1 e árvore de decisão; isso aparece no guia, no checklist, na análise e no relatório.
- Guia reorganizado: 1 Método, 2 Árvores de decisão D1–D9 + execução do programa (cada árvore com pergunta, até 5 decisões, resultado, controles MCSB e verificações; itens DEC/REQ/CTL/OPS/LEG como detalhes), 3 Checklist, 4 Plano de ação, 5 Alertas e anexos A–J (mapas, fluxo por fase, serviços, rastreabilidade, evidências, movimento lateral, mapeamento MCSB, referências, curadoria, histórico). Nenhum conteúdo removido.
- HTML menos poluído: seções do guia e da análise recolhíveis (Expandir/Recolher tudo; links abrem o trecho certo; impressão expande tudo); sumário com anexos compactos.
- Análise: "Conformidade por camada e controle MCSB" e Secure Score no topo; ordem executiva (conformidade, indicadores, o que fazer agora) e detalhes recolhidos.
- Relatório: resumo executivo, conformidade e plano de ação antes do detalhe por verificação; cabeçalhos legíveis; camada e MCSB no plano.
- "Postura ponderada" passa a se chamar "índice do kit" e é identificado como apoio, sem substituir o Secure Score e a conformidade MCSB.

### Corrigido
- A análise não carregava os arquivos de atribuições de Machine Configuration, alertas, vulnerabilidades e Secure Score do pacote (Secure Score não aparecia no relatório).
- Símbolo de seleção do preset aparecia como "¹3".

## [2.4.0] — 2026-10-22

### Corrigido
- Blocos do plano de ação e dos alertas abrem por clique ou teclado em qualquer navegador; CHK e ALR viraram links (checklist e guia) e cada alerta do plano leva ao bloco do alerta.

### Adicionado
- CHK-54 Ameaças e vulnerabilidades (Defender for Cloud): alertas de segurança ativos, vulnerabilidades por alcance e severidade e Secure Score por subscription, com a classificação do próprio Defender.
- Secure Score no resumo executivo do relatório.
- Diagramas: ciclo de vida fim a fim (2.4), identidade e acesso no onboarding e na operação (2.5) e remoção individual e em escala (OPS-07/OPS-08), com o procedimento oficial (extensões, azcmagent disconnect, desinstalação, limpeza; --force-local-only no Azure Local; limpeza de recursos stale).

### Alterado
- OPS-12 e CHK-50: revisão mensal manual dos avisos de segurança do Service Health (o detalhe exige papel acima de Reader).
- CTL-06: alertas, vulnerabilidades e uso da severidade do Defender; a categoria Security do Advisor repete o Defender.

## [2.3.1] — 2026-10-22

### Adicionado
- Extensões com falha classificadas pela causa (mensagem do instanceView): bloqueio pela allowlist do agente, rede, tempo esgotado ou outra.
- Avaliação de patches detecta máquinas com AutomaticByPlatform cuja extensão de patch falhou.
- Inventário passa a ler atualização automática do agente, status do serviço de guest configuration, elegibilidade de ESU e o recurso Windows Server Management (benefício de Software Assurance) usado na estimativa de custo.

## [2.3.0] — 2026-10-22

### Adicionado
- Plano de ação por verificação (prazo, responsável sugerido, o que fazer, como decidir e documentação oficial), no guia (seção 10.1), na análise ("O que fazer agora") e no relatório.
- Alertas recomendados (ALR-01 a ALR-09) com consultas prontas para Azure Monitor (Resource Graph via arg e Activity Log), no guia (seção 10.2), na análise e no relatório.
- Versões do agente e da extensão SQL avaliadas pela data da execução (idade em meses e suporte de 12 meses); extensões comparadas com a mais nova do parque, atualização automática e falhas.
- Cobertura do Sentinel: DCRs que enviam ao workspace do Sentinel, máquinas Arc cobertas, fluxos, retenção e exportação do Activity Log; DCRs em uso e destinos na verificação de DCR.
- Etapa 5 renomeada para "Plano e entrega", com o propósito de cada saída e resumo executivo no relatório.

## [2.2.0] — 2026-10-22

### Adicionado
- REQ-09 e verificação de custo (CHK-53): estimativa mensal em preço de lista por servidor (Defender, Update Manager, Machine Configuration/Change Tracking, WS PAYG), benefícios (Software Assurance atestado, WS PAYG, ESU, Defender P2) e economia possível; nova coleta de atribuições de Machine Configuration.
- DEC-01 alinhado ao assistente *Help me choose* do portal (3 perguntas e 4 métodos de onboarding com tempos).

### Alterado
- Legado (LEG-01/03/04 e CHK-51): fim do ESU do Windows Server 2012/2012 R2 em 13/10/2026 (FAIL) e preparação do ESU do Windows Server 2016 (fim do suporte em 12/01/2027, agente 1.62+).
- Botões de seleção rápida (Essenciais, Todas, Nenhuma) com estado visível, contagem e progresso por domínio.
- Análise e relatório podem ser salvos: análise em HTML estático (com os itens de cada prioridade), relatório completo em HTML, impressão/PDF, e o relatório .md/.json passa a incluir resultado, permissões, prioridades, matriz por subscription, cenários cross-subscription e a avaliação de cada arquivo.

### Corrigido
- Escopo vazio quando a CLI não tem subscription padrão: o script usa as subscriptions habilitadas da conta e mostra o escopo usado.

## [2.1.0] — 2026-10-22

### Adicionado
- Validação das permissões efetivas da conta de coleta por subscription (somente leitura, `Microsoft.Authorization/permissions`), com resultado no console, `findings/permissions.csv`, `summary.md`, `results.json` e na aba de análise.
- Controles automáticos afetados por falta de leitura passam a ser marcados como PARCIAL ou ERRO.
- Layout em assistente de 5 etapas (Guia, Preparar coleta, Resumo, Análise, Relatório) com o estado de cada etapa.
- Validação dos campos antes de baixar ou copiar o script (IDs, management group, resource group, máquina, dias, tags, regiões, pasta de saída e seleção de verificações), com mensagem no próprio campo.
- Escopo por tipo (subscription atual, lista de subscriptions ou management group) e opções avançadas recolhidas.

### Corrigido
- Compatibilidade com PowerShell 7.6 (Cloud Shell): gravação de `results.json` e `manifest.json` sem o erro "Argument types do not match"; cálculo de duração e de dias sem subtração de datas.
- CHK-17 (modelo de conectividade) voltou a ser avaliado.

## [2.0.0] — 2026-10-22
- Fonte única para guia (.md) e checklist (.html): 52 verificações (CHK) vinculadas a 40 itens do playbook, nos dois sentidos.
- Script PowerShell somente leitura baseado em Azure Resource Graph (paginado, sem laço por máquina, várias subscriptions ou management group).
- Análise do pacote no navegador: postura ponderada, matriz por subscription, cross-subscription, avaliação por arquivo, integridade SHA-256.
- Novas verificações: região/residência de dados, Sentinel, SQL Arc (Defender for SQL, menor privilégio, data processing service sem Private Link), suporte de versão do agente e da extensão SQL (12 meses).
- Diagramas: fluxo do playbook, conectividade público × privado, fluxo da coleta, decisão DEC-01.
- Tags passam a ser recomendação (boa prática).

## [1.4.0]
- Versão anterior (checklist manual CHK-01..22).
