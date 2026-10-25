from pathlib import Path
import shutil,sys
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'ryu-head-candidate-v3/source';(out/'src').mkdir(parents=True,exist_ok=False)
shutil.copy2(R/'smb1base-mmc5-expanded.cfg',out/'smb1base-mmc5-expanded.cfg');shutil.copy2(R/'src/entrypoint.s',out/'src/entrypoint.s')
sys.path.insert(0,str(R/'tools/audit'))
from check_tmnt_render_oa import load
b=load(D/'food-candidate-v3/candidate.nes');size=int(b['syms']['RyuSourceHeadGate']['size'],0);assert size==771
t=(R/'src/ryu_source_head.s').read_text()
a='''  lda XgJumpUsed
  jeq Native
  lda RgCrouch''';b='''  lda XgJumpUsed
  jeq Native
.if ::ENABLE_MMC5_EXPANDED
  lda RgAttack
  beq NoRetainedAttack
  lda RyuSourceBodyProfile
  cmp #25
  jne Native
NoRetainedAttack:
.endif
  lda RgCrouch''';assert t.count(a)==1;t=t.replace(a,b)
a='  ora CrouchingFlag\n  ora RgAttack\n  ora MmUnderwater';b='''  ora CrouchingFlag
.if !::ENABLE_MMC5_EXPANDED
  ora RgAttack
.endif
  ora MmUnderwater''';assert t.count(a)==1;t=t.replace(a,b)
a='''Prior27:
  tya
  clc
  adc #5''';b='''Prior27:
.if ::ENABLE_MMC5_EXPANDED
  ; An already-running air attack retains its published25px HRect.
  ; Fresh attack transitions keep the existing conservative27 fallback.
  lda RgAttack
  beq OriginalPriorTop
  lda RgAttackAge
  cmp #2
  bcc OriginalPriorTop
  iny
  iny
OriginalPriorTop:
.endif
  tya
  clc
  adc #5''';assert t.count(a)==1;t=t.replace(a,b)
a='''Handled:
  RP_Restore
  lda #0                         ; return no second native head response.
  rts
Native:
  RP_Restore                     ; original tile/query flags/scratch exactly.
  rts
.endproc''';b='''Handled:
.if ::ENABLE_MMC5_EXPANDED
  ; RP_Save owns17stack bytes: saved A/P are SP+16/+17. Share the full
  ; restore tail while returning exactly the old LDA#0 A/N/Z contract.
  ; Every write stays inside this caller's live snapshot, not other RAM.
  tsx
  lda #0
  sta $0110,x
  lda $0111,x
  and #$7f
  ora #2
  sta $0111,x
  jmp Native
.else
  RP_Restore
  lda #0                         ; return no second native head response.
  rts
.endif
Native:
  RP_Restore                     ; original tile/query flags/scratch exactly.
  rts
.if ::ENABLE_MMC5_EXPANDED
  ; The following ROSTER routines and every old public PC remain fixed.
  .res 771-(*-RyuSourceHeadGate),$ea
.endif
.endproc''';assert t.count(a)==1;t=t.replace(a,b)
(out/'src/ryu_source_head.s').write_text(t);print(out)
