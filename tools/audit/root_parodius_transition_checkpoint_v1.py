"""Preserve the real death/area coverage failures without changing their verdicts."""
from pathlib import Path
import hashlib
import json
import shutil

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/parodius-transition-held'


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True)
    catalog={};verified={};inputs={}
    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(p)==sha(q)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    for name,h in [
            ('parodius-hud-transition-ready-v1','ed173cf27f257a0531af3964a3789526de7cc69654cefc47c4bb8aa7b8d2c0a2'),
            ('parodius-hud-transition-negative-final-v1','714cb2b95a48d0b734a7de788cacb13dab65bd2c52ebbd0e51e52b6e50c1d5b9')]:
        p=D/name;assert sha(p/'proof.json')==h
        j=json.loads((p/'proof.json').read_text());assert sha(p/'manifest.json')==j['manifest_sha256']
        m=json.loads((p/'manifest.json').read_text())
        for n,digest in m.items():assert sha(n)==digest,n
        verified[name]=len(m);inputs.update(m)
        for f in p.iterdir():
            if f.suffix=='.json'and f.name!='settings.json':copy(f,'packets/'+name+'/'+f.name)
    for name in ['parodius-hud-transition-native-negatives-v1',
                 'parodius-hud-transition-observer-source-v1','parodius-hud-transition-cpu-v3',
                 'parodius-hud-transition-buffer-cpu-v4','parodius-hud-transition-dmc-source-v1']:
        p=D/name
        for f in p.rglob('*'):
            if f.is_file()and f.suffix in ['.json','.txt','.png']and f.name!='settings.json':
                copy(f,'evidence/'+name+'/'+f.relative_to(p).as_posix())
    for n,h in inputs.items():
        p=Path(n)
        if p.is_relative_to(ROOT/'tools/audit'):copy(p,'frozen-tools/'+p.name)
        elif 'source-context'in n and p.suffix=='.json':copy(p,'source-context/'+p.parent.name+'-'+p.name)
    for name in ['parodius-hud-transition-readiness-2026-10-26.txt',
                 'parodius-hud-transition-native-hold-2026-10-26.txt']:
        copy(ROOT/'docs/qa'/name,'reports/'+name)
    review=dict(passed=False,production_adopted=False,
                root_verified_manifest_counts=verified,actual_native_launches=2,retries=0,
                source_ready_but_natural_reachability_unqualified=True,
                actual_failures={'death':514,'area':1560},
                common_failure='Actual body immutable record alias',
                missing_precise_native_failing_pointer_explicit=True,
                separate_source_lead='PnDeathGraphics uses thirteen immutable death records/three CHR pages outside the131-live-pose metadata. This is not yet a recovered native pointer or ROM-defect verdict.',
                root_viewed_whole_PPU_death_frames=[278,456,459,460,477,500,510,511,512,513],
                root_viewed_whole_PPU_area_frames=[278,456,459,460,477,500,510,511,512,513,1177,1178,1179,1200,1300,1500,1556,1557,1558,1559],
                natural_area_pipe_entry_and_Buffer2_hold_not_observed=True,
                copied_bindings=catalog)
    (OUT/'root-review.json').write_text(json.dumps(review,indent=2)+'\n')
    print(json.dumps(dict(checkpoint=str(OUT),verified=verified,copied=len(catalog),passed=False)))


if __name__=='__main__':main()
