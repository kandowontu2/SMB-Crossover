"""Build an external Roll shared-host fade proposal. No install or native launch."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

ROOT=Path(__file__).resolve().parents[2]
BASE='9bac46e934d3301e378139783febf2d54c4fd5753a62e082f2d7e6580946d58c'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
HELPER='''; Match InventoryDrawPickups::Drops age/parity admission; supplied art is unchanged.
; Appended after existing ROLL_CORE owners to retain all existing code PCs.
.pushseg
.segment "ROLL_CORE"
.proc RlDropVisibleKind
 lda InvDropKind,x
 beq Done
 php
 lda InvDropAgeHi,x
 bne Fade
 lda InvDropAge,x
 cmp #240
 bcc Visible
Fade:
 lda FrameCounter
 and #1
 beq Visible
 plp
 lda #0
 rts
Visible:
 plp
 lda InvDropKind,x
Done:rts
.endproc
.popseg
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--frozen',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();assert sha(a.frozen/'candidate.nes')==BASE
    a.output.mkdir(parents=True,exist_ok=False);overlay=a.output/'overlay';overlay.mkdir()
    shutil.copytree(a.frozen/'src',overlay/'src')
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg',overlay/'smb1base-mmc5-expanded.cfg')
    inputs=[ROOT/'build_options.ini',ROOT/'smb1base-mmc5-expanded.cfg',ROOT/'tools/build_mmc5_expanded.py']
    inputs+=sorted(p for p in(ROOT/'chr').rglob('*')if p.is_file())
    deps={str(p.relative_to(ROOT)).replace('\\','/'):sha(p)for p in inputs}
    def build(out):
        z=subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(ROOT),'--source-overlay',str(overlay),'--output',str(out)],capture_output=True,text=True)
        out.with_suffix('.driver.log').write_text(z.stdout+z.stderr,encoding='utf-8');assert z.returncode==0,z.stdout+z.stderr
    baseline=a.output/'baseline/candidate.nes';baseline.parent.mkdir();build(baseline);assert sha(baseline)==BASE
    originals={n:(overlay/'src'/n).read_bytes()for n in ['roll_render.s','roll.s']}
    old=originals['roll_render.s'];assert old.count(b'Drops:stx RlSlot')==1
    needle=b'Drops:stx RlSlot\n lda InvDropKind,x\n beq DropNext'
    if b'\r\n'in old:needle=needle.replace(b'\n',b'\r\n')
    assert old.count(needle)==1
    (overlay/'src/roll_render.s').write_bytes(old.replace(needle,needle.replace(b'lda InvDropKind,x',b'jsr RlDropVisibleKind')))
    old=originals['roll.s'];needle=b'.include "roll_weapons.s"';assert old.count(needle)==1
    nl=b'\r\n'if b'\r\n'in old else b'\n'
    (overlay/'src/roll.s').write_bytes(old.replace(needle,needle+nl+b'.include "roll_drop_fade.s"'))
    (overlay/'src/roll_drop_fade.s').write_text(HELPER,encoding='utf-8')
    patch=''
    for n in ['roll_render.s','roll.s','roll_drop_fade.s']:
        before=originals.get(n,b'').decode('utf-8').splitlines(True)
        after=(overlay/'src'/n).read_text(encoding='utf-8').splitlines(True)
        patch+=''.join(difflib.unified_diff(before,after,fromfile='a/src/'+n if before else'/dev/null',tofile='b/src/'+n))
    (a.output/'sourcepatch.patch').write_text(patch,encoding='utf-8')
    candidate=a.output/'candidate.nes';build(candidate)
    assert deps=={n:sha(ROOT/n)for n in deps}
    b,c=map(scoped_load,[baseline,candidate]);bm={n:address(b,n)for n in b['syms']};cm={n:address(c,n)for n in c['syms']}
    moved={n:[v,cm.get(n)]for n,v in bm.items()if cm.get(n)!=v};assert not moved,moved
    call=location(b,'RlDraw::Drops')+3;callpc=address(b,'RlDraw::Drops')+3
    assert b['raw'][call:call+3]==bytes([0xbd,address(b,'InvDropKind')&255,address(b,'InvDropKind')>>8])
    at=location(c,'RlDropVisibleKind');size=int(c['syms']['RlDropVisibleKind']['size'],0)
    assert address(c,'RlDropVisibleKind')==address(b,'RlWeapons')+int(b['syms']['RlWeapons']['size'],0)
    want=bytearray(b['raw']);want[call:call+3]=bytes([0x20,address(c,'RlDropVisibleKind')&255,address(c,'RlDropVisibleKind')>>8]);want[at:at+size]=c['raw'][at:at+size]
    assert bytes(want)==c['raw']
    proof=dict(source_cpu_proposal_only=True,native_passed=False,goal_complete=False,
        base_sha256=BASE,candidate_sha256=sha(candidate),script_sha256=sha(Path(__file__)),
        sourcepatch_sha256=sha(a.output/'sourcepatch.patch'),changed_source=['src/roll_render.s','src/roll.s','src/roll_drop_fade.s'],
        replaced_call=dict(bank=(call-16)//8192,pc=callpc,old=b['raw'][call:call+3].hex(),new=c['raw'][call:call+3].hex()),
        new_helper=dict(bank=(at-16)//8192,pc=address(c,'RlDropVisibleKind'),bytes=size,old_unused_bytes=b['raw'][at:at+size].hex(),new=c['raw'][at:at+size].hex()),
        all_old_symbol_addresses_identical=True,all_other_ROM_bytes_identical=True,RAM_CHR_art_identical=True,
        dependencies=deps,reference='Shared InventoryDrawPickups::Drops source ageHi/age>=240 then oddFrameCounter skip. Native9bac bothmode actualage236..247 draw-cursor andPPU omission proof retained separately; this candidate has no native execution.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in proof.items()if k!='dependencies'}))


if __name__=='__main__':main()
