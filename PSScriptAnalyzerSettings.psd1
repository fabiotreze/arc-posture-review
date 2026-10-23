# PSScriptAnalyzer settings shared by the release gate (.github/workflows/release.yml)
# and the local check (tools/Test-BeforePublish.ps1). Keep in sync with psscriptanalyzer.yml (excludeRule).
@{
    Severity     = @('Error', 'Warning')
    ExcludeRules = @(
        'PSAvoidUsingPositionalParameters', # script style; no risk
        'PSAvoidUsingWriteHost'             # progress output shown to the operator
    )
}
