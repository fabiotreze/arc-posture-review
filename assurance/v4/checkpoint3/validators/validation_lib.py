from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'
STAGES=['IDENTITY','MANAGEMENT','HOST','DEFENSE']
ALLOWED_TRANSITIONS={(STAGES[i],STAGES[i+1]) for i in range(len(STAGES)-1)}
DEFENSE=['Prevent','Detect','Respond','Recover']

def load(name): return json.loads((DATA/name).read_text(encoding='utf-8-sig'))
def ids(rows): return [r['id'] for r in rows]
def require(cond,msg,errors):
    if not cond: errors.append(msg)
def finish(errors,label):
    if errors:
        print(f'[FAIL] {label}: {len(errors)} error(s)')
        for e in errors: print(' - '+e)
        return 1
    print(f'[PASS] {label}')
    return 0

def validate_scenarios(rows,tax,checks):
    errors=[]; risks={r['id'] for r in tax['risks']}; bounds={b['id'] for b in tax['securityBoundaries']}; cids={c['id'] for c in checks}
    require(len(rows)==11,'Expected exactly 11 Security Scenarios',errors)
    require(ids(rows)==[f'AS{i:02d}' for i in range(1,12)],'Scenario IDs must be AS01..AS11 in order',errors)
    for s in rows:
        require(set(s['riskIds'])<=risks,f"{s['id']}: unknown risk",errors)
        require(set(s['securityBoundaryIds'])<=bounds,f"{s['id']}: unknown boundary",errors)
        require(set(s['controlCheckIds'])<=cids and s['controlCheckIds'],f"{s['id']}: invalid/empty controlCheckIds",errors)
        require(bool(s.get('hypothesis')) and len(s['hypothesis'])>=20,f"{s['id']}: weak hypothesis",errors)
        prereq=set(s.get('prerequisites',[]))
        for edge in s.get('attackPath',[]):
            require((edge.get('from'),edge.get('to')) in ALLOWED_TRANSITIONS,f"{s['id']}: improper attack-path transition {edge.get('from')}->{edge.get('to')}",errors)
            require(edge.get('boundaryId') in bounds,f"{s['id']}: attack path uses unknown boundary",errors)
            require(bool(edge.get('requires')) and set(edge['requires'])<=prereq,f"{s['id']}: edge has undeclared/missing prerequisite",errors)
    return errors
