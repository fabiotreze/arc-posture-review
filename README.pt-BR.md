# Arc Posture Review

[![Release](https://img.shields.io/github/v/release/fabiotreze/arc-posture-review)](https://github.com/fabiotreze/arc-posture-review/releases)
[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-EF9421.svg)](LICENSE-DOCS)

[English](README.md) · **Português**

Kit somente leitura para avaliar a segurança de **servidores habilitados pelo Azure Arc** e do **SQL Server habilitado pelo Azure Arc**. Um único HTML offline guia a avaliação, gera um coletor PowerShell somente leitura e analisa o pacote de evidências localmente no navegador.

> Projeto pessoal e independente. Não é uma ferramenta oficial da Microsoft. Construído a partir de anos de experiência em entregas de campo e da documentação pública da Microsoft, consolidado com apoio de agentes de IA e revisado pelo autor. Valide as recomendações na documentação oficial; o uso é de responsabilidade de quem executa. Veja [DISCLAIMER.md](DISCLAIMER.md).

## Para que serve

**Foco: a postura de segurança dos servidores habilitados pelo Azure Arc** (e do SQL Server habilitado pelo Azure Arc). Responde a uma pergunta: *este ambiente Arc está configurado, protegido e operado com segurança, e o que corrigir primeiro?*

As decisões de segurança começam antes do primeiro servidor conectado (credenciais de onboarding, caminho de rede) e terminam depois que ele é removido (recursos órfãos, identidades esquecidas). Por isso o guia cobre o ciclo de vida inteiro do servidor: planejar, conectar, proteger, operar, desativar.

| Você quer | Use | Resultado |
|---|---|---|
| **Avaliar um ambiente Arc existente** (uso principal) | Etapas 2–5: gerar o script somente leitura, rodar no Cloud Shell, carregar o `.zip` | Achados por verificação, plano de ação priorizado, relatório |
| **Planejar ou revisar um onboarding** | Guia → *Comece aqui* → árvores D1–D3, D2 e D9; itens documentais como checklist de desenho | Decisões registradas antes do rollout |
| **Preparar uma conversa ou workshop de segurança** | Guia, árvores de decisão e relatório de exemplo | Vocabulário comum e pauta estruturada |
| **Acompanhar a evolução** | Rodar a coleta de novo e comparar os `.json` exportados | Evidência de antes e depois |

**Por que tantas referências e diagramas?** Cada verificação aponta para a fonte pública da Microsoft que a sustenta (controle do Microsoft Cloud Security Benchmark, Cloud Adoption Framework, documentação do produto), e cada decisão tem uma árvore que explica o *porquê*. Os achados podem ser rastreados e defendidos, em vez de serem opinião.

**O que não é:** não instala, não conecta e não altera nada (somente leitura); não substitui o Defender for Cloud, o Secure Score ou o Azure Policy (ele os lê); e não é orientação oficial da Microsoft.

## O que entrega

- **Método público da Microsoft:** ciclo de sustentação de postura do [Cloud Adoption Framework — Secure](https://learn.microsoft.com/azure/cloud-adoption-framework/secure/overview), medido pelo [Microsoft Cloud Security Benchmark](https://learn.microsoft.com/security/benchmark/azure/introduction) (MCSB v2, com mapeamento para CIS Controls v8.1, NIST SP 800-53, PCI-DSS v4, NIST CSF 2.0 e ISO 27001).
- **63 verificações** (44 automáticas, 19 documentais), cada uma com camada, controle MCSB e árvore de decisão.
- **9 árvores de decisão** (onboarding, organização, conectividade, identidade, extensões, proteção, versões e legado, remoção, custo) e execução do programa.
- **Coletor somente leitura** (`Invoke-ArcPostureReview.ps1`): apenas leitura via Azure Resource Graph e Azure CLI, paginado, várias subscriptions ou management group, com verificação prévia de permissões (Reader basta).
- **Análise local:** leitura rápida, índice do kit no modelo do Secure Score (pontos por severidade, proporção de máquinas saudáveis, mesma causa contada uma vez), conformidade por camada e por controle MCSB, Secure Score do Defender for Cloud, plano de ação em uma linha por ação com ganho, prazo e responsável, 9 alertas recomendados, versões do agente e das extensões na data da execução, estimativa de custo e evidências por achado.
- **Inventário de cobertura:** o guia (Anexo J) mostra os totais por domínio, severidade, camada e árvore de decisão, e o que mudou desde a versão anterior.
- **Piso de segurança do agente:** máquinas abaixo da versão **1.61** do Connected Machine agent falham na verificação de versão (CVEs públicas de elevação de privilégio local: CVE-2025-49692, CVE-2025-26627, CVE-2025-55316, CVE-2026-26117), e o catálogo de serviços cobre as tarefas agendadas do agente e os serviços das extensões.
- **Validação do pacote:** origem, estrutura, SHA-256 do manifest e limites de tamanho; pacote alterado é rejeitado. O script imprime o SHA-256 do `.zip` para confirmar a origem.
- **Arquivos gerados**, em **português** e **inglês** (o idioma faz parte do nome do arquivo):

  | Arquivo | O que contém | Para que usar |
  |---|---|---|
  | `arc-posture-review-<data>.zip` | Dados coletados, resultados e itens de cada verificação (gerado pelo script) | Evidência; carregar na etapa 3 |
  | `arc-posture-review-analysis-<data>.<idioma>.html` | **Um único arquivo:** a análise completa mais o registro do checklist (status, evidência da coleta e notas de cada verificação, notas da sessão) | A entrega: compartilhar, arquivar ou imprimir em PDF |
  | `arc-posture-review-report.<idioma>.md` / `.json` | O mesmo conteúdo em texto e em dados | Editar o texto ou comparar execuções |
- **Interface acessível:** status por ícone, texto e cor (paleta do Advisor/Defender), contraste AA, modo escuro, alto contraste e movimento reduzido.

## Veja antes de rodar

![Comece aqui: etapas e árvores de decisão](docs/images/start-here.pt-BR.png)

![Fluxo da coleta somente leitura e das evidências](docs/images/collection-flow.pt-BR.png)

**Relatório de exemplo** de uma subscription de laboratório (7 servidores Arc, SQL Server, Defender for Servers), anonimizado: subscription, conta, IDs e nomes de recursos de governança substituídos.
[Abrir o relatório de exemplo](https://fabiotreze.github.io/arc-posture-review/docs/examples/sample-analysis.pt-BR.html) · [English](https://fabiotreze.github.io/arc-posture-review/docs/examples/sample-analysis.en-US.html)

![Análise de exemplo](docs/images/sample-report.pt-BR.png)

## Como usar

| Opção | Como |
|---|---|
| Online | https://fabiotreze.github.io/arc-posture-review/arc-posture-review.pt-BR.html |
| Offline | Baixe [`arc-posture-review.pt-BR.html`](arc-posture-review.pt-BR.html) (ou [`.en-US.html`](arc-posture-review.en-US.html)) e abra no Edge ou Chrome |
| Só o script | [`scripts/Invoke-ArcPostureReview.ps1`](scripts/Invoke-ArcPostureReview.ps1): as 63 verificações, subscription atual por padrão |
| Ler o guia | [docs/guide.pt-BR.md](docs/guide.pt-BR.md) · [docs/guide.en-US.md](docs/guide.en-US.md) |

1. Abra o HTML e siga o **Comece aqui**: escolha as decisões nas árvores visuais e depois o escopo e as verificações.
2. Baixe o script e execute no **Azure Cloud Shell (PowerShell)**: `./Invoke-ArcPostureReview.ps1` (ou `-Subscriptions <id1>,<id2>` / `-ManagementGroup <nome>`).
3. Carregue o `.zip` gerado e compare o SHA-256 exibido com o impresso pelo script.
4. Revise a análise, aplique os status e exporte o relatório.

**Permissões:** Reader no management group ou nas subscriptions. **Privacidade:** os campos ficam só no navegador da sua máquina; pacote e relatórios têm dados do ambiente e são confidenciais.

## Repositório

```
index.html                           versão em inglês (GitHub Pages)
arc-posture-review.en-US.html        HTML offline, inglês
arc-posture-review.pt-BR.html        HTML offline, português
scripts/Invoke-ArcPostureReview.ps1  coletor somente leitura avulso (revise antes de executar)
docs/guide.en-US.md · guide.pt-BR.md playbook com árvores de decisão (o GitHub renderiza o Mermaid)
docs/examples/                       relatórios de exemplo anonimizados (en-US, pt-BR)
docs/images/                         imagens usadas no README
```

## Contribuições

Dúvidas, correções e sugestões são bem-vindas por [issues](../../issues), citando a documentação oficial da Microsoft. Nunca inclua dados de clientes ou do seu ambiente. Questões de segurança: veja [SECURITY.md](SECURITY.md).

## Licença

- **Código** (o script PowerShell e o JavaScript, CSS e PowerShell dentro dos HTML): [MIT](LICENSE).
- **Documentação e texto do playbook** (docs/, README, DISCLAIMER e o texto dos HTML): [CC BY 4.0](LICENSE-DOCS). Crédito sugerido: *"Arc Posture Review" por Fabio Rodrigues Vieira Costa, https://github.com/fabiotreze/arc-posture-review*.
- Conteúdo de terceiros referenciado ou citado brevemente (Microsoft Learn, pesquisas públicas de segurança) e marcas (Microsoft, Azure, Azure Arc) não são relicenciados e continuam com seus donos.
