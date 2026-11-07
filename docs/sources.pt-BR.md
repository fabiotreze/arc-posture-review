# Fontes e fundamento das afirmações

Cada limiar, data e rótulo usado pelo coletor e pelos relatórios está registrado em `criteria/v4/sources.json` com o estado do seu fundamento. Esta página é gerada por `tools/Sync-Sources.py`; o `tools/Test-ClaimRegister.py` falha quando o coletor ganha um limiar que não está registrado.

## Como ler o estado

- **Fonte oficial**: a página da Microsoft foi aberta por inteiro e o trecho citado sustenta a afirmação.
- **Registro oficial de CVE**: confirmado no registro do CVE no NVD, que cita o aviso do MSRC.
- **Critério do kit**: um critério deste kit, **não** uma recomendação da Microsoft; a justificativa diz por que ele existe.
- **A verificar**: ainda não confirmado em fonte oficial; o resultado aparece, mas não deve ser apresentado como oficial até a pendência ser fechada.

## Resumo

| Id | Afirmação | Verificações | Estado | Verificado em |
|---|---|---|---|---|
| `AGENT-SUPPORT-12M` | Só as versões do agente Connected Machine lançadas no último ano têm suporte oficial. | CHK-29 | Fonte oficial | 2026-11-06 |
| `AGENT-RELEASE-CALENDAR` | Meses de lançamento do agente usados para datar uma versão: 1.57 (2025-10) a 1.69 (2026-10). | CHK-29 | Fonte oficial | 2026-11-06 |
| `AGENT-SEC-FLOOR-61` | Agentes abaixo da 1.61 são afetados pelo CVE-2026-26117 (elevação local de privilégio, CVSS 7,8). O piso 1.61 é a maior versão corrigida entre os CVEs do agente Arc listados aqui. | CHK-29 | Registro oficial de CVE | 2026-11-06 |
| `AGENT-CVE-2025-55316` | O CVE-2025-55316 afeta agentes abaixo da 1.56. | CHK-29 | Registro oficial de CVE | 2026-11-06 |
| `AGENT-CVE-2025-49692` | O CVE-2025-49692 afeta agentes abaixo da 1.49. | CHK-29 | Registro oficial de CVE | 2026-11-06 |
| `AGENT-CVE-2025-26627` | O CVE-2025-26627 não é mapeado a uma versão do agente: o NVD lista o produto 'Azure ARC' abaixo de 1.0.10, que não corresponde à numeração do agente Connected Machine. Ele não aparece por máquina. | CHK-29 | A verificar | 2026-11-06 |
| `AGENT-AUTOUPGRADE-MIN-167` | O upgrade automático do agente exige o agente 1.67 ou superior (Windows: política de execução RemoteSigned; Linux: cron). Só está disponível na nuvem pública do Azure. | CHK-29 | Fonte oficial | 2026-11-06 |
| `AGENT-AUTOUPGRADE-LOCALBLOCK` | A configuração local automaticupgrade.blocklocally tem precedência sobre a propriedade do Azure enableAutomaticUpgrade: com valor true, os upgrades automáticos ficam bloqueados mesmo que a propriedade do Azure seja true. Lê-se na máquina com 'azcmagent config get automaticupgrade.blocklocally', não pelo Azure. | CHK-29, CHK-36 | Fonte oficial | 2026-11-06 |
| `AGENT-OLD-6M` | Um agente com suporte, mas com mais de 6 meses, é um alerta. | CHK-29 | Critério do kit | 2026-11-06 |
| `AMA-SUPPORT-12M` | A Microsoft só dá suporte às versões do Azure Monitor Agent lançadas no último ano. | CHK-30 | Fonte oficial | 2026-11-06 |
| `SQLEXT-SUPPORT-12M` | Só as versões da extensão do Azure para SQL Server lançadas no último ano têm suporte. | CHK-30, CHK-34 | Fonte oficial | 2026-11-06 |
| `SQLEXT-TARGET` | O alvo atual do upgrade automático da extensão do Azure para SQL Server é 1.1.3518.465 (agosto de 2026); o valor lido do Azure prevalece quando for maior. | CHK-30, CHK-34 | Fonte oficial | 2026-11-06 |
| `SQLEXT-MIN-2859` | Extensão SQL abaixo de 1.1.2859.223 é reportada. | CHK-34 | A verificar | 2026-11-06 |
| `AGENT-DISCONNECT-45D` | Uma máquina que permanece desconectada por 45 dias pode passar para Expired e precisa ser desconectada e reconectada (novo onboarding) para voltar a ser gerenciada. | CHK-37 | Fonte oficial | 2026-11-06 |
| `AGENT-DISCONNECT-30D` | Uma máquina desconectada por 30 a 44 dias está na faixa de alerta, antes da expiração de 45 dias. | CHK-37 | Critério do kit | 2026-11-06 |
| `ESU-2012-END` | O ESU do Windows Server 2012/2012 R2 termina em 2026-10-13; as licenças ESU habilitadas pelo Azure Arc são desativadas às 00:00 UTC de 2026-10-14. O ESU pelo Arc para o 2012 exige o agente 1.34 ou superior. | CHK-51 | Fonte oficial | 2026-11-06 |
| `ESU-2016` | O Windows Server 2016 chega ao fim do suporte em 2027-01-12; o ESU pode ser configurado no portal do Azure a partir de 2026-08-03 e a cobrança pelo Azure Arc começa em 2027-01-13; o agente deve ser 1.62 ou superior. | CHK-51 | Fonte oficial | 2026-11-06 |
| `ESU-2008` | O ESU entregue pelo Azure Arc está documentado para Windows Server 2012, 2012 R2 e 2016; o Windows Server 2008 não consta. | CHK-51 | Fonte oficial | 2026-11-06 |
| `AGENT-PORTS-CHANNELS` | incomingconnections.ports lista as portas locais que o canal de conectividade do Azure Arc pode alcançar (várias portas se separam por vírgula). O SSH usa a porta 22 por padrão (uma única porta por configuração de serviço) e o Windows Admin Center é implantado pela extensão AdminCenter em uma porta configurável (os exemplos usam 6516). Qualquer outra porta é reportada como não classificada. | CHK-21 | Fonte oficial | 2026-11-06 |
| `SQL-USAGE-24H` | Um envio de uso do SQL com mais de 24 horas é reportado como desatualizado. | CHK-64 | Fonte oficial | 2026-11-06 |
| `SQL-PAYG-30D` | Uma máquina SQL Server com pay-as-you-go precisa se comunicar com o Azure ao menos a cada 30 dias; acima de 30 dias desconectada, a cobrança passa a ser recorrente com base na última configuração conhecida. | CHK-64 | Fonte oficial | 2026-11-06 |
| `ACTIVITYLOG-90D` | O Activity Log guarda 90 dias de forma nativa. | CHK-43 | Fonte oficial | 2026-11-06 |
| `LA-RETENTION-90D` | Um workspace do Log Analytics que recebe dados do Arc e retém menos de 90 dias é um alerta. | CHK-45 | Critério do kit | 2026-11-06 |
| `DEFENDER-OPEN-90D` | Recomendações do Defender abertas há 90 dias ou mais são contadas à parte no detalhe (informativo). | CHK-33 | Critério do kit | 2026-11-06 |
| `DEFENDER-HIGH-FAIL` | Uma recomendação do Defender de severidade High que afeta uma máquina Arc é uma lacuna verificada (FAIL); só severidades menores são oportunidade de melhoria (WARN). | CHK-33 | Critério do kit | 2026-11-06 |
| `PRICES-GC` | Azure Policy guest configuration (machine configuration) e Change Tracking & Inventory custam USD 6 por servidor por mês (preço de lista). | CHK-53 | Fonte oficial | 2026-11-06 |
| `PRICES-LIST` | Preços de tabela em USD usados na estimativa mensal (Defender for Servers P1/P2, Update Manager, Machine Configuration, Windows Server pay-as-you-go). | CHK-53 | A verificar | 2026-11-06 |
| `KIT-INDEX` | O índice do kit não é o Secure Score do Defender for Cloud. A Microsoft dá a cada controle uma pontuação máxima fixa e a divide entre os recursos saudáveis e não saudáveis; o kit pondera os controles por severidade (Alta 3, Média 2, Baixa 1) e os pontua pela proporção de máquinas saudáveis. | - | Critério do kit | 2026-11-06 |
| `PRIORITY-SCALE` | As pontuações de risco residual se traduzem em prioridades P0 (80 ou mais), P1 (60), P2 (35) e P3. Prioriza trabalho de postura; não é severidade de incidente. | - | Critério do kit | 2026-11-06 |
| `SCENARIOS-AS` | Os 11 cenários de segurança (AS01-AS11) e seus caminhos de ataque são hipóteses escritas pelo autor; um ataque nunca é afirmado como confirmado. | - | Critério do kit | 2026-11-06 |
| `MCSB-ZT-MAPPING` | O mapeamento de cada verificação para controles do Microsoft Cloud Security Benchmark, princípios e pilares do Zero Trust e tiers é a leitura do autor, com um nível de confiança por verificação. | - | Critério do kit | 2026-11-06 |

## Registros

### AGENT-SUPPORT-12M — Fonte oficial

Só as versões do agente Connected Machine lançadas no último ano têm suporte oficial.

- **Evidência:** "Only Connected Machine agent versions within the last year are officially supported by the product group."
- [Overview of the Azure Connected Machine agent](https://learn.microsoft.com/en-us/azure/azure-arc/servers/agent-overview)
- [Manage Azure Connected Machine agent versions](https://learn.microsoft.com/en-us/azure/azure-arc/servers/manage-agent)

### AGENT-RELEASE-CALENDAR — Fonte oficial

Meses de lançamento do agente usados para datar uma versão: 1.57 (2025-10) a 1.69 (2026-10).

- **Evidência:** Release notes headings 'Version 1.60 - January 2026' to 'Version 1.69 - October 2026' match the table. Versions 1.57 to 1.59 are corroborated by the release calendar of the Arc agent support workbook (https://github.com/fabiotreze/AzureArcBRTips/tree/main/workbooks/arc-agent-support), not by the page section opened.
- [What's new with the Azure Connected Machine agent](https://learn.microsoft.com/en-us/azure/azure-arc/servers/agent-release-notes)
- **Rever até:** 2026-12-06

### AGENT-SEC-FLOOR-61 — Registro oficial de CVE

Agentes abaixo da 1.61 são afetados pelo CVE-2026-26117 (elevação local de privilégio, CVSS 7,8). O piso 1.61 é a maior versão corrigida entre os CVEs do agente Arc listados aqui.

- **Evidência:** NVD: product 'Arc Enabled Servers - Azure Connected Machine Agent', affected versions 1.0.0 up to (excluding) 1.61.
- [NVD: CVE-2026-26117](https://nvd.nist.gov/vuln/detail/CVE-2026-26117)
- [MSRC: CVE-2026-26117](https://msrc.microsoft.com/update-guide/vulnerability/CVE-2026-26117)

### AGENT-CVE-2025-55316 — Registro oficial de CVE

O CVE-2025-55316 afeta agentes abaixo da 1.56.

- **Evidência:** NVD: Azure Connected Machine Agent, affected 1.0.0 up to (excluding) 1.56.
- [NVD: CVE-2025-55316](https://nvd.nist.gov/vuln/detail/CVE-2025-55316)

### AGENT-CVE-2025-49692 — Registro oficial de CVE

O CVE-2025-49692 afeta agentes abaixo da 1.49.

- **Evidência:** NVD: Azure Connected Machine Agent, affected 1.0.0 up to (excluding) 1.49.
- [NVD: CVE-2025-49692](https://nvd.nist.gov/vuln/detail/CVE-2025-49692)

### AGENT-CVE-2025-26627 — A verificar

O CVE-2025-26627 não é mapeado a uma versão do agente: o NVD lista o produto 'Azure ARC' abaixo de 1.0.10, que não corresponde à numeração do agente Connected Machine. Ele não aparece por máquina.

- **Pendência:** Confirm in the MSRC advisory which component and fixed agent version apply before listing it per machine.
- [NVD: CVE-2025-26627](https://nvd.nist.gov/vuln/detail/CVE-2025-26627)

### AGENT-AUTOUPGRADE-MIN-167 — Fonte oficial

O upgrade automático do agente exige o agente 1.67 ou superior (Windows: política de execução RemoteSigned; Linux: cron). Só está disponível na nuvem pública do Azure.

- **Evidência:** "All Arc-enabled servers: Azure Connected Machine agent version 1.67 or later is required."
- [Automatically upgrade the Azure Connected Machine agent](https://learn.microsoft.com/en-us/azure/azure-arc/servers/automatic-agent-upgrade)

### AGENT-AUTOUPGRADE-LOCALBLOCK — Fonte oficial

A configuração local automaticupgrade.blocklocally tem precedência sobre a propriedade do Azure enableAutomaticUpgrade: com valor true, os upgrades automáticos ficam bloqueados mesmo que a propriedade do Azure seja true. Lê-se na máquina com 'azcmagent config get automaticupgrade.blocklocally', não pelo Azure.

- **Evidência:** "The automaticupgrade.blocklocally setting takes precedence over the enableAutomaticUpgrade property." The option was introduced in agent 1.61 (release notes: 'Added option to disable automatic upgrades locally').
- [Automatically upgrade the Azure Connected Machine agent (section: Block automatic agent upgrades locally)](https://learn.microsoft.com/en-us/azure/azure-arc/servers/automatic-agent-upgrade)

### AGENT-OLD-6M — Critério do kit

Um agente com suporte, mas com mais de 6 meses, é um alerta.

- **Justificativa:** Microsoft publishes a 12-month support window, not a 6-month one. The kit warns at half of the window so the upgrade is planned before support ends.

### AMA-SUPPORT-12M — Fonte oficial

A Microsoft só dá suporte às versões do Azure Monitor Agent lançadas no último ano.

- **Evidência:** "Microsoft supports Azure Monitor Agent versions released within the last year only."
- [Azure Monitor Agent extension versions](https://learn.microsoft.com/en-us/azure/azure-monitor/agents/azure-monitor-agent-extension-versions)

### SQLEXT-SUPPORT-12M — Fonte oficial

Só as versões da extensão do Azure para SQL Server lançadas no último ano têm suporte.

- **Evidência:** "Only Azure extension for SQL Server versions released within the last year are supported."
- [Release notes - SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/release-notes?view=sql-server-ver17)

### SQLEXT-TARGET — Fonte oficial

O alvo atual do upgrade automático da extensão do Azure para SQL Server é 1.1.3518.465 (agosto de 2026); o valor lido do Azure prevalece quando for maior.

- **Evidência:** "The current auto-upgrade target version of the Azure extension for SQL Server is 1.1.3518.465".
- [Release notes - SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/release-notes?view=sql-server-ver17)
- **Rever até:** 2026-12-06

### SQLEXT-MIN-2859 — A verificar

Extensão SQL abaixo de 1.1.2859.223 é reportada.

- **Pendência:** The release notes (checked 2026-11-06) do not state a minimum version. 1.1.2859.223 is a November 2024 release ("Minor bug fixes") and the current auto-upgrade target is 1.1.3518.465 (August 2026). Decide whether to keep it as a kit criterion with a rationale or replace it by a 12-month window computed from the release table.
- [Release notes - SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/release-notes?view=sql-server-ver17)

### AGENT-DISCONNECT-45D — Fonte oficial

Uma máquina que permanece desconectada por 45 dias pode passar para Expired e precisa ser desconectada e reconectada (novo onboarding) para voltar a ser gerenciada.

- **Evidência:** "If a machine remains disconnected for 45 days, its status might change to Expired. An expired machine can't be managed through Azure Arc until a server administrator disconnects and then reconnects it to Azure. ... The credential is valid for up to 90 days and renews every 45 days."
- [Azure Arc-enabled servers overview - Agent status](https://learn.microsoft.com/en-us/azure/azure-arc/servers/overview#agent-status)

### AGENT-DISCONNECT-30D — Critério do kit

Uma máquina desconectada por 30 a 44 dias está na faixa de alerta, antes da expiração de 45 dias.

- **Justificativa:** Microsoft documents the 45-day point, not a 30-day one. The kit warns 15 days earlier so the machine can be reconnected before it expires and a new onboarding is needed.

### ESU-2012-END — Fonte oficial

O ESU do Windows Server 2012/2012 R2 termina em 2026-10-13; as licenças ESU habilitadas pelo Azure Arc são desativadas às 00:00 UTC de 2026-10-14. O ESU pelo Arc para o 2012 exige o agente 1.34 ou superior.

- **Evidência:** "The three-year ESU period ends on October 13, 2026 ... At midnight UTC on October 14, 2026, Windows Server 2012 ESU licenses enabled by Azure Arc are deactivated".
- [Prepare to deliver Extended Security Updates for Windows Server through Azure Arc](https://learn.microsoft.com/en-us/azure/azure-arc/servers/prepare-extended-security-updates)

### ESU-2016 — Fonte oficial

O Windows Server 2016 chega ao fim do suporte em 2027-01-12; o ESU pode ser configurado no portal do Azure a partir de 2026-08-03 e a cobrança pelo Azure Arc começa em 2027-01-13; o agente deve ser 1.62 ou superior.

- **Evidência:** "Windows Server 2016 reaches end of support on January 12, 2027 ... starting August 3, 2026 ... Billing ... begins January 13, 2027 ... use agent version 1.62 or higher."
- [Prepare to deliver Extended Security Updates for Windows Server through Azure Arc](https://learn.microsoft.com/en-us/azure/azure-arc/servers/prepare-extended-security-updates)
- **Rever até:** 2027-01-12

### ESU-2008 — Fonte oficial

O ESU entregue pelo Azure Arc está documentado para Windows Server 2012, 2012 R2 e 2016; o Windows Server 2008 não consta.

- **Evidência:** "By using Azure Update Manager, you can deploy Extended Security Updates for your Azure Arc-enabled Windows Server 2012, 2012 R2, and 2016 machines." The Arc ESU pages list no other Windows Server version.
- [Extended Security Updates (ESU) for Windows Server with Azure Update Manager](https://learn.microsoft.com/en-us/azure/update-manager/extended-security-updates)

### AGENT-PORTS-CHANNELS — Fonte oficial

incomingconnections.ports lista as portas locais que o canal de conectividade do Azure Arc pode alcançar (várias portas se separam por vírgula). O SSH usa a porta 22 por padrão (uma única porta por configuração de serviço) e o Windows Admin Center é implantado pela extensão AdminCenter em uma porta configurável (os exemplos usam 6516). Qualquer outra porta é reportada como não classificada.

- **Evidência:** WAC page: "azcmagent config set incomingconnections.ports <port> ... you can specify multiple ports separated by a comma"; deployment example `$wacPort = "6516"` with extension AdminCenter (publisher Microsoft.AdminCenter). SSH page: "You may only allow connection to a single port", default 22.
- [Manage Azure Arc-enabled servers using Windows Admin Center in Azure](https://learn.microsoft.com/en-us/windows-server/manage/windows-admin-center/azure/manage-arc-hybrid-machines)
- [SSH access to Azure Arc-enabled servers](https://learn.microsoft.com/en-us/azure/azure-arc/servers/ssh-arc-overview)
- [CLI reference for azcmagent config](https://learn.microsoft.com/en-us/azure/azure-arc/servers/azcmagent-config)

### SQL-USAGE-24H — Fonte oficial

Um envio de uso do SQL com mais de 24 horas é reportado como desatualizado.

- **Evidência:** "If usage uploads aren't received for more than 24 hours, check the following things"; "Periodically verify that usage reporting is functioning correctly by reviewing the Last Usage Upload Time in the Azure portal."
- [Manage Licensing and Billing - SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/manage-license-billing?view=sql-server-ver17)

### SQL-PAYG-30D — Fonte oficial

Uma máquina SQL Server com pay-as-you-go precisa se comunicar com o Azure ao menos a cada 30 dias; acima de 30 dias desconectada, a cobrança passa a ser recorrente com base na última configuração conhecida.

- **Evidência:** "Azure Arc-connected servers must check in with Azure at least once every 30 days." / "If the machine remains disconnected for more than 30 days, the SQL Arc service switches to recurring billing based on the last known configuration." Charges include backfill for the previous 30 days; a changed VM ID can cause double billing.
- [Manage the transition to pay-as-you-go billing - SQL Server enabled by Azure Arc](https://learn.microsoft.com/en-us/sql/sql-server/azure-arc/manage-pay-as-you-go-transition?view=sql-server-ver17#solution-overview)

### ACTIVITYLOG-90D — Fonte oficial

O Activity Log guarda 90 dias de forma nativa.

- **Evidência:** "Azure retains activity log events for 90 days and then deletes them." Longer retention needs a diagnostic setting that sends the entries elsewhere.
- [Activity log in Azure Monitor - Retention period](https://learn.microsoft.com/en-us/azure/azure-monitor/fundamentals/activity-log#retention-period)

### LA-RETENTION-90D — Critério do kit

Um workspace do Log Analytics que recebe dados do Arc e retém menos de 90 dias é um alerta.

- **Justificativa:** Microsoft does not set a minimum retention for security investigations; 90 days matches the native Activity Log window and is the kit's default for detection and audit.

### DEFENDER-OPEN-90D — Critério do kit

Recomendações do Defender abertas há 90 dias ou mais são contadas à parte no detalhe (informativo).

- **Justificativa:** A reading aid for stale recommendations; it does not change the result.

### DEFENDER-HIGH-FAIL — Critério do kit

Uma recomendação do Defender de severidade High que afeta uma máquina Arc é uma lacuna verificada (FAIL); só severidades menores são oportunidade de melhoria (WARN).

- **Justificativa:** The recommendation exists and is unhealthy in Defender for Cloud, so the condition is observed. The mapping from High severity to FAIL is the kit's.

### PRICES-GC — Fonte oficial

Azure Policy guest configuration (machine configuration) e Change Tracking & Inventory custam USD 6 por servidor por mês (preço de lista).

- **Evidência:** "Azure Policy Guest Configuration and Change Tracking & Inventory | $6/server/month | $0.009/server/hour". Prices change; the report states it is an estimate, not an invoice.
- [Azure Arc pricing - core control plane](https://azure.microsoft.com/en-us/pricing/details/azure-arc/core-control-plane/)

### PRICES-LIST — A verificar

Preços de tabela em USD usados na estimativa mensal (Defender for Servers P1/P2, Update Manager, Machine Configuration, Windows Server pay-as-you-go).

- **Pendência:** Only the guest configuration price (USD 6) is published on the Azure Arc pricing page checked on 2026-11-06 (see PRICES-GC); the page shows placeholders for Defender for Servers and Update Manager and does not list the Windows Server pay-as-you-go rate. Re-check these values on the Defender for Cloud, Update Manager and Windows Server pay-as-you-go pricing pages; the report states it is an estimate, not an invoice.
- [Azure Arc pricing](https://azure.microsoft.com/pricing/details/azure-arc/)
- **Rever até:** 2026-12-06

### KIT-INDEX — Critério do kit

O índice do kit não é o Secure Score do Defender for Cloud. A Microsoft dá a cada controle uma pontuação máxima fixa e a divide entre os recursos saudáveis e não saudáveis; o kit pondera os controles por severidade (Alta 3, Média 2, Baixa 1) e os pontua pela proporção de máquinas saudáveis.

- **Evidência:** Learn: "Max score ... is fixed for every environment"; "Score per resource = max score / (healthy + unhealthy resources)".
- **Justificativa:** A reading aid to rank work inside this report. The official measure is the Secure Score of Defender for Cloud.
- [Cloud Secure Score in Microsoft Defender for Cloud](https://learn.microsoft.com/en-us/azure/defender-for-cloud/secure-score-security-controls)

### PRIORITY-SCALE — Critério do kit

As pontuações de risco residual se traduzem em prioridades P0 (80 ou mais), P1 (60), P2 (35) e P3. Prioriza trabalho de postura; não é severidade de incidente.

- **Justificativa:** Deterministic model defined by this project (checkpoint 3 and 4); documented in docs/v4/methodology-v4.md.

### SCENARIOS-AS — Critério do kit

Os 11 cenários de segurança (AS01-AS11) e seus caminhos de ataque são hipóteses escritas pelo autor; um ataque nunca é afirmado como confirmado.

- **Justificativa:** Scenarios link controls to a reading of risk. They carry attackConfirmation=NOT_ASSERTED.

### MCSB-ZT-MAPPING — Critério do kit

O mapeamento de cada verificação para controles do Microsoft Cloud Security Benchmark, princípios e pilares do Zero Trust e tiers é a leitura do autor, com um nível de confiança por verificação.

- **Justificativa:** Reading aid; not a compliance mapping. See mappingConfidence in assurance/v4/checkpoint3/data/checks.enriched.json.
