from pathlib import Path
import subprocess, sys, json, hashlib, os
ROOT=Path(__file__).resolve().parents[1]
validators=['Validate-JsonSchemas.py','Validate-Mappings.py','Validate-Claims.py','Validate-SecurityScenarios.py']
tests=['Test-AttackPathHypotheses.py']

def run(cmd,cwd=ROOT):
    print('> '+' '.join(map(str,cmd)))
    return subprocess.run(cmd,cwd=cwd).returncode

def main():
    (ROOT/'reports').mkdir(parents=True, exist_ok=True)
    failures=[]
    for f in validators:
        if run([sys.executable,str(ROOT/'validators'/f)]): failures.append(f)
    for f in tests:
        if run([sys.executable,str(ROOT/'tests'/f)]): failures.append(f)
    # deterministic cross-file cardinality and JSON parsing gate
    for p in sorted((ROOT/'data').glob('*.json'))+sorted((ROOT/'schemas').glob('*.json')):
        try: json.loads(p.read_text(encoding='utf-8-sig'))
        except Exception as e: failures.append(f'{p.name}: {e}')
    print('[PASS] JSON parse gate' if not any(': ' in x for x in failures) else '[FAIL] JSON parse gate')
    report={'checkpoint':'3','version':'4.0.0','status':'PASS' if not failures else 'FAIL','failures':failures}
    (ROOT/'reports'/'last-gate-result.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    if failures:
        print('[FAIL] CHECKPOINT 3 V4 - '+', '.join(failures)); return 1
    print('[PASS] CHECKPOINT 3 V4 - ALL GATES PASSED'); return 0
if __name__=='__main__': raise SystemExit(main())
