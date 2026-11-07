# Contributing

**English** · [Português](#contribuindo)

Thanks for helping. This is a personal, independent project; corrections that cite official Microsoft documentation are the most useful.

## Before you open an issue

- **Never attach or paste collected data**: the `.zip`, `results.json`, `findings/*.csv` and the reports contain machine names, subscription and principal IDs and Activity Log callers. Describe the case with fake names, or use `tests/fixtures/reviewed-lab-sanitized.zip`.
- Security vulnerabilities in this repository: use *Report a vulnerability* in the Security tab ([SECURITY.md](SECURITY.md)), not a public issue.
- Say which version you ran (`./Invoke-ArcPostureReview.ps1` prints it, and `VERSION` holds it) and whether the problem is in the collector, the engine, the report or the app.

## Pull requests

1. Branch from `main` (it is protected: changes go through a pull request and CI).
2. Keep the posture vocabulary: *verified gap* (observed with enough evidence), *improvement opportunity* (hardening or visibility not configured; not "insecure") and *not verified* (a collection task). `tools/Test-PostureWording.py` guards it.
3. Collector changes must stay read-only. Keep the UTF-8 BOM and consistent line endings of `scripts/Invoke-ArcPostureReview.ps1` (`tools/Test-LineEndings.py`).
   Every numeric threshold, date or price in the collector needs an entry in `criteria/v4/sources.json` (official source, kit criterion or to verify); then run `python tools/Sync-Sources.py`. `tools/Test-ClaimRegister.py` fails otherwise. Open the Microsoft page in full and quote it: a search summary is not evidence.
4. Texts exist in EN-US and PT-BR. New Portuguese detail rules go in the app table (`PT_DETAIL_RULES`); then run `python tools/Sync-PtRules.py` to regenerate `criteria/v4/pt-br-detail-rules.json` (`tools/Test-PtBrContent.py` checks they match).
5. After changing the collector, criteria, CSS or the kit files run `python tools/Build-Kit.py --write-hash` and `python tools/Sync-ReportAssets.py` (it also refreshes `index.html`, which must stay byte-identical to `arc-posture-review.en-US.html`; `tools/Test-ReportContract.py` and `tools/Test-CriteriaCoverage.py` check it), then `python tools/Prepare-Release.py checksums`.
6. Run the gates before pushing (the pull request runs the same gates in `v4 PR quality`; `analyze` runs PSScriptAnalyzer):

```powershell
python -m pip install -r requirements-dev.txt
python tools/Invoke-V4FinalGates.py --profile release
```

Releases follow the process in `docs/v4/` (security review record, `release/<version>/`, tag `vX.Y.Z`).

## Licenses

Code: [MIT](LICENSE). Documentation and text: [CC BY 4.0](LICENSE-DOCS). By contributing you agree to license your contribution the same way.

---

## Contribuindo

Obrigado por ajudar. Este é um projeto pessoal e independente; as correções que citam a documentação oficial da Microsoft são as mais úteis.

### Antes de abrir uma issue

- **Nunca anexe nem cole dados coletados**: o `.zip`, `results.json`, `findings/*.csv` e os relatórios contêm nomes de máquinas, IDs de subscription e de principals e autores (`caller`) do Activity Log. Descreva o caso com nomes fictícios ou use `tests/fixtures/reviewed-lab-sanitized.zip`.
- Vulnerabilidades de segurança neste repositório: use *Report a vulnerability* na aba Security ([SECURITY.md](SECURITY.md)), não uma issue pública.
- Informe qual versão você executou (`./Invoke-ArcPostureReview.ps1` a exibe, e o arquivo `VERSION` a contém) e se o problema está no coletor, no motor, no relatório ou no app.

### Pull requests

1. Parta da `main` (ela é protegida: as mudanças passam por um pull request e pelo CI).
2. Mantenha o vocabulário de postura: *lacuna verificada* (observada com evidência suficiente), *oportunidade de melhoria* (hardening ou visibilidade não configurados; não é "inseguro") e *não verificado* (uma tarefa de coleta). O `tools/Test-PostureWording.py` o protege.
3. As mudanças no coletor devem continuar somente leitura. Mantenha o BOM UTF-8 e os finais de linha consistentes de `scripts/Invoke-ArcPostureReview.ps1` (`tools/Test-LineEndings.py`).
   Todo limiar numérico, data ou preço no coletor precisa de uma entrada em `criteria/v4/sources.json` (fonte oficial, critério do kit ou a verificar); depois execute `python tools/Sync-Sources.py`. Caso contrário, o `tools/Test-ClaimRegister.py` falha. Abra a página da Microsoft por inteiro e cite o trecho: o resumo de uma busca não é evidência.
4. Os textos existem em EN-US e PT-BR. As novas regras de detalhe em português vão na tabela do app (`PT_DETAIL_RULES`); depois execute `python tools/Sync-PtRules.py` para regenerar `criteria/v4/pt-br-detail-rules.json` (o `tools/Test-PtBrContent.py` verifica que os dois coincidem).
5. Depois de alterar o coletor, os critérios, o CSS ou os arquivos do kit, execute `python tools/Build-Kit.py --write-hash` e `python tools/Sync-ReportAssets.py` (ele também atualiza o `index.html`, que deve continuar idêntico, byte a byte, ao `arc-posture-review.en-US.html`; o `tools/Test-ReportContract.py` e o `tools/Test-CriteriaCoverage.py` verificam isso) e, em seguida, `python tools/Prepare-Release.py checksums`.
6. Execute os gates antes de enviar (o pull request executa os mesmos gates no `v4 PR quality`; o `analyze` executa o PSScriptAnalyzer):

```powershell
python -m pip install -r requirements-dev.txt
python tools/Invoke-V4FinalGates.py --profile release
```

As versões seguem o processo descrito em `docs/v4/` (registro da revisão de segurança, `release/<versão>/`, tag `vX.Y.Z`).

### Licenças

Código: [MIT](LICENSE). Documentação e texto: [CC BY 4.0](LICENSE-DOCS). Ao contribuir, você concorda em licenciar sua contribuição da mesma forma.
