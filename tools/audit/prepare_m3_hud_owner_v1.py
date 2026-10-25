"""Private, fixed-layout fix for transient SMB3 HUD ownership withdrawal."""
from pathlib import Path
import argparse, difflib, hashlib, json, shutil, subprocess, sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address, location

ROOT=Path(__file__).resolve().parents[2]
BASE='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--base-sha256',default=BASE);a=p.parse_args()
    out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
    overlay=out/'overlay';shutil.copytree(ROOT/'src',overlay/'src')
    shutil.copy2(ROOT/'smb1base-mmc5-expanded.cfg',overlay/'smb1base-mmc5-expanded.cfg')
    def build(path):
        with path.with_suffix('.host.log').open('w')as log:
            subprocess.run([sys.executable,str(ROOT/'tools/build_mmc5_expanded.py'),'--workspace',str(ROOT),'--source-overlay',str(overlay),'--output',str(path)],cwd=ROOT,check=True,stdout=log,stderr=subprocess.STDOUT)
    oldrom=out/'baseline.nes';build(oldrom);assert sha(oldrom)==a.base_sha256
    source=overlay/'src/x5_bounce.s';old=source.read_bytes();nl=b'\r\n'if b'\r\n'in old else b'\n'
    text=old.decode().replace('\r\n','\n')
    before=' jmp X5NativeInventoryUiLeaf\n .res 15,$ea\nLegacy:'
    after=''' jmp X5NativeInventoryUiLeaf
; The SMB3 P-bar owns its font throughout the update, including a lag NMI
; between this generic input leaf and M3Hud. Other native leaves still hide
; the legacy inventory font. Reuse this previously unreachable15-byte tail.
HudRead:
 cpx #17
 bne OrdinaryHud
 lda #0
 clc
 rts
OrdinaryHud:
 lda InvHudActive
 clc
 rts
 .res 2,$ea
Legacy:'''
    assert text.count(before)==1;text=text.replace(before,after)
    before='  ldx SelectedCharacter\n  clc\n  lda InvHudActive\n  beq Done'
    after='  ldx SelectedCharacter\n  clc\n  jsr X5OwnInventoryUi::HudRead\n  beq Done'
    assert text.count(before)==1;text=text.replace(before,after)
    new=text.replace('\n',nl.decode()).encode();source.write_bytes(new)
    (out/'review.patch').write_text(''.join(difflib.unified_diff(old.decode().splitlines(True),new.decode().splitlines(True),fromfile='a/src/x5_bounce.s',tofile='b/src/x5_bounce.s')),encoding='utf-8')
    candidate=out/'candidate.nes';build(candidate)
    b,c=scoped_load(oldrom),scoped_load(candidate)
    assert all(address(c,n)==address(b,n)for n in b['syms']),[(n,address(b,n),address(c,n))for n in b['syms']if address(c,n)!=address(b,n)]
    p1=location(b,'X5OwnInventoryUi::Legacy')-15
    p2=location(b,'X5NativeInventoryUiLeaf::Done')-18
    # Only the old fifteen-byte unreachable pad and one real three-byte read
    # can change. Determine the latter from its unique actual operand bytes.
    start=location(b,'X5NativeInventoryUiLeaf');end=location(b,'X5NativeInventoryUiLeaf::Done')
    needle=bytes([0xad,address(b,'InvHudActive')&255,address(b,'InvHudActive')>>8])
    at=b['raw'].find(needle,start,end);assert at>=0 and b['raw'].find(needle,at+1,end)<0
    allowed=set(range(p1,p1+15))|set(range(at,at+3))
    changes=[i for i,(x,y)in enumerate(zip(b['raw'],c['raw']))if x!=y]
    assert len(b['raw'])==len(c['raw'])and set(changes)<=allowed
    assert b['raw'][p1:p1+15]==b'\xea'*15
    proof=dict(passed=True,native_passed=False,goal_complete=False,base_sha256=a.base_sha256,candidate_sha256=sha(candidate),
               changed_source='src/x5_bounce.s',baseline_source_sha256=hashlib.sha256(old).hexdigest(),candidate_source_sha256=sha(source),
               all_preexisting_symbol_values_identical=True,RAM_CHR_identical=True,changed_bytes=len(changes),
               change_windows=[dict(bank=(p1-16)//8192,offset=p1,bytes=15),dict(bank=(at-16)//8192,offset=at,bytes=3)],
               patch_sha256=sha(out/'review.patch'),tool_sha256=sha(Path(__file__)),
               scope='Retain active custom P-bar ownership at the generic inventory leaf. No early NMI/font publication change and no new resident space, RAM, CHR or bank. Native pixel/timing and affected-leaf CPU/performance qualification pending.')
    (out/'proof.json').write_text(json.dumps(proof,indent=2)+'\n',encoding='utf-8');print(json.dumps(proof))


if __name__=='__main__':main()
