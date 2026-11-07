# Metodologia do Arc Posture Review v4

[English](methodology-v4.md) · **Português**

**Release:** v4.0.1 (metodologia inalterada desde a v4.0.0-rc.1)\
**Resultado canônico:** `assessment-result.v4.json`  
**Camada de evidência:** exatamente de `CHK-01` a `CHK-64`

## Finalidade e limite de garantia

O Arc Posture Review v4 avalia a evidência do coletor somente leitura com um Motor de Avaliação determinístico. O motor, e não o relatório HTML, decide os vereditos das afirmações, os resultados dos controles, o risco residual, a prioridade, o estado do Cenário de Segurança, a Cobertura de Defesa, os action cards, o posicionamento no roadmap e os deltas de comparação. O relatório é uma projeção do contrato canônico e não deve inferir comprometimento, exploração ou causalidade.

## Pipeline

1. O coletor preservado produz evidência no schema v3.
2. A integridade da entrada e os campos obrigatórios são validados.
3. A evidência é normalizada em 64 registros de evidência.
4. A rastreabilidade Evidência → Observação → Afirmação → Controle é avaliada.
5. O motor avalia os mapeamentos de Zero Trust, o escopo de Tier, os Cenários de Segurança e a cobertura Prevent/Detect/Respond/Recover.
6. O motor emite `assessment-result.v4.json` com um digest estável.
7. O CP6 renderiza o HTML EN-US/PT-BR; o CP7 renderiza dados canônicos de antes/depois.

## Semântica de controles e evidências

Todo CHK aparece exatamente uma vez em `traceability.evidence`, `traceability.observations`, `traceability.claims` e `controlAssessments`. A evidência ausente nunca produz um resultado efetivo. A cobertura da evidência e o resultado do controle são independentes: a cobertura parcial pode coexistir com um resultado conclusivo quando a evidência disponível é suficiente, enquanto a evidência obrigatória ausente permanece não resolvida.

## Cenários de Segurança

Os cenários mantêm o modelo de segurança ordenado `IDENTITY → MANAGEMENT → HOST → DEFENSE`. A maturidade da evidência é representada como `HYPOTHESIS`, `POTENTIAL_RELEVANCE`, `PROVIDER_IDENTIFIED` ou `VALIDATED`. Esses são estados de validação de postura; nenhum deles confirma um ataque. `attackConfirmation` permanece `NOT_ASSERTED`, a menos que uma futura fonte de incidentes, governada separadamente, altere o contrato.

## Cobertura de Defesa

Para cada cenário, o motor emite o status de Prevent, Detect, Respond e Recover, além dos IDs de CHK de suporte. O relatório exibe esses valores como fornecidos. Uma lacuna é um achado de postura, não prova de que um agente de ameaça usou o caminho.

## Risco, prioridade e roadmap

Os scores de risco residual, os níveis, as prioridades e o posicionamento em NOW/30d/90d são saídas determinísticas do motor. A camada de renderização não pode recalculá-los, reordená-los nem sobrescrevê-los. Os action cards incluem responsáveis, ações, evidência de encerramento e texto de rollback como dados canônicos.

## Antes/depois e Melhoria Verificada

Quando nenhum baseline é fornecido, `comparison` é `null` e o relatório declara explicitamente que nenhuma tendência é afirmada. Com um baseline, o motor emite deltas de controle e de cenário. O CP7 rotula como **Melhoria Verificada** apenas as linhas canônicas `IMPROVED`; ele não deriva melhoria a partir dos scores exibidos.

## Reprodutibilidade e gates de qualidade

A mesma evidência, o mesmo modelo e o mesmo motor produzem uma saída canônica estável byte a byte. Os gates do repositório cobrem contratos JSON, determinismo, guardas de falso positivo, paridade bilíngue, verificações responsivas com Playwright e saída de PDF limpa. Os workflows de DevSecOps têm permissões somente leitura no repositório e não publicam releases.

## Restrição conhecida da release

O KI-V4-001 está resolvido: a dependência aprovada passou de `pypdf==6.19.0` para `pypdf==6.21.2`, o que encerra os onze alertas do Dependabot por arquivo de requisitos. A revisão de segurança da v4.0.0 foi repetida e aprovada em 2026-10-29 e a v4.0.0 está publicada. Veja [Problemas conhecidos](known-issues.pt-BR.md).
