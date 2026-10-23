# Changelog

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
