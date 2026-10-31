"""Correct genuine Only-service index17; service2 remains byte-exact gameplay."""
from pathlib import Path
import re
P=Path(__file__).with_name('prepare_ff_cold_preview_v1.py');s=P.read_text()
s=s.replace("O=R/'build/ff-cold-preview-v1'","O=R/'build/ff-cold-preview-v3'")
a=s.index(" code='''");z=s.index("'''\n assert s.count(needle)",a)
code=''' code=\'\'\'.import FwPreviewPublish,DrawMetasprite
.export FwPortraitDraw
; Genuine Only-service17 is the actual title/lives DRAW callback. Service3
; already built SmPosePtr/body0, and HpPrepareNativePointers took its snapshot.
FwPortraitDraw:
 php
 pha
 txa
 pha
 tya
 pha
 jsr FwPreviewPublish
 pla
 tay
 pla
 tax
 pla
 plp
 sta SafecallA_SMC+1
 lda #<DrawMetasprite
 sta FarcallJmpTarget_SMC+1
 lda #>DrawMetasprite
 sta FarcallJmpTarget_SMC+2
 lda #.lobyte(.bank(DrawMetasprite)|$80)
 jmp FarCallCommon
 .assert *-FwPortraitDraw<=52,error,"OWN retired FF two-gate span"
 .res 52-(*-FwPortraitDraw),$ea'''
s=s[:a]+code+s[z:]
s=s.replace("s=old.replace('.import FwHostDrawShots','.import FwDrawDispatch')","s='.import FwPortraitDraw\\n'+old")
s=s.replace("assert s.count(' jmp FwHostDrawShots')==1;s=s.replace(' jmp FwHostDrawShots',' jmp FwDrawDispatch')", "a='; 17 MenuPortrait typed_source_gate_only\\n jmp FwPortrait';assert s.count(a)==1;s=s.replace(a,a.replace('jmp FwPortrait','jmp FwPortraitDraw'))")
s=s.replace("if v in[str(P/'joint'/n)for n in['loader.o'", "if v==str(P/'joint/main.o'):link[i]=str(R/'build/ff-cold-preview-v2/joint/main.o')\n  if v in[str(P/'joint'/n)for n in['loader.o'")
s=s.replace("location(b,'FwServiceVeneers')+6,location(b,'FwServiceVeneers')+9","location(b,'FwServiceVeneers')+51,location(b,'FwServiceVeneers')+54")
s=s.replace("'FwDrawDispatch'","'FwPortraitDraw'").replace('only52B_owned_alias_and_service2_operands','only52B_owned_alias_and_service17_operands')
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(Path(__file__).resolve())))
