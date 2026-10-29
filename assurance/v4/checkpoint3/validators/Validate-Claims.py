from validation_lib import *
def main():
    checks=load('checks.enriched.json'); assessments=load('control-assessments.json'); errors=[]
    allowed_types={'configuration','telemetry','inventory','documentary','absence','effectiveness'}; allowed_abs={'FAIL','WARN','UNKNOWN','NOT_APPLICABLE','NOT_OBSERVED'}
    for c in checks:
        cl=c.get('claim',{})
        require(cl.get('claimType') in allowed_types,f"{c['id']}: invalid claimType",errors)
        require(bool(cl.get('evidenceRequired')),f"{c['id']}: evidenceRequired empty",errors)
        require({'scope','timestamp','source'}<=set(cl.get('evidenceRequired',[])),f"{c['id']}: evidence must include scope/timestamp/source",errors)
        require(cl.get('absenceMeans') in allowed_abs,f"{c['id']}: invalid absenceMeans",errors)
        require(cl.get('absenceMeans')!='PASS',f"{c['id']}: absence can never mean PASS",errors)
        require('absence is never interpreted as PASS' in cl.get('evaluationRule',''),f"{c['id']}: evaluation rule must reject absent-evidence PASS",errors)
    amap={a['checkId']:a for a in assessments}
    require(set(amap)=={c['id'] for c in checks},'Control Assessment/CHK key mismatch',errors)
    for c in checks:
        require(amap[c['id']]['claim']==c['claim'],f"{c['id']}: claim drift between enriched check and assessment",errors)
    return finish(errors,'claims validator')
if __name__=='__main__': raise SystemExit(main())
