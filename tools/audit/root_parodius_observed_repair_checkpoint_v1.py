"""Preserve the observed HUD repair without converting a missing receipt to PASS."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/parodius-observed-hud-repair'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True);catalog={}
    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(p)==sha(q)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    final=D/'parodius-hud-cancel-native-final-v1'
    assert sha(final/'proof.json')=='d8ac359cd6c2e77d4f40b83c88b7499112ba5b912e27532f237260da336b74fe'
    q=json.loads((final/'proof.json').read_text());m=json.loads((final/'manifest.json').read_text())
    assert len(m)==10698
    for p,h in m.items():assert sha(p)==h,p
    assert not q['passed'] and q['sixth_native_receipt_missing']
    assert q['original_five_native_components_passed'] and q['independent_saved_pair_and_RGB_reaggregation_passed']
    for p in final.glob('*.json'):copy(p,'final/'+p.name)
    for key in ['native_outcome_sha256','RGB_replay_sha256','cadence_sha256']:
        paths=[Path(p) for p,h in m.items() if h==q[key] and Path(p).name=='proof.json'];assert len(paths)==1,paths
        folder=paths[0].parent
        for p in folder.iterdir():
            if p.is_file() and p.suffix in ['.json','.png','.txt']:
                copy(p,key+'/'+p.name)
    native=json.loads((OUT/'native_outcome_sha256/proof.json').read_text())
    assert not native['passed'] and native['original_five_passed']
    refs=json.loads((final/'review-files.json').read_text())
    for p,h in refs.items():
        assert sha(p)==h
        if Path(p).suffix=='.py':copy(p,'frozen-tools/'+Path(p).name)
        else:copy(p,'report.txt')
    result=dict(production_adopted=False,goal_complete=False,original_native_aggregate_passed=False,
                original_five_native_components_passed=True,missing_sixth_receipt_not_backfilled=True,
                saved_actual_pair_and_RGB_scope_passed=True,ROOT_verified_bindings=len(m),
                ROOT_viewed_before_after_whole_frames=[515,813],copied_bindings=catalog,
                limits='Observed Easy Octopus death/restart repair only. Native/independent offline evidence remain explicitly separate. No Hard/other variants/natural area/pending Buffer2/global timing/crowded visibility/adoption verdict.')
    (OUT/'root-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(copied=len(catalog),verified=len(m),original_aggregate_passed=False)))


if __name__=='__main__':main()
