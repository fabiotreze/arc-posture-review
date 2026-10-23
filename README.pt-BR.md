# Arc Posture Review

[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Docs: CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-EF9421.svg)](LICENSE-DOCS)

[English](README.md) · **Português**

Kit somente leitura para avaliar a segurança de **servidores habilitados pelo Azure Arc** e do **SQL Server habilitado pelo Azure Arc**. Um único HTML offline guia a avaliação, gera um coletor PowerShell somente leitura e analisa o pacote de evidências localmente no navegador.

> Projeto pessoal e independente. Não é uma ferramenta oficial da Microsoft. Construído a partir de anos de experiência em entregas de campo e da documentação pública da Microsoft, consolidado com apoio de agentes de IA e revisado pelo autor. Valide as recomendações na documentação oficial; o uso é de responsabilidade de quem executa. Veja [DISCLAIMER.md](DISCLAIMER.md).

## O que entrega

- **Método público da Microsoft:** ciclo de sustentação de postura do [Cloud Adoption Framework — Secure](https://learn.microsoft.com/azure/cloud-adoption-framework/secure/overview), medido pelo [Microsoft Cloud Security Benchmark](https://learn.microsoft.com/security/benchmark/azure/introduction) (MCSB v1, com mapeamento para CIS Controls v8, NIST SP 800-53 e PCI-DSS).
- **54 verificações** (38 automáticas, 16 documentais), cada uma com camada, controle MCSB e árvore de decisão.
- **9 árvores de decisão** (onboarding, organização, conectividade, identidade, extensões, proteção, versões e legado, remoção, custo) e execução do programa.
- **Coletor somente leitura** (`Invoke-ArcPostureReview.ps1`): apenas leitura via Azure Resource Graph e Azure CLI, paginado, várias subscriptions ou management group, com verificação prévia de permissões (Reader basta).
- **Análise local:** conformidade por camada e por controle MCSB, Secure Score do Defender for Cloud, plano de ação com prazo e responsável, 9 alertas recomendados, versões do agente e das extensões na data da execução, estimativa de custo e evidências por achado.
- **Piso de segurança do agente:** máquinas abaixo da versão **1.61** do Connected Machine agent falham na verificação de versão (CVEs públicas de elevação de privilégio local: CVE-2025-49692, CVE-2025-26627, CVE-2025-55316, CVE-2026-26117), e o catálogo de serviços cobre as tarefas agendadas do agente e os serviços das extensões.
- **Validação do pacote:** origem, estrutura, SHA-256 do manifest e limites de tamanho; pacote alterado é rejeitado. O script imprime o SHA-256 do `.zip` para confirmar a origem.
- **Relatórios** em HTML, Markdown e JSON, em **português** e **inglês**.
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
| Só o script | [`scripts/Invoke-ArcPostureReview.ps1`](scripts/Invoke-ArcPostureReview.ps1): as 54 verificações, subscription atual por padrão |
| Ler o guia | [docs/guide.pt-BR.md](docs/guide.pt-BR.md) · [docs/guide.en-US.md](docs/guide.en-US.md) |

1. Abra o HTML e siga o **Comece aqui**: escolha as decisões nas árvores visuais e depois o escopo e as verificações.
2. Baixe o script e execute no **Azure Cloud Shell (PowerShell)**: `./Invoke-ArcPostureReview.ps1` (ou `-Subscriptions <id1>,<id2>` / `-ManagementGroup <nome>`).
3. Carregue o `.zip` gerado e compare o SHA-256 exibido com o impresso pelo script.
4. Revise a análise, aplique os status e exporte o relatório.

**Permissões:** Reader no management group ou nas subscriptions. **Privacidade:** os campos ficam só no navegador da sua máquina; pacote e relatórios têm dados do ambiente e são confidenciais.

Dúvidas e correções por [issues](../../issues), citando a documentação oficial e sem dados do seu ambiente.

Licenças: código [MIT](LICENSE); documentação [CC BY 4.0](LICENSE-DOCS).

## Licença

- **Código** (o script PowerShell e o JavaScript, CSS e PowerShell dentro dos HTML): [MIT](LICENSE).
- **Documentação e texto do playbook** (docs/, README, DISCLAIMER e o texto dos HTML): [CC BY 4.0](LICENSE-DOCS). Crédito sugerido: *"Arc Posture Review" por Fabio Rodrigues Vieira Costa, https://github.com/fabiotreze/arc-posture-review*.
- Conteúdo de terceiros referenciado ou citado brevemente (Microsoft Learn, pesquisas públicas de segurança) e marcas (Microsoft, Azure, Azure Arc) não são relicenciados e continuam com seus donos.
