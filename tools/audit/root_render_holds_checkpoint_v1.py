"""Preserve qualified Turtle emitter cost negatives and the real Parodius HUD defect."""
from pathlib import Path
import hashlib
import json
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
OUT=ROOT/'docs/qa/checkpoints/2026-10-26/render-lifecycle-holds'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    assert not OUT.exists();OUT.mkdir(parents=True);catalog={};tools=set()
    def copy(p,name):
        p=Path(p);q=OUT/name;q.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(p,q);assert sha(p)==sha(q)
        catalog[name]=dict(source=str(p),sha256=sha(p))
    a=D/'tmnt-equipment-emitter-ready-v1';r=json.loads((a/'receipt.json').read_text())
    assert sha(a/'receipt.json')=='ce0ff605c45df40cfb58d2763706b2ea7cddd3b955e62a49c9659bb4f2785614'
    assert r['legal_cold_max_added_cycles']==119 and not r['accepted']
    assert sha(a/'source.zip')==r['source_archive_sha256']
    assert sha(a/'source-bindings.json')==r['source_bindings_sha256']
    bindings=json.loads((a/'source-bindings.json').read_text())
    with zipfile.ZipFile(a/'source.zip') as z:
        assert set(z.namelist())==set(bindings)
        for name,h in bindings.items():
            assert hashlib.sha256(z.read(name)).hexdigest()==h
            assert sha(a/'source'/name)==h
    for name in ['receipt.json','source-bindings.json','changed-source-versus-1d741.json',
                 'changed-source-versus-50b5.json','changed-source-versus-5373.json',
                 'prior-stages.json','retained-negatives.json','review.patch','report.txt']:
        copy(a/name,'tmnt/'+name)
    for name,row in json.loads((a/'changed-source-versus-1d741.json').read_text()).items():
        assert sha(a/'source'/name)==row['after_sha256'];copy(a/'source'/name,'tmnt/source/'+name)
    for name,h in r['tools'].items():
        f=a/'tools'/name;assert sha(f)==h;copy(f,'tmnt/frozen-tools/'+name)
        if sha(ROOT/'tools/audit'/name)==h:tools.add('tools/audit/'+name)
    def refs(value,prefix):
        if isinstance(value,dict):
            if 'path' in value and 'sha256' in value:
                p=Path(value['path']);assert sha(p)==value['sha256'];copy(p,prefix+'/'+p.name)
            else:
                for k,v in value.items():refs(v,prefix+'/'+k)
        elif isinstance(value,list):
            for i,v in enumerate(value):refs(v,prefix+'/'+str(i))
    refs(r['proofs'],'tmnt/proofs')
    refs(json.loads((a/'retained-negatives.json').read_text()),'tmnt/negatives')
    stages=json.loads((a/'prior-stages.json').read_text())
    for name,v in stages.items():
        folder=Path(v['path']);assert sha(folder/'candidate.nes')==v['ROM_sha256']
        assert sha(folder/'fast-preparation.json')==v['preparation_sha256']
        copy(folder/'fast-preparation.json','tmnt/stages/'+name+'/preparation.json')
        refs(v['proofs'],'tmnt/stages/'+name+'/proofs')
    b=D/'parodius-hud-death-restart-negative-final-v1'
    assert sha(b/'proof.json')=='3dbf40e6f697cd299ceb037d2ed6b44f62608a68ebba921e53cc8612bc1df90b'
    m=json.loads((b/'manifest.json').read_text());assert len(m)==7609
    for p,h in m.items():assert sha(p)==h,p
    for name in ['proof.json','manifest.json','visual-review.json']:copy(b/name,'parodius/'+name)
    for name in ['parodius-death-observer-source-2026-10-26.txt','parodius-death-restart-hud-hold-2026-10-26.txt']:
        copy(ROOT/'docs/qa'/name,'parodius/'+name)
    for name in ['parodius_visibility_death_observer_ready_v1.py','parodius_visibility_death_observer_prepare_v1.py',
                 'parodius_visibility_death_observer_cpu_v1.py','parodius_visibility_death_records_cpu_v1.py',
                 'parodius_visibility_death_records_cpu_v2.py','parodius_visibility_area_controller_cpu_v1.py',
                 'parodius_visibility_hud_static_observer_v2.lua','parodius_visibility_death_native_freeze_v1.py',
                 'parodius_visibility_death_native_negative_v1.py']:
        copy(ROOT/'tools/audit'/name,'parodius/frozen-tools/'+name);tools.add('tools/audit/'+name)
    for folder in ['parodius-hud-death-observer-ready-v1','parodius-hud-death-observer-native-negative-v2']:
        f=D/folder
        for p in f.glob('*.json'):copy(p,'parodius/'+folder+'/'+p.name)
        if (f/'selected-full-PPU.png').exists():copy(f/'selected-full-PPU.png','parodius/selected-full-PPU.png')
    result=dict(production_adopted=False,native_granted=False,goal_complete=False,
                tmnt_source_archive_members_verified=len(bindings),tmnt_legal_added_cold_cycles=119,
                tmnt_hot_model_residual_cycles=r['residual_model_cycles'],parodius_final_bindings_verified=len(m),
                parodius_actual_glyph_failure_ROOT_viewed=True,parodius_native_failure=813,
                stage_tools=sorted(tools),copied_bindings=catalog,
                limits='Private source correctness/cost negatives and one real native HUD failure only. Later fused Turtle emitter and Parodius cancellation repair are separate unqualified successors, excluded here.')
    (OUT/'root-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(copied=len(catalog),TMNT_source_members=len(bindings),Parodius_bindings=len(m))))


if __name__=='__main__':main()
