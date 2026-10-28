"""Sparse cold portrait/backdrop successor; preserves every frozen83db input."""
from pathlib import Path
import difflib,hashlib,json,shutil,subprocess,sys
R=Path(__file__).resolve().parents[1];B=R/'build'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 out=B/'celeste-host-visual-v2-overlay';assert not out.exists()
 original=json.loads((B/'celeste_host_handoff.json').read_text())
 for p,h in original['bindings'].items():assert sha(p)==h,('frozen input changed',p)
 (out/'src').mkdir(parents=True)
 shutil.copyfile(B/'celeste-host-overlay/smb1base-mmc5-expanded.cfg',out/'smb1base-mmc5-expanded.cfg')
 (out/'src/entrypoint.s').write_text('.include "build/celeste-host-overlay/src/entrypoint.s"\n',encoding='utf-8')
 before=(R/'src/celeste_mario_host.s').read_text()
 old=' jsr CmHostEnsure\n farcall CmColors,jmp\n.endproc'
 new=' jsr CmHostEnsure\n jmp CmHostAreaColors\n .res 15,$ea                 ; preserve genuine old host entry PCs\n.endproc'
 assert before.count(old)==1
 after=before.replace(old,new)
 marker='.assert * <= $c000,lderror,"Celeste host adapter exceeds audited81BB10 tail"'
 added='''; Cold portrait tail: the real menu/lives producer supplied a native Mario
; record. Select the authenticated Celeste standing record before its consumer.
.proc CmHostPortraitRender
 php
 pha
 phx
 phy
 jsr CmHostEnabled
 bcc Foreign
 jsr CmHostEnsure
 ldx #25
 farcall CmGraphics::Select
 farcall CmDraw
 farcall HpPrepareNativePointers
 ply
 plx
 pla
 plp
 ldx #METASPRITE_SAMUS_BODY
 farcall DrawMetasprite,jmp
Foreign:
 ply
 plx
 pla
 plp
 farcall DrawMetasprite,jmp
.endproc
.proc CmHostAreaColors
 ; Existing native area/background control selects the universal backdrop.
 ldx VRAM_Buffer1_Offset
 cpx #80                    ; four bytes plus terminator must fit84B queue
 bcs Body
 farcall X5QueueAreaBackdrop
Body:
 farcall CmColors,jmp
.endproc
'''
 assert after.count(marker)==1;after=after.replace(marker,added+marker)
 ui=(R/'src/x5_menu_ui.s').read_text();assert ui.count(' farcall DrawMetasprite,jmp')==1
 changed=ui.replace(' farcall DrawMetasprite,jmp',' farcall CmHostPortraitRender,jmp')
 patches=[]
 for name,a,z in [('celeste_mario_host.s',before,after),('x5_menu_ui.s',ui,changed)]:
  (out/'src'/name).write_text(z,encoding='utf-8',newline='\n')
  patches.extend(difflib.unified_diff(a.splitlines(True),z.splitlines(True),fromfile='a/src/'+name,tofile='b/src/'+name))
 (B/'celeste_host_visual_v2.patch').write_text(''.join(patches),encoding='utf-8')
 cmd=[sys.executable,str(R/'tools/build_mmc5_expanded.py'),'--source-overlay',str(out),'--output',str(B/'celeste-host-visual-v2.nes')]
 result=subprocess.run(cmd,cwd=R,text=True,capture_output=True)
 (B/'celeste_host_visual_v2_build.json').write_text(json.dumps(dict(command=cmd,exit=result.returncode,stdout=result.stdout,stderr=result.stderr),indent=2)+'\n',encoding='utf-8')
 print(result.stdout,result.stderr);assert result.returncode==0
 for p,h in original['bindings'].items():assert sha(p)==h,('frozen input changed',p)
if __name__=='__main__':main()
