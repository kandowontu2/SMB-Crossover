"""Private Celeste small-body CHR window ownership successor on frozen d52."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ov=B/'celeste-small-chr-overlay';assert not ov.exists();(ov/'src').mkdir(parents=True)
 parent=B/'celeste-small-v1.nes';assert sha(parent)=='d52eeefe78c5f050d276a833c651456b717157856d1783b98c131f9da29f8a60'
 assert parent.read_bytes()[16+98*8192+0x1dfa:16+99*8192]==b'\xff'*(0xc000-0xbdfa)
 old=(B/'celeste-small-overlay/src/celeste_mario_render_small_host.inc').read_text();s=old
 before=' cpy #4\n bne Loop\n lda #1\n sta X5WideChrActive\n rts\n.endproc';after=' cpy #1                      ; small source records only use sprite window0\n bne Loop\n jmp CmSmallChrDrawDone\n .res 3,$ea                  ; preserve every following original entry PC\n.endproc'
 assert s.count(before)==1;s=s.replace(before,after)
 s+='''
.pushseg
.segment "CELESTE_MARIO_CORE"
.assert * = $bdfa,lderror,"Expected frozen small mapper end"
CmSmallChrStart:
.proc CmSmallChrDrawDone
 ; Preserve the complete original CmDraw scratch/register/flag contract.
 inc CmTemp
 inc CmTemp
 inc CmTemp
 ldy #4
 lda #1
 sta X5WideChrActive
 rts
.endproc
CmSmallChrEnd:
.assert * <= $c000,lderror,"Celeste CHR ownership tail overflow"
.popseg
'''
 (ov/'src/celeste_mario_render_small_host.inc').write_text(s,encoding='utf-8',newline='\n')
 (ov/'smb1base-mmc5-expanded.cfg').write_bytes((B/'celeste-small-overlay/smb1base-mmc5-expanded.cfg').read_bytes())
 (ov/'src/entrypoint.s').write_text('.include "build/roster-shared-rcr-adopted-v8-objects/entrypoint.s"\n',encoding='utf-8')
 (B/'celeste_small_chr_v1.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),s.splitlines(True),fromfile='a/src/celeste_mario_render_small_host.inc',tofile='b/src/celeste_mario_render_small_host.inc')),encoding='utf-8')
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(ov),'--output',str(B/'celeste-small-chr-v1.nes')]
 q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_small_chr_build_v1.json').write_text(json.dumps(dict(command=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr),indent=2)+'\n');print(q.stdout,q.stderr);assert q.returncode==0
if __name__=='__main__':main()
