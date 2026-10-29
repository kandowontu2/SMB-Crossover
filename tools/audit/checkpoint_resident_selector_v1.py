"""Retain the independently frozen same-span resident graphics selector."""
from pathlib import Path
import hashlib,json,subprocess,sys
from checkpoint_roster_packets_v1 import ROOT,verify


def bind(path):
    p=Path(path).resolve();b=p.read_bytes()
    return dict(path=str(p),bytes=len(b),sha256=hashlib.sha256(b).hexdigest())


def main():
    hp=ROOT/'build/gimmick-resident-selector-v1/handoff.json'
    assert bind(hp)['sha256']=='22df023201c615d7c36f4d0c7a24663d5b33cf413ba51f780b7f0569109f9e93'
    h=json.loads(hp.read_text());seen={};verify(h,seen)
    c=json.loads(Path(h['controls']['path']).read_text())
    q=json.loads(Path(h['closure']['path']).read_text())
    assert c['passed']and not c['native']and q['passed']
    assert [len(c[n])for n in ['full_Main','full_NMI','menu_lives','direct']]==[352,176,176,54]
    assert q['changed_bytes']==116 and q['changed_banks']==[125,126,127]
    assert q['outer_capsule']==[0x809a,0x8122]and len(q['actual_IRQ'])==40
    public=ROOT/'docs/qa/resident-graphics-selector-2026-10-29.json';assert not public.exists()
    report=dict(status=h['status'],handoff=bind(hp),candidate=h['candidate'],
        exact_capsule_bytes=136,full_Main=352,normal_and_lag_NMI=176,menu_lives=176,
        original_row_controls=54,genuine_IRQ_seams=40,changed_bytes=116,
        routing='Original raw6..23 rows retained; raw26 mapsC73 and raw28 mapsC12. Raw24/25/27 remain unsupported. No menu/gameplay admission by this graphics-only change.',
        deliberate_scratch_change='Selector terminal X is raw identity rather than raw-6. Actual complete callers retain live AXYP/SP, hardware banks, nonstack RAM and33SMC bytes; genuine writer histories justify dead stack differences.',
        genuine_relink='Four internal helpers/table entries move within the same capsule; four external symbolic operands are genuinely relinked, including final125 mirror. Other preexisting symbols remain exact.',
        limits='Finite source CPU arenas only; no physical PPU/DMA/native timing or complete new-character qualification. DK/Gimmick owners must still bind their real graphics records/CHR and validate actual native visuals.',
        controls=h['controls'],closure=h['closure'],unique_bound_files=len(seen),
        shared_Downloads_unchanged=True)
    public.write_text(json.dumps(report,indent=2)+'\n')
    allowed={'.s','.d','.json','.txt','.py'}
    owned=[Path(p)for p in h['owned_files']if Path(p).suffix in allowed]
    root=dict(h,report=bind(public),original_handoff=bind(hp),actual_ASM_dependencies={},
        owned_files=[bind(p)for p in owned+[public,Path(__file__).resolve()]])
    target=hp.parent/'root-checkpoint.json';assert not target.exists()
    target.write_text(json.dumps(root,indent=2)+'\n')
    subprocess.run([sys.executable,'-B',str(ROOT/'tools/audit/checkpoint_roster_component_v5.py'),
        '--handoff',str(target),'--name','resident-graphics-selector-for-gimmick-dk'],cwd=ROOT,check=True)
    p=ROOT/'docs/qa/new-character-source-progress-2026-10-28.json';state=json.loads(p.read_text())
    state['Shared_resident_graphics_selector']=dict(status=h['status'],report=bind(public),
        checkpoint='checkpoints/2026-10-28/resident-graphics-selector-for-gimmick-dk')
    p.write_text(json.dumps(state,indent=2)+'\n')
    print(json.dumps(dict(report=bind(public),bound_files=len(seen))))


if __name__=='__main__':main()
