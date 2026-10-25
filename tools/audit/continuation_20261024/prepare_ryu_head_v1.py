from pathlib import Path
import shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'ryu-head-candidate-v1/source';out.mkdir(parents=True,exist_ok=False);(out/'src').mkdir();shutil.copytree(R/'cfg',out/'cfg')
p=out/'src/ryu_source_head.s';t=(R/'src/ryu_source_head.s').read_text();a='  ora CrouchingFlag\n  ora RgAttack\n  ora MmUnderwater';b='''  ora CrouchingFlag
.if ::ENABLE_MMC5_EXPANDED
  ; An airborne sword attack retains the cached source25px body.
  jsr RyuAttackHeadMix
.else
  ora RgAttack
.endif
  ora MmUnderwater''';assert t.count(a)==1;p.write_text(t.replace(a,b))
t=(R/'src/entrypoint.s').read_text();t+='''
; Append after every existing ROSTER contributor; old symbol PCs stay fixed.
.if ::ENABLE_MMC5_EXPANDED
.include "ryu_attack_head_mix.inc"
.endif
''';(out/'src/entrypoint.s').write_text(t)
(out/'src/ryu_attack_head_mix.inc').write_text('''; Only a published retained25px source body can bypass the attack fallback.
; The caller already excludes crouch/hurt/wall/water/platform/special states
; and proves the previous source head was below this very ceiling.
; Y/C are scratch until the next CMP/TAY; RP_Restore restores full query state.
.pushseg
.segment "ROSTER"
.proc RyuAttackHeadMix
 ldy RyuSourceBodyProfile
 cpy #25
 beq Done
 ora RgAttack
Done:rts
.endproc
.assert * <= $c000,error,"Ryu head mixer must fit existing ROSTER slack"
.export RyuAttackHeadMix
.popseg
''')
print(out)
