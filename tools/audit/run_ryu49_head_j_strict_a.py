"""Fresh J binding admissions, native-query and independent end-effect proofs."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
PACKET=ROOT/'build/verification/ryu49o2-head-checkers-j'
OUT=ROOT/'build/verification/root49o2-head-j-strict-a'
PY314=Path('C:/Users/kando/AppData/Local/Programs/Python/Python314/python.exe')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    sys.dont_write_bytecode=True
    assert not OUT.exists()
    assert sha(PACKET/'freeze.json')=='33660ca365496b4f2fc50e8b0b399311d029c281d299917c7346ac7642397a96'
    native=ROOT/'build/verification/root49o2-head-i-native-a/report.json'
    assert sha(native)=='0c0b71c95f1b139d0e4a99fd466dcf8c88a136d09bb3faffd112f3be9826230a'
    n=json.loads(native.read_text())
    assert all(c['native_exit']==(0 if c['role']=='e' else 1) for c in n['cases'])
    f=json.loads((PACKET/'freeze.json').read_text())
    for k,r in f['files'].items():assert sha(PACKET/k)==r['sha256']
    for k,h in f['dependencies'].items():assert sha(ROOT/k)==h
    OUT.mkdir()
    report=dict(status='RUNNING_J_STRICT_COMPONENT_PROOFS',script_sha256=sha(Path(__file__)),
                actual_I_native_report_sha256=sha(native),cases=[],accepted_release=False,goal_complete=False)
    def save():(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    save()
    for c in n['cases']:
        for kind in (['native','end'] if c['role']=='e' else ['native']):
            stem=f"{c['role']}-{c['mapper']}-{kind}"
            output=OUT/(stem+'.json')
            command=[str(PY314),str(PACKET/('check_native.py' if kind=='native' else 'check_end.py')),
                     '--mapper',c['mapper'],'--binding',c['binding'],'--execute','--output',str(output)]
            case=dict(mapper=c['mapper'],role=c['role'],kind=kind,command=command)
            report['cases'].append(case);save()
            with (OUT/(stem+'.log')).open('wb') as log:
                p=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
            case.update(exit=p.returncode,log_sha256=sha(OUT/(stem+'.log')))
            if output.exists():case.update(report_sha256=sha(output),report=json.loads(output.read_text()))
            save()
    for k,r in f['files'].items():assert sha(PACKET/k)==r['sha256']
    report.update(status='COMPLETE_J_STRICT_PROOFS_ALL_NEGATIVES_AND_GAPS_RETAINED',
                  qualification='Actual compiled query reexecution and separately scoped proper-source end effects. CPU-only case80 and full source lifecycle/ordinary-route obligations remain open.')
    save()
    print(json.dumps(dict(status=report['status'],exits=[(c['role'],c['mapper'],c['kind'],c['exit']) for c in report['cases']],report_sha256=sha(OUT/'report.json'))))

if __name__=='__main__':main()
