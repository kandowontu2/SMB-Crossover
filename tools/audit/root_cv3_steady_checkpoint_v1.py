"""Verify and preserve all14 completed BASIC cells; lifecycle is still pending."""
from pathlib import Path
import csv
import hashlib
import json
import shutil

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT = ROOT/'docs/qa/checkpoints/2026-10-26/cv3-steady-basic-native'


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    native = D/'cv3-remaining-steady-native-v2/native-freeze-v1/qualification-native.json'
    assert sha(native)=='84fe5f805a3c1fb0b4ca89f19d5895c1b2ecb817282fde6ddb8cf573438d7c73'
    q = json.loads(native.read_text())
    ready = Path(q['source_readiness']['path'])
    assert sha(ready)==q['source_readiness']['sha256']
    r = json.loads(ready.read_text())
    assert q['passed'] and not q['accepted'] and q['native_launches']==15 and q['candidate_cells']==14
    verified = 0
    for records in q['all_new_native_GAME_artifacts'].values():
        for p,h in records.items():
            assert sha(p)==h,p
            verified += 1
    for p,h in q['all_launch_and_verification_artifacts'].items():
        assert sha(p)==h,p
        verified += 1
    for case in q['cases']:
        assert case['source_and_hardware_pass'] and case['strict_cadence_pass']
        assert case['cadence']['all_draw_prefix_deferrals']==[]
        arrays = []
        for field in ['baseline_game','candidate_game']:
            record = case[field]['proof']
            assert sha(record['path'])==record['sha256']
            with (Path(record['path']).parent/'cadence.csv').open() as stream:
                arrays.append(list(csv.DictReader(stream)))
        before,after = arrays
        assert len(before)==len(after)==140
        b0,c0 = int(before[0]['draws']),int(after[0]['draws'])
        assert all(int(c['draws'])-c0 >= int(b['draws'])-b0 for b,c in zip(before,after)),case['name']
    assert not OUT.exists()
    OUT.mkdir(parents=True)
    catalog = {}

    def copy(p,name,expected=None):
        p=Path(p)
        if expected:
            assert sha(p)==expected,p
        target=OUT/name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target)
        assert sha(target)==sha(p)
        catalog[name]=dict(source=str(p),sha256=sha(p))

    copy(native,'qualification-native.json')
    copy(ready,'readiness-source-only.json')
    for name,record in r['source_receipts'].items():
        copy(record['path'],'source-proofs/'+name+'.json',record['sha256'])
    for name in ['deadline','same_input_native_source_matrix']:
        rec=r[name]
        copy(rec['path'],name+'.json',rec['sha256'])
    layout=Path(r['source_layout']['path'])
    l=json.loads(layout.read_text())
    for name in ['all-deployable-files.json','implementation-from50b.patch','incremental-from0c45.patch']:
        copy(layout.parent/name,'source-layout/'+name)
    for rec in l['deployment_source']:
        copy(Path(r['source'])/rec['path'],'changed-source/'+rec['path'],rec['sha256'])
    for name,digest in {**r['frozen_tools'],**q['new_frozen_tools']}.items():
        copy(ROOT/name,'frozen-tools/'+Path(name).name,digest)
    for case in q['cases']:
        for label in ['comparison','candidate_game','baseline_game']:
            rec=case[label] if label=='comparison' else case[label]['proof']
            copy(rec['path'],'native-cases/'+case['name']+'/'+label+'.json',rec['sha256'])
    for rec in q['launches']:
        file=rec['launch']
        copy(file['path'],'launches/'+rec['name']+'.json',file['sha256'])
    for name in ['cv3-remaining-sfx-steady-ready-2026-10-26.txt','cv3-remaining-sfx-steady-basic-native-2026-10-26.txt']:
        copy(ROOT/'docs/qa'/name,'reports/'+name)
    review=dict(passed=True,accepted=False,production_adopted=False,
                root_verified_native_artifact_bindings=verified,
                root_independent_cumulative_draw_prefix_cases=14,
                native_launches=15,retries=0,worker_released=q['worker_released'],
                remaining=q['remaining_required'],copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),verified=verified,cases=14,copied=len(catalog),accepted=False)))


if __name__=='__main__':
    main()
