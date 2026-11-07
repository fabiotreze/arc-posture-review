# Arc Posture Review v4 — matriz de consultas e evidências

[English](query-evidence-matrix.md) · **Português**

Esta matriz é o baseline de revisão do coletor somente leitura. O pacote de evidências gerado é a fonte autoritativa de uma execução: `data/query-evidence.json` preserva a consulta ou o comando da CLI normalizado, seu SHA-256, a fonte oficial, as contagens de linhas/páginas, as tentativas de escopo, as falhas e o carimbo de data/hora da coleta; `manifest.json` protege cada dataset salvo com SHA-256.

## Contrato global de execução

- As consultas do Azure Resource Graph são paginadas com `--first 1000` e o skip token retornado. Um token ainda presente no limite de segurança de 500 páginas rejeita o dataset como incompleto; ele nunca é pontuado como resultado vazio.
- Os comandos por subscription registram os escopos tentados, bem-sucedidos e com falha. Se todos os escopos falharem, o dataset é `null` e os checks dependentes viram `ERROR`. Falhas parciais de escopo reduzem a cobertura da evidência por meio dos ledgers de permissões e de coleta.
- Dados vazios são interpretados pelo check, não de forma global. Uma ausência válida só pode ser `PASS` quando um alvo explícito diferente de zero foi avaliado. Nenhum alvo aplicável resulta em `N/A`; um `PASS` explícito com zero alvo é rejeitado novamente pelo Motor de Avaliação v4.
- IDs de recurso, subscriptions, resource groups e nomes de máquina são normalizados apenas para correspondência. As linhas originais da evidência permanecem em `data/*.json`.
- O coletor é somente leitura. Sua allowlist de comandos admite apenas o Azure Resource Graph, operações de leitura/listagem da CLI e quatro padrões delimitados de GET do ARM.

Fundamentos oficiais: [Visão geral do Resource Graph](https://learn.microsoft.com/azure/governance/resource-graph/overview), [orientações de paginação](https://learn.microsoft.com/azure/governance/resource-graph/concepts/paging-results), [consultas de exemplo do Azure Arc](https://learn.microsoft.com/azure/azure-arc/servers/resource-graph-samples), [consultas de exemplo do Azure Policy](https://learn.microsoft.com/azure/governance/policy/samples/resource-graph-samples) e [consultas de exemplo do Defender for Cloud](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples).

## Validação dataset a dataset

| Dataset | Fonte e finalidade | Escopo/chave de junção | Significado de zero linhas | Referência oficial |
|---|---|---|---|---|
| `subs` | `resourcecontainers`; resolve a população de subscriptions acessíveis | `subscriptionId` | Fatal: nenhum escopo acessível | [Linguagem de consulta do Resource Graph](https://learn.microsoft.com/azure/governance/resource-graph/concepts/query-language) |
| `permissions` | GET do ARM `Microsoft.Authorization/permissions` por subscription | `subscriptionId` | `UNKNOWN`; não se pode presumir que a evidência dependente esteja completa | [Permissions](https://learn.microsoft.com/rest/api/authorization/permissions) (as operações documentadas são por resource group e por recurso; o GET no escopo da subscription não está listado ali, a verificar) |
| `machines` | `resources` / `microsoft.hybridcompute/machines`; inventário Arc canônico e configuração | `subscriptionId/resourceGroup/name` em minúsculas | Sem alvo Arc; os controles de máquina são `N/A`, não `PASS` | [Exemplos de Resource Graph para o Arc](https://learn.microsoft.com/azure/azure-arc/servers/resource-graph-samples) |
| `extensions` | `resources` / extensões de máquinas Arc; estado, tipo, publisher, versão, auto-upgrade | `resourceGroup/machine` | Os checks específicos de extensão são `N/A`; os checks de hardening da máquina mantêm o alvo da máquina | [Referência do recurso de extensões](https://learn.microsoft.com/azure/templates/microsoft.hybridcompute/machines/extensions) |
| `gcAssign`, `gcComp` | `guestconfigurationresources`; atribuições e conformidade | `subscriptionId/resourceGroup/machine` | Cobertura desconhecida, a menos que a não aplicabilidade seja estabelecida de forma independente | [Visão geral do Machine Configuration](https://learn.microsoft.com/azure/governance/machine-configuration/overview) |
| `related` | Inventário delimitado de `resources` para PLS, gateway, DNS, resolver, DCR/DCE, Key Vault, workspace, Automation, licenças e soluções do Sentinel | ID do recurso mais o escopo de subscription/RG do Arc | Aplicabilidade por recurso; nunca uma conclusão global de ambiente saudável | [Visão geral do Resource Graph](https://learn.microsoft.com/azure/governance/resource-graph/overview) |
| `dcra` | `insightsresources`; associações de DCR anexadas a máquinas Arc | `resourceGroup/machine` → `dcrId` | Se o AMA existir, zero associação é uma lacuna; sem o AMA, a avaliação fica bloqueada | [Associações de DCR](https://learn.microsoft.com/azure/azure-monitor/data-collection/data-collection-rule-associations) |
| `roles` | `authorizationresources`; atribuições de papel com left join nas definições; os IDs built-in publicados servem como nomes de fallback | `principalId`, `scope` da atribuição normalizado, `roleId` | Zero atribuição válida somente contra um alvo de máquina/subscription diferente de zero | [Exemplos do Resource Graph por categoria](https://learn.microsoft.com/azure/governance/resource-graph/samples/samples-by-category) |
| `policyAssignments` | `policyresources`; atribuições e modo de imposição | `scope` da atribuição alcança a subscription/RG do Arc | Zero atribuição relevante é uma lacuna, não sucesso | [Exemplos de Resource Graph para o Policy](https://learn.microsoft.com/azure/governance/policy/samples/resource-graph-samples) |
| `policyStates` | `policyresources`; estados não conformes de máquinas Arc | `resourceId` normalizado | PASS somente se a consulta teve sucesso e o alvo de máquinas Arc é diferente de zero | [Obter dados de conformidade de política](https://learn.microsoft.com/azure/governance/policy/how-to/get-compliance-data) |
| `defender` | `securityresources`; avaliações não íntegras/isentas resumidas por recomendação | `properties.resourceDetails.Id` → máquina Arc | Um conjunto vazio de avaliações não íntegras é PASS somente com coleta e permissões bem-sucedidas e alvo de máquinas diferente de zero | [Exemplos de Resource Graph para o Defender](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `govAssign` | Atribuições de governança do Defender; cobertura de ownership dentro do prazo e em atraso | ID do recurso Arc atribuído | Cobertura suplementar; não apaga uma recomendação não íntegra | [Regras de governança](https://learn.microsoft.com/azure/defender-for-cloud/governance-rules) |
| `alerts` | Alertas do Defender Active/InProgress que referenciam máquinas Arc | identificadores de recurso → máquina | A ausência não é prova de saúde do endpoint; usada junto com a cobertura de plano/MDE | [Exemplos de Resource Graph para o Defender](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `vulns` | Subavaliações não íntegras do Defender com raiz em máquinas Arc | ID da máquina Arc pai | Zero achado sem cobertura de plano/MDE permanece `PARTIAL` | [Exemplos de Resource Graph para o Defender](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `secscore` | Secure Score da subscription | `subscriptionId` | Informativo; a pontuação inclui recursos que não são Arc | [Secure Score no Resource Graph](https://learn.microsoft.com/azure/defender-for-cloud/resource-graph-samples) |
| `patch` | Resultados da avaliação de patches do Arc | `resourceGroup/machine` | A ausência de avaliação atual significa desconhecido/parcial, e não zero patches pendentes | [Consultas do Azure Update Manager](https://learn.microsoft.com/azure/update-manager/query-logs) |
| `advisor` | Recomendações do Advisor que impactam o Arc | máquina impactada | Verificação cruzada informativa para os controles de status/versão | [Advisor no Resource Graph](https://learn.microsoft.com/azure/advisor/advisor-azure-resource-graph) |
| `providers` | `az provider list` por subscription | `subscriptionId/namespace` | Provider obrigatório ausente é um achado; falha de comando é falha do dataset | [CLI do Azure: provider](https://learn.microsoft.com/cli/azure/provider) |
| `pricing` | Pricing do Defender no escopo da subscription | `subscriptionId/name` | A ausência da linha `VirtualMachines` não equivale a Standard | [CLI do Azure: security pricing](https://learn.microsoft.com/cli/azure/security/pricing) |
| `pricingRes` | GET do ARM delimitado para `Microsoft.Security/pricings/VirtualMachines` por máquina Arc | `resourceGroup/machine` | Leituras com falha são mantidas por máquina e não podem virar Free/Standard por suposição | [GET de pricing do Defender](https://learn.microsoft.com/rest/api/defenderforcloud/pricings/get) |
| `refVersions` | Hybrid Compute Agent Version List e Extension Metadata List | SO globalmente; região/publisher/tipo para extensões | As tabelas de fallback devem ser divulgadas; falha da consulta em tempo real reduz a confiança na atualidade dos dados | [Agent Version - List](https://learn.microsoft.com/rest/api/hybridcompute/agent-version/list?view=rest-hybridcompute-2025-01-13) |
| `diag` | Configurações de diagnóstico do Activity Log da subscription | `subscriptionId` | Zero configuração é uma lacuna para a exportação do Activity Log | [CLI de diagnostic settings](https://learn.microsoft.com/cli/azure/monitor/diagnostic-settings/subscription) |
| `activity` | Eventos do Activity Log do Hybrid Compute no período solicitado | `subscriptionId/resourceId`, `correlationId` | Zero evento válido é uma observação, não prova de que nenhum ataque ocorreu | [CLI do Activity Log](https://learn.microsoft.com/cli/azure/monitor/activity-log) |

## Regras de cruzamento de informações

1. **Identidade da máquina ↔ RBAC:** `machines.identityPrincipalId` se junta a `roles.principalId`. Uma máquina sem `identity.principalId` é um alvo de validação com falha, não uma identidade limpa.
2. **Máquina ↔ extensão:** use `resourceGroup/machine` normalizado; a subscription continua fazendo parte da validação de escopo. A ausência de extensão é interpretada conforme o serviço medido.
3. **AMA ↔ DCRA ↔ DCR ↔ workspace:** um agente instalado, por si só, não prova o fluxo de dados. CHK-39 valida a implantação; CHK-40 valida a associação; CHK-41/45 usam os destinos da DCR e a evidência do workspace/Sentinel.
4. **Plano do Defender ↔ recomendação/alerta/vulnerabilidade:** zero achado não significa saudável sem cobertura de plano e de sensor/avaliação. O Secure Score da subscription continua contextual.
5. **Atribuição de policy ↔ estado de policy:** o alcance da atribuição e o modo de imposição são separados da conformidade avaliada. Ambos são mantidos.
6. **Amostra ↔ ambiente inteiro:** `MaxMachines` é uma amostra de descoberta priorizada por risco. Os resumos de status/versão do ambiente inteiro são calculados antes da amostragem, e o relatório rotula o denominador explicitamente.

## Evidências da release

Um pacote v4.0.2 só é aceitável quando:

- os 64 checks estão presentes exatamente uma vez;
- os 45 checks automáticos têm um contrato de alvo explícito;
- `PASS` com `applicableCount = 0` está ausente;
- toda consulta tem uma linha no ledger e todo dataset salvo é coberto pelo manifest;
- os relatórios EN-US e PT-BR embutem o JSON canônico idêntico e mostram alvo, cobertura, referência da consulta e status da fonte;
- os gates determinístico, de schema, de rastreabilidade, visual, de localização, de segurança e de release passam.
