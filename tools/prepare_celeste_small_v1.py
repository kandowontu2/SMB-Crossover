"""Private always-small Celeste source derivative on exact shared4cbd; no native."""
from pathlib import Path
import difflib,hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[1]; B=R/'build'; sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ov=B/'celeste-small-overlay'; assert not ov.exists()
 parent=B/'roster-shared-rcr-adopted-v8.nes'; assert sha(parent)=='4cbd019100ba4dfc51fd9f71c5d3cabd844828eb7d5d2a4aa39413e3579ab39a'
 assert parent.read_bytes()[16+98*8192+0x1dd8:16+99*8192]==b'\xff'*552
 (ov/'src').mkdir(parents=True)
 (ov/'smb1base-mmc5-expanded.cfg').write_bytes((R/'smb1base-mmc5-expanded.cfg').read_bytes())
 patches=[]
 def edit(name,newname,pairs):
  old=(R/'src'/name).read_text(); text=old
  for before,after in pairs: assert text.count(before)==1,(name,before); text=text.replace(before,after)
  (ov/'src'/newname).write_text(text,encoding='utf-8',newline='\n')
  patches.extend(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='a/src/'+name,tofile='b/src/'+newname))
 edit('celeste_mario_core.s','celeste_mario_core_small_host.inc',[
 (' sta PlayerSize               ; native CM starts big; upgrades grant mechanics',' .res 3,$ea                  ; host owns always-small size; preserve zero A/StartedJump'),
 ('.proc CmCollisionBox\n ldy #0\n lda CrouchingFlag\n beq :+\n ldy #2\n:rts\n.endproc','.proc CmCollisionBox\n ldy #1                      ; native small bbox, independent of upgrade/crouch\n rts\n .res 7,$ea                  ; preserve genuine CmBounce and subsequent PCs\n.endproc')])
 edit('celeste_mario_render.s','celeste_mario_render_small_host.inc',[
 ('Select:\n stx CmPose','Select:\n jsr CmSmallPoseSelect')])
 f=ov/'src/celeste_mario_render_small_host.inc'
 with f.open('a',encoding='utf-8',newline='\n') as o:o.write('''
; Host adaptation requested by user: original native small source records only.
; Legal CmGraphics selectors are0..10,22,25. Other original internal indices
; remain unchanged for compatibility;11/24 are not produced by CmGraphics.
.pushseg
.segment "CELESTE_MARIO_CORE"
.assert * = $bdd8,lderror,"Unexpected original Celeste core/art end"
CmSmallPoseStart:
.proc CmSmallPoseSelect
 lda Map,x
 tax
 stx CmPose
 rts
Map:.byte 12,13,14,15,16,17,18,19,20,21,23,11
 .byte 12,13,14,15,16,17,18,19,20,21,22,23,24,23
.endproc
CmSmallPoseEnd:
.assert * <= $c000,lderror,"Celeste small mapper exceeds original core tail"
.popseg
''')
 edit('celeste_mario_host.s','celeste_mario_host.s',[
 (' sta PlayerStatus\n lda #0\n sta PlayerSize',' sta PlayerStatus\n lda #1\n sta PlayerSize'),
 (' ldx #25\n farcall CmGraphics::Select',' ldx #23\n farcall CmGraphics::Select')])
 edit('celeste_mario_host_entry.s','celeste_mario_host_entry.s',[
 ('.include "celeste_mario_core.s"','.include "celeste_mario_core_small_host.inc"'),
 ('.include "celeste_mario_render.s"','.include "celeste_mario_render_small_host.inc"')])
 (ov/'src/entrypoint.s').write_text('.include "build/roster-shared-rcr-adopted-v8-objects/entrypoint.s"\n',encoding='utf-8')
 (B/'celeste_small_v1.patch').write_text(''.join(patches),encoding='utf-8')
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(ov),'--output',str(B/'celeste-small-v1.nes')]
 q=subprocess.run(cmd,cwd=R,capture_output=True,text=True);(B/'celeste_small_build_v1.json').write_text(json.dumps(dict(command=cmd,exit=q.returncode,stdout=q.stdout,stderr=q.stderr),indent=2)+'\n');print(q.stdout,q.stderr);assert q.returncode==0
if __name__=='__main__':main()
