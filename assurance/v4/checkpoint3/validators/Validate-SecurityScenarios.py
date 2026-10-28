from validation_lib import *
def main():
    checks=load('checks.enriched.json'); tax=load('taxonomies.json'); rows=load('security-scenarios.json'); errors=validate_scenarios(rows,tax,checks)
    cards=load('action-cards.json')
    require(len(cards)==11,'Expected exactly 11 Action Cards',errors)
    require([x['riskId'] for x in cards]==[f'R{i:02d}' for i in range(1,12)],'Action Cards must cover R01..R11 exactly once',errors)
    require([x['scenarioId'] for x in cards]==[f'AS{i:02d}' for i in range(1,12)],'Action Cards must cover AS01..AS11 exactly once',errors)
    for s in rows:
        mapped={c['id'] for c in checks if s['id'] in c['scenarioIds']}
        require(set(s['controlCheckIds'])==mapped,f"{s['id']}: controlCheckIds drift from CHK mappings",errors)
        got={fn for c in checks if s['id'] in c['scenarioIds'] for fn in c['defenseFunctions']}
        require(set(s['expectedDefenseFunctions'])==got,f"{s['id']}: defense coverage drift",errors)
    return finish(errors,'Security Scenarios validator')
if __name__=='__main__': raise SystemExit(main())
