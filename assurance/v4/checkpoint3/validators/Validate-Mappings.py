from validation_lib import *
def main():
    checks=load('checks.enriched.json'); tax=load('taxonomies.json'); scenarios=load('security-scenarios.json'); assessments=load('control-assessments.json'); coverage=load('defense-coverage.json')
    errors=[]; risk_ids={x['id'] for x in tax['risks']}; scenario_ids={x['id'] for x in scenarios}; boundary_ids={x['id'] for x in tax['securityBoundaries']}
    require(len(checks)==64,'Expected exactly 64 enriched CHKs',errors)
    require(ids(checks)==[f'CHK-{i:02d}' for i in range(1,65)],'CHK IDs must be CHK-01..CHK-64 in order',errors)
    require(len(assessments)==64,'Expected 64 Control Assessments',errors); require(len(coverage)==64,'Expected 64 Defense Coverage rows',errors)
    for c in checks:
        require(set(c['riskIds'])<=risk_ids and c['riskIds'],f"{c['id']}: invalid/empty risk mapping",errors)
        require(set(c['scenarioIds'])<=scenario_ids and c['scenarioIds'],f"{c['id']}: invalid/empty scenario mapping",errors)
        require(set(c['securityBoundaryIds'])<=boundary_ids and c['securityBoundaryIds'],f"{c['id']}: invalid/empty boundary mapping",errors)
        require(c['mappingConfidence'] in {'high','medium'},f"{c['id']}: low/invalid mapping confidence requires review",errors)
        require(set(c['defenseFunctions'])<=set(DEFENSE) and c['defenseFunctions'],f"{c['id']}: invalid defense functions",errors)
        require(c['securityModelStage'] in STAGES,f"{c['id']}: invalid security model stage",errors)
        require(c['zeroTrust']['principles'] and c['zeroTrust']['pillars'],f"{c['id']}: Zero Trust mapping incomplete",errors)
        require(c['securityScopes'],f"{c['id']}: T0/T1/T2/Global mapping absent",errors)
    covered=set(fn for c in checks for fn in c['defenseFunctions']); require(covered==set(DEFENSE),f'Defense lifecycle incomplete: {covered}',errors)
    stages=set(c['securityModelStage'] for c in checks); require(stages==set(STAGES),f'Security model stages incomplete: {stages}',errors)
    return finish(errors,'mapping validator')
if __name__=='__main__': raise SystemExit(main())
