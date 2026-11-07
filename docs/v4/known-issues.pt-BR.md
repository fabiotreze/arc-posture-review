# Problemas conhecidos — v4.2.0

[English](known-issues.md) · **Português**

> **Registro histórico.** Situação na v4.2.0, mantida como histórico dos problemas conhecidos; cada entrada indica a versão que a corrigiu ou que a acompanha. Desde a v4.2.3, o `requirements-v4.txt` foi incorporado ao `requirements-dev.txt` e os workflows citados em entradas mais antigas foram reduzidos (veja `docs/v4.2.3-cleanup.md`). As versões posteriores estão descritas no `CHANGELOG.md`.

## KI-V4-001 — alertas do Dependabot no pypdf

- **Status:** RESOLVED — corrigido com a atualização da versão fixada aprovada
- **Dependências aprovadas anteriores:** `pypdf==6.19.0` e depois `pypdf==6.21.2`
- **Dependência aprovada atual:** `pypdf==6.21.4`
- **Fila de segurança observada antes da primeira correção:** 11 alertas do Dependabot por arquivo de requisitos (`requirements-v4.txt` e `requirements-dev.txt`)
- **Fila de segurança observada antes da v4.1.1:** 14 alertas do Dependabot (7 avisos de segurança x 2 arquivos de requisitos) contra `pypdf==6.21.2`; a `6.21.4` é a primeira versão corrigida para todos eles.
- **Correção:** os dois arquivos de requisitos trazem a nova versão fixada e os gates CP8/CP9/CP10 validam o estado resolvido. O `pypdf` só lê PDFs gerados por este projeto (`tools/Generate-CleanPdf.py` e o teste visual do relatório); ele nunca processa PDFs fornecidos por usuários.
- **Efeito:** o bloqueio de dependência está encerrado. A revisão de segurança da v4.0.0 foi repetida e aprovada em 2026-10-29 e a v4.0.0 está publicada.

Nenhum workflow nem script de integração deste pacote contorna os gates de release nem suprime alertas.

## Notas da revisão da v4.0.3

Veja `docs/v4/security-review-addendum-v4.0.3.md`: correção da declaração do SHA256SUMS, artefato de cobertura presente apenas nas fixtures, hardening da disponibilidade de evidências (F1) e itens adiados para a v4.1.0 (F2, F3, F4, F5, F6).

## Notas da revisão da v4.0.4

CHK-32 e CHK-39 retornavam PASS contra um alvo vazio de máquinas conectadas quando o inventário do Arc tinha máquinas, mas nenhuma estava Connected (v4.0.3 e anteriores). Corrigido na v4.0.4: ambos retornam N/A; veja `docs/v4/security-review-record-v4.0.4.md`.

## Notas da revisão da v4.0.5

Até a v4.0.4, os marcadores do guia incorporados aos arquivos HTML não acompanhavam a versão do coletor (o EN-US mostrava a v4.0.1 e o PT-BR, a v3.9.5), porque nenhum gate os comparava. Corrigido na v4.0.5 com `tools/Test-GuideVersion.py`; veja `docs/v4/security-review-record-v4.0.5.md`.

## Notas da revisão da v4.1.1

Postura versus evidência: uma configuração ausente ou uma evidência ausente era reportada como FAIL conclusivo em vários checks, e uma execução sem `-Subscriptions` consultava silenciosamente apenas a subscription padrão da CLI enquanto reportava cobertura completa. Corrigido na v4.1.1; veja `docs/v4.1.1-posture-vs-evidence.pt-BR.md` e `docs/v4/security-review-record-v4.1.1.md`.

Ainda em aberto (documentado, não são regressões): F3 (o motor não condiciona FAIL/WARN à presença dos campos obrigatórios; o modelo aprovado permite um FAIL conclusivo com cobertura PARTIAL e as fixtures não têm membros `data/*.json`), a correlação por máquina via `resourceGroup/name` sem a subscription (o coletor agora avisa quando o mesmo par existe em mais de uma subscription) e o CHK-37 misturando a amostra de máquinas com as contagens de status de todo o ambiente quando `-MaxMachines` é usado.

## Notas da revisão da v4.1.4 e da v4.1.5

Primeira execução de ponta a ponta no Cloud Shell: os action cards de lacunas verificadas usavam redação de resposta a incidentes (corrigido na v4.1.4: *Remediate*), o relatório v4 em PT-BR mostrava frases do motor e do coletor em inglês (corrigido na v4.1.4, apenas de exibição) e uma regra em português reescrevia texto que já estava em português ("controle(s)" virou "contpapel(is)"; corrigido na v4.1.5 e protegido por `tools/Test-PtBrContent.py`). Veja `docs/v4.1.4-wording-and-pt-br.md`.

Ainda em aberto (documentado, não são regressões): cenários com pontuação de risco residual alta são P0 (NOW) mesmo em ambientes pequenos (a escala de prioridade prioriza o trabalho de postura, não é uma severidade de incidente); frases do coletor que não apareceram em uma execução real podem permanecer em inglês no relatório PT-BR (adicione uma regra à tabela do app e regenere `criteria/v4/pt-br-detail-rules.json`); o ramo do CHK-55 para uma atribuição ausente é inalcançável porque um resultado vazio conta como uma linha.

## Notas da revisão da v4.2.0

Uma revisão dos fundamentos das afirmações encontrou dois rótulos do coletor sem respaldo (nomes de portas do CHK-21) e faixas de CVE que divergiam do NVD (CHK-29); ambos estão corrigidos e o restante é acompanhado no registro (docs/sources.pt-BR.md), onde toda afirmação agora está classificada (fonte oficial, CVE ou critério do kit). Ainda em aberto: os textos do guia e do catálogo e o relatório ainda não mostram o estado de cada afirmação; o bloqueio local do upgrade automático só é visível na própria máquina; o CHK-37 mistura a amostra com o ambiente sob -MaxMachines.
