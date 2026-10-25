"""Install private equal-span native hooks, retaining original resident PCs."""
from pathlib import Path
import subprocess, sys
R=Path(__file__).resolve().parents[2]
S=R/'build/verification/crossover-helpers-jb/source'
def main():
    p=S/'src/game.s';t=p.read_text();begin=t.index('.proc PauseRoutine');end=t.index('.endproc',begin)+len('.endproc')
    original=t[begin:end]
    assert 'HpPauseCold' not in original
    (S/'src/native_helper_pause.s').write_text('.pushseg\n.segment "CROSSOVER_HELPERS"\n'+original.replace('.proc PauseRoutine','.proc HpPauseCold')+'\n.popseg\n')
    new='''.if ::ENABLE_CROSSOVER
HpResidentBegin:
.proc PauseRoutine
  farcall HpPauseCold
  rts
.endproc
.proc HpGraphicsBankCopy
  ; A is dead at the original DrawAll entry; native SMC farcall ABI.
  lda #<HpPrepareNativePointers
  SMC_StoreLowByte FarcallJmpTarget,a
  lda #>HpPrepareNativePointers
  SMC_StoreHighByte FarcallJmpTarget,a
.if ::MAPPER_MMC5
  lda #.bank(HpPrepareNativePointers) | MMC5_PRG_ROM
.else
  lda #.bank(HpPrepareNativePointers)
.endif
  jsr FarCallCommon
  jmp CrossoverGraphicsBank
.endproc
.proc HpProcessFireballsBridge
  jsr ProcFireball_Bubble
  lda HpCount
  beq Done
  farcall HpSpawnAndTrack
Done:
  rts
.endproc
.assert *-HpResidentBegin<=68,error,"Original PauseRoutine resident span"
.res 68-(*-HpResidentBegin),$ea
.else
'''+original+'\n.endif'
    t=t[:begin]+new+t[end:]
    assert t.count('    jsr ProcFireball_Bubble    ')==1
    t=t.replace('    jsr ProcFireball_Bubble    ','.if ::ENABLE_CROSSOVER\n    jsr HpProcessFireballsBridge\n.else\n    jsr ProcFireball_Bubble\n.endif\n    ; ')
    assert t.count('  farcall GetAreaDataAddrs     ')==1
    t=t.replace('  farcall GetAreaDataAddrs     ','.if ::ENABLE_CROSSOVER\n  farcall HpLoadArea\n.else\n  farcall GetAreaDataAddrs\n.endif\n  ; ')
    p.write_text(t)
    p=S/'src/object.s';t=p.read_text()
    assert t.count('        jsr LargePlatformBoundBox')==1
    t=t.replace('        jsr LargePlatformBoundBox','.if ::ENABLE_CROSSOVER\n        jsr HpNativePlatformBBoxGate\n.else\n        jsr LargePlatformBoundBox\n.endif')
    begin=t.index('LargePlatformSubroutines:\n');end=t.index(';-------------------------------------------------------------------------------------',begin)
    old=t[begin:end]
    t=t[:begin]+'''.if ::ENABLE_CROSSOVER
LargePlatformSubroutines:
  farcall HpNativePlatformDispatch
  rts
  .res 22-(*-LargePlatformSubroutines),$ea
.else
'''+old+'.endif\n\n'+t[end:]
    p.write_text(t)
    subprocess.run([sys.executable,str(R/'build/player-guide-agent/platform-axis-private/patch_native16_v2.py'),'--source',str(S)],check=True)
if __name__=='__main__':main()
