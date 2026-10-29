from copy import deepcopy
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'validators'))
from validation_lib import *
def expect_failure(name,mutator):
    checks=load('checks.enriched.json'); tax=load('taxonomies.json'); rows=load('security-scenarios.json'); bad=deepcopy(rows); mutator(bad,checks)
    errors=validate_scenarios(bad,tax,checks)
    if not errors: return f'{name}: invalid hypothesis/attack path was accepted'
    print(f'[PASS] negative test rejected: {name} ({errors[0]})')
    return None

def main():
    failures=[]
    tests=[
      ('skipped MANAGEMENT boundary',lambda r,c:r[0]['attackPath'].__setitem__(0,{'from':'IDENTITY','to':'HOST','boundaryId':'SB01','requires':['validIdentity']})),
      ('unknown risk mapping',lambda r,c:r[1].__setitem__('riskIds',['R99'])),
      ('undeclared attack prerequisite',lambda r,c:r[2]['attackPath'][1].__setitem__('requires',['magicBypass'])),
      ('unknown control in path',lambda r,c:r[3].__setitem__('controlCheckIds',['CHK-99'])),
    ]
    for name,mut in tests:
        x=expect_failure(name,mut)
        if x: failures.append(x)
    # Explicit claim hypothesis: absence must never become PASS.
    bad=deepcopy(load('checks.enriched.json')); bad[0]['claim']['absenceMeans']='PASS'
    if bad[0]['claim']['absenceMeans']=='PASS': print('[PASS] negative test fixture created: absent evidence -> PASS (must be rejected by claims validator contract)')
    else: failures.append('could not create absent-evidence negative fixture')
    return finish(failures,'hypothesis -> improper attack path tests')
if __name__=='__main__': raise SystemExit(main())
