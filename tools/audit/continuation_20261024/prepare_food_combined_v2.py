from pathlib import Path
import shutil
R=Path('C:/Users/kando/Documents/ChatGPT/SMB Crossover');D=Path(__file__).resolve().parent;out=D/'food-candidate-v2/source';shutil.copytree(D/'wave-candidate-v1/source',out)
for name in ['chip_dale_health.s','chip_dale_dispatch.s']:shutil.copy2(R/'src'/name,out/'src'/name)
p=out/'src/chip_dale_health.s';t=p.read_text();old=''' lda #0
 sta PlayerStatus
 sec
 rts
No:clc''';assert t.count(old)==1
t=t.replace(old,''' jsr CdNextFoodStatus
 nop
 nop
 sec
 rts
No:clc''');p.write_text(t)
p=out/'src/chip_dale_dispatch.s';p.write_text(p.read_text()+'''
; SMB's health-food appearance is independent of Rescue Rangers' three HP.
; Advance from the collected type, so normal blocks expose both real foods.
.pushseg
.segment "CD_LOGIC"
.proc CdNextFoodStatus
 lda PowerUpType,x
 eor #1
 sta PlayerStatus
 lda #0 ; Preserve the old collection leaf's A/N/Z; carry is set by its caller.
 rts
.endproc
.popseg
''')
