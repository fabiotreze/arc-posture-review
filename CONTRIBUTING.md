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
4. Texts exist in EN-US and PT-BR. New Portuguese detail rules go in the app table (`PT_DETAIL_RULES`); then run `python tools/Sync-PtRules.py` to regenerate `criteria/v4/pt-br-detail-rules.json` (`tools/Test-PtBrContent.py` checks they match).
5. After changing the collector, criteria, CSS or the kit files run `python tools/Build-Kit.py --write-hash` and `python tools/Sync-ReportAssets.py`, then `python tools/Prepare-Release.py checksums`.
6. Run the gates before pushing:

```powershell
python -m pip install -r requirements-dev.txt
python tools/Invoke-V4FinalGates.py --profile release
```

Releases follow the process in `docs/v4/` (security review record, `release/<version>/`, tag `vX.Y.Z`).

## Licenses

Code: [MIT](LICENSE). Documentation and text: [CC BY 4.0](LICENSE-DOCS). By contributing you agree to license your contribution the same way.

---

## Contribuindo

Obrigado por ajudar. É um projeto pessoal e independente; correções que citem a documentação oficial da Microsoft são as mais úteis.

- **Nunca anexe nem cole dados coletados**: o `.zip`, `results.json`, `findings/*.csv` e os relatórios contêm nomes de máquinas, IDs de subscription e de principals e autores do Activity Log. Descreva o caso com nomes fictícios ou use `tests/fixtures/reviewed-lab-sanitized.zip`.
- Vulnerabilidades neste repositório: use *Report a vulnerability* na aba Security ([SECURITY.md](SECURITY.md)), não uma issue pública.
- Informe a versão usada e se o problema está no coletor, no motor, no relatório ou no app.
- Pull requests: parta da `main` (protegida), mantenha o vocabulário de postura (*lacuna verificada*, *oportunidade de melhoria*, *não verificado*), mantenha o coletor somente leitura (com BOM UTF-8 e finais de linha consistentes), mantenha EN-US e PT-BR e rode `python tools/Invoke-V4FinalGates.py --profile release` antes de enviar.
