# Modelo de ameaças do Arc Posture Review v4

[English](threat-model-v4.md) · **Português**

## Escopo

Este modelo cobre o pacote do coletor somente leitura, o ZIP de evidências, o Motor de Avaliação determinístico, o `assessment-result.v4.json` canônico, os relatórios estáticos, os gates do repositório e os workflows de CI.

## Objetivos de segurança

- Preservar a integridade e a rastreabilidade das evidências.
- Impedir que evidência ausente ou malformada se torne um resultado positivo.
- Impedir que a camada de relatório calcule ou exagere conclusões de segurança.
- Manter credenciais, identificadores de tenant e evidências brutas fora de fixtures versionadas e de logs.
- Tornar a prontidão da release reproduzível e revisável.

## Ativos

| Ativo | Propriedade de segurança |
|---|---|
| Coletor e critérios | Integridade, privilégio mínimo |
| Pacote de evidências | Confidencialidade, integridade, proveniência |
| Avaliação canônica | Integridade, reprodutibilidade determinística |
| Rastreabilidade dos 64 CHK | Completude, não repúdio da derivação |
| Modelo de Cenário de Segurança | Fronteiras corretas, sem exagero de ataque |
| Relatórios HTML/PDF | Renderização fiel, segurança offline |
| Workflows e metadados da release | Integridade da cadeia de suprimentos, permissões somente leitura |

## Fronteiras de confiança

1. Estação de trabalho do operador → plano de controle do Azure.
2. Saída do coletor → entrada do Motor de Avaliação.
3. Motor de Avaliação → contrato canônico.
4. Contrato canônico → renderizador HTML/PDF.
5. Repositório → runner hospedado no GitHub e feed de pacotes aprovado.

## Ameaças e controles

| Ameaça | Exemplo | Controle exigido |
|---|---|---|
| Adulteração de evidências | Conteúdo do ZIP alterado após a coleta | Digest do pacote/da entrada e estado de integridade |
| Confusão de schema | Campos ou cardinalidade inesperados | Schemas Draft 2020-12 e validadores semânticos |
| Otimismo com evidência ausente | Dado ausente interpretado como saudável | Evidência ausente nunca é PASS; afirmação não resolvida |
| Falso positivo | Sinal indireto tratado como prova direta | Critérios de afirmação, cobertura da evidência, testes de guarda e checklist do revisor |
| Exagero de ataque | Fraqueza de postura apresentada como comprometimento | `attackConfirmation=NOT_ASSERTED` e guardrail de cenário |
| Deriva do renderizador | O HTML recalcula o score ou a prioridade | Gate de pureza de renderização e paridade com o canônico embutido |
| Injeção de script | Evidência renderizada como conteúdo executável | Escape de HTML, CSP restritiva, sem parsing do contrato em JavaScript no navegador |
| Divulgação de segredos | Dados do tenant em fixture ou artefato de CI | Fixture sanitizada e revisão de conteúdo |
| Expansão de privilégios do workflow | Token de escrita usado pelo gate de qualidade | `permissions: contents: read` e validador de workflow |
| Exposição de dependência | Versão vulnerável do parser de PDF | Versão aprovada fixada, acompanhamento pelo Dependabot e bloqueio de release estável |
| Substituição de código em tempo de execução (v4.1.2) | O coletor baixa o kit de relatório e um kit adulterado é executado | O kit é construído de forma determinística (`tools/Build-Kit.py`), seu SHA-256 é fixado dentro do coletor e recusado em caso de divergência, o workflow de release o reconstrói e falha em caso de deriva, e o kit é Python somente com a biblioteca padrão, que não faz chamadas de rede nem de processo e grava apenas os arquivos de saída que recebe |

## Casos de abuso

- Um contribuidor altera o kit sem atualizar o SHA-256 fixado: rejeitado por `tools/Build-Kit.py --check` (gate do checkpoint 4 e workflow de release).
- Um kit servido de outro local ou alterado em trânsito: recusado pelo coletor (`tools/Test-V4ReportStep.py` cobre a divergência).
- Um contribuidor altera o JavaScript para derivar um score menor: rejeitado pelos gates de pureza de renderização e de contrato do relatório.
- Um cenário pula MANAGEMENT: rejeitado pelos testes de transição de cenário.
- Um check desaparece da evidência: rejeitado pelos gates de cardinalidade exata de 64 CHK.
- Um pull request adiciona um comando mutante a um workflow v4: rejeitado pela política de workflow do CP8.
- Uma release estável é preparada enquanto os alertas do pypdf permanecem: rejeitada pelos gates de bloqueio CP9/CP10.

## Riscos residuais

- A revisão se limita ao escopo coletado e à evidência de um ponto no tempo.
- A coleta somente leitura não consegue validar todas as condições locais do host nem as de resposta a incidentes.
- O atraso do feed aprovado pode impedir a correção imediata de dependências.
- Um relatório de postura correto não substitui a investigação de incidentes, os testes de intrusão nem a aprovação de mudanças.
