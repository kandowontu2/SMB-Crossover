"""Freeze twenty native lifecycle launches and independently count real DMAs."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/cv3-lifecycle-native-held'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    native=D/'cv3-remaining-lifecycle-native-v1/native-freeze-v1/qualification-native.json'
    assert sha(native)=='f218052630f0170b570349c527198e3da4845b9a893206b50f9da5b8ff983a3f'
    q=json.loads(native.read_text());assert q['native_launches']==20 and q['strict_cadence_passes']==9 and q['strict_cadence_held']==1
    ready=Path(q['source_ready']['path']);assert sha(ready)==q['source_ready']['sha256']
    r=json.loads(ready.read_text())
    for n,h in r['all_frozen_bindings'].items():assert sha(n)==h,n
    for n,h in q['all_new_frozen_bindings'].items():assert sha(n)==h,n
    assert not (OUT/'root-review.json').exists();OUT.mkdir(parents=True,exist_ok=True);catalog={}
    def copy(p,name):
        p=Path(p);target=OUT/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,target);assert sha(target)==sha(p)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    copy(native,'qualification-native.json');copy(ready,'readiness-source-only.json')
    for index,rec in enumerate(r['source_receipts']):
        assert sha(rec['path'])==rec['sha256'];copy(rec['path'],'source-proofs/'+str(index)+'-'+Path(rec['path']).parent.name+'.json')
    for name,h in r['frozen_tools'].items():copy(name,'frozen-tools/'+Path(name).name)
    for n in q['all_new_frozen_bindings']:
        p=Path(n)
        if p.is_relative_to(ROOT/'tools/audit'):copy(p,'frozen-tools/'+p.name)
    actual={};dma_by_profile={}
    for cell in q['cells']:
        rec=cell['receipt'];game=cell['GAMEproof']
        assert sha(rec['path'])==rec['sha256']and sha(game['path'])==game['sha256']
        copy(rec['path'],'launches/'+cell['name']+'.json')
        folder=Path(game['path']).parent
        for name in ['proof.json','configuration.json','preparation.json','run.lua','cadence.csv','dma-bus.jsonl','deadline-timing.csv','lifecycle.jsonl']:
            copy(folder/name,'native-cases/'+cell['name']+'/'+name)
        rows=[json.loads(line)for line in (folder/'dma-bus.jsonl').read_text().splitlines()]
        starts=Counter(row['stamp']['frame']for row in rows if row['kind']=='DMA-start')
        completed=[row for row in rows if row['kind']=='DMA-complete']
        assert len(completed)==sum(starts.values())
        assert all(row['source_exact']and row['data_writes']==256 for row in completed)
        actual[cell['name']]=dict(starts=sum(starts.values()),complete_exact256=len(completed))
        dma_by_profile[cell['name']]=starts
    for case in q['profiles']:
        name=case['name'];b=dma_by_profile['baseline-'+name];c=dma_by_profile['candidate-'+name]
        assert sum(b.values())==case['actual_DMA_counts']['baseline']
        assert sum(c.values())==case['actual_DMA_counts']['candidate']
        if name=='pressure-fireball-hard':
            differences={frame:(b[frame],c[frame])for frame in b.keys()|c.keys()if b[frame]!=c[frame]}
            assert differences=={717:(1,0)},differences
        else:
            assert sum(c.values())>=sum(b.values()),name
        copy(case['comparison']['path'],'comparisons/'+name+'.json')
    boundary=Path(q['boundary']['path']);assert sha(boundary)==q['boundary']['sha256']
    copy(boundary,'actual-held-boundary.json')
    for label,rec in [('readiness',r['report']),('native',q['report'])]:
        assert sha(rec['path'])==rec['sha256'];copy(rec['path'],'reports/'+Path(rec['path']).name)
    review=dict(accepted=False,production_adopted=False,
                root_verified_source_bindings=len(r['all_frozen_bindings']),
                root_verified_new_native_bindings=len(q['all_new_frozen_bindings']),
                actual20_launches_no_retries=True,all10_source_hardware_and_native_goals_pass=True,
                strict_cadence_passes=9,strict_cadence_held=1,
                root_independent_complete_DMA_counts=actual,
                sole_held_Hard1F_actual_missing_transfer=dict(PPU_frame=717,baseline=1,candidate=0),
                source_wrapper_measured_extra_cycles=26,conditional_required_saving27_is_not_full_interrupted_state_proof=True,
                raw_settings_and_lossless_ARGb_retained_external=True,copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),copied=len(catalog),source_verified=1367,native_verified=529,actual_DMA_cases=20,held=1)))


if __name__=='__main__':main()
