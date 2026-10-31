"""Repair the reversed Rescue Rangers pose selector; preserve all gameplay bytes."""
from pathlib import Path
import difflib
import hashlib
import json
import sys

R = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(R/'tools/audit'), str(R/'tools')]
import prepare_current_rcr_misc_chr_fix_1030_v1 as B
from link_pit_rygar_sophia_audit_cpu import scoped_load, Arena
from check_tmnt_render_oa import address, location

P = R/'build/current-rcr-misc-chr-fix-1030-v1'
O = R/'build/current-chip-facing-fix-1030-v1'
sha = B.sha
save = B.save


def main():
    assert not O.exists()
    assert sha(P/'candidate.nes') == '3bac3d9ad5d0f93538113095a5b800317ab3e829075eae94195ae4eed82eb0f3'
    parent = json.loads((P/'source-proof.json').read_text())
    for p,h in parent['bindings'].items():
        assert sha(p)==h,p
    O.mkdir()
    copied=[]
    for p in P.rglob('*'):
        if p.is_file() and p.suffix in {'.s','.inc','.cfg'}:
            q=O/p.relative_to(P)
            q.parent.mkdir(parents=True,exist_ok=True)
            q.write_bytes(p.read_bytes())
            copied.append(q)
    p=O/'src/chip_dale_render.s'
    old=p.read_text()
    needle=' lda PlayerFacingDir\n cmp #2\n beq Left\n lda CdPoseRightLo,x'
    assert old.count(needle)==1
    new=old.replace(needle,
        '; Donor table names are inverted: Left contains right-facing pixels.\n'
        ' lda PlayerFacingDir\n cmp #2\n bne Left\n lda CdPoseRightLo,x')
    p.write_text(new)
    (O/'source.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
        fromfile='parent/src/chip_dale_render.s',tofile='new/src/chip_dale_render.s')))
    p=O/'private.cfg'
    p.write_text(p.read_text().replace(str(P),str(O)).replace(P.as_posix(),O.as_posix()))
    compile_cmd=[v.replace(str(P),str(O)) for v in json.loads((P/'compile-main.json').read_text())['command']]
    link_cmd=[v.replace(str(P/'candidate'),str(O/'candidate'))
        .replace(str(P/'private.cfg'),str(O/'private.cfg'))
        .replace(str(P/'main.o'),str(O/'main.o')) for v in json.loads((P/'link.json').read_text())['command']]
    inputs={Path(v):sha(v) for v in link_cmd if v.endswith('.o') and Path(v)!=O/'main.o'}
    B.O=O
    B.run(compile_cmd,'compile-main')
    B.run(link_cmd,'link')
    B.prepare(R,O/'candidate.nes')
    assert all(sha(p)==h for p,h in inputs.items())
    before,syms,addr,loc,_=B.linked(P/'candidate.nes')
    after,newsyms,_,_,_=B.linked(O/'candidate.nes')
    assert all(n in newsyms and s['val']==newsyms[n]['val'] for n,s in syms.items())
    at=loc('CdSetPose')
    code=before[at:at+int(syms['CdSetPose']['size'],0)]
    needle=bytes([0xad,addr('PlayerFacingDir')&255,addr('PlayerFacingDir')>>8,0xc9,2,0xf0])
    assert code.count(needle)==1
    delta=at+code.index(needle)+5
    assert before[delta]==0xf0 and after[delta]==0xd0
    assert [i for i,(a,b) in enumerate(zip(before,after)) if a!=b]==[delta]
    assert len(before)==len(after) and before[:16]==after[:16] and before[1048592:]==after[1048592:]
    # Execute the actual linked selector for every source pose and both real
    # SMB facing values. No movement, collision, or throw code is modified.
    bundle=scoped_load(O/'candidate.nes')
    cases=[]
    for pose in range(60):
        for face in (1,2):
            q=Arena(bundle,14)
            # Actual graphics caller has donor art mapped in C; direct selector
            # does not switch it itself.
            artbank=(location(bundle,'CdArtBegin')-16)//8192
            q.m.page(2,artbank)
            q.set('CurrentBankC',artbank|128)
            q.put(PlayerFacingDir=face,Player_Rel_XPos=104)
            c,writes=q.invoke('CdSetPose',x=pose)
            label=f'CdPose{pose}'+('Left' if face==1 else 'Right')
            actual=q.get('SmPosePtr')+256*q.get('SmPosePtr',1)
            assert actual==address(bundle,label)
            assert q.get('CdPose')==pose and q.get('PlayerFacingDir')==face
            assert q.get('Player_Pos_ForScroll')==104 and c.sp==0xfd
            cases.append(dict(pose=pose,facing=face,record=label,pointer=actual))
    for p,h in parent['bindings'].items():
        assert sha(p)==h,p
    save(O/'selector-controls.json',dict(passed=True,native=False,cases=cases,
        scope='120 actual linked CdSetPose executions; donor C art mapping is explicit. Standing pixel direction was visually confirmed separately; this does not claim a full native route.'))
    files=set(copied)|set(inputs)|{Path(__file__),Path(B.__file__),P/'source-proof.json',P/'candidate.nes'}
    files.update(p for p in O.rglob('*') if p.is_file())
    proof=dict(passed=True,native=False,installed=False,parent_ROM_sha256=sha(P/'candidate.nes'),
        ROM_sha256=sha(O/'candidate.nes'),changed_ROM_bytes=1,changed_file_offset=delta,
        before_opcode=240,after_opcode=208,public_symbol_values_exact=True,
        all_header_CHR_other_PRG_exact=True,actual_selector_cases=len(cases),
        RCR_native_misc_repair_retained=True,changed_sources=['src/chip_dale_render.s'],
        semantics='SMB facing1 selects donor Left table (right-facing pixels); facing2 selects donor Right table (left-facing pixels). Shared by Chip, Dale, gameplay and colored portrait. Movement/box direction bytes unchanged.',
        bindings={str(p):sha(p) for p in sorted(files)})
    save(O/'source-proof.json',proof)
    print(json.dumps({k:proof[k] for k in ['passed','ROM_sha256','changed_ROM_bytes','actual_selector_cases']}))


if __name__=='__main__':
    main()
