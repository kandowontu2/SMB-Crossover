"""Source-fund Karnov's real shared ingress without altering legacy arithmetic."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[2]
O=R/'build/karnov-host-resource-base-1101-v1'
PHYS=R/'build/bt-ready-menu-1031-v2/joint/src/megaman_physics.s'
UNION=R/'build/hogan-thomas-current/union.s'
RECIPE=R/'build/hogan-thomas-current/union-build.json'

def once(t,a,b):
    assert t.count(a)==1,(a,t.count(a));return t.replace(a,b)

def prepare(resident,write):
    physics=PHYS.read_text()
    old='''ProductHi:
  .repeat 256,I
    .byte .bankbyte(I * Factor)
  .endrepeat'''
    new='''; Only this table is relocated, intact, inside the same physical bank.
.if .xmatch({Name},{MarioWaterCoast})
  .assert Factor=62344,error,"Exact source coast factor"
ProductHi=::KrMarioWaterProductHi
  .assert *=$b38e,lderror,"Original coast table extent moved"
  .res $72,$ff
::KrServiceVeneers:
  .repeat 36
    jmp ::KrDispatch
  .endrepeat
  .res $22,$ff
  .assert *=$b48e,lderror,"Coast source swap changed original extent"
.else
'''+old+'\n.endif'
    physics=once(physics,old,new);write(O/'megaman_physics.s',physics)
    resident=once(resident,'KrSelected:\n lda SelectedCharacter\n','KrSelected:\n lda SelectedCharacter\n cmp #34\n beq KrSelectedYes\n')
    resident=once(resident,' and #1\n beq KrSelectedNo\n sec',' and #1\n beq KrSelectedNo\nKrSelectedYes:\n sec')
    resident=once(resident,'KrServiceVeneers:\n.repeat 36\n jmp KrDispatch\n.endrepeat','; The genuine service rows now live at B400 in the source-funded table swap.')
    resident=once(resident,'KrResidentEnd:', '''; Preserve the low address byte so every indexed table read has exactly
; the same page-crossing cycle behavior as the original Mario water routine.
.align 256,$ff
.export KrMarioWaterProductHi
KrMarioWaterProductHi:
.assert <KrMarioWaterProductHi=$8e,lderror,"Exact native indexed table low address"
.repeat 256,I
 .byte .bankbyte(I*62344)
.endrepeat
KrResidentEnd:''')
    union=UNION.read_text();union='.import KrServiceVeneers\n'+union
    old=''' ldy #0
 jmp HuCommon
 .res 5,$ff'''
    union=once(union,old,''' ldy #0
 jmp HuCommon
::HuQClass:
 cmp #25
 jmp HuS2Decide''')
    old=''' ldy #35
 jmp HuCommon
 .res 5,$ff'''
    union=once(union,old,''' ldy #35
 jmp HuCommon
::KrUnionBank:
 lda #.lobyte(.bank(KrServiceVeneers)|$80)
 jmp ThFFBankReady''')
    union=once(union,'::HuGenericIndex:\n lda SelectedCharacter\n cmp #10','::HuGenericIndex:\n lda SelectedCharacter\n cmp #34\n beq KrUnionBank\n cmp #10')
    union=once(union,'ThForeign:\n::HuQClass:\n cmp #25\n jmp HuS2Decide','ThForeign:\n jmp HuQClass')
    # Bring the existing BT transport into branch range. Its selector reaches
    # this point only after CMP #30 was not equal, so BNE replaces JMP exactly.
    union=once(union,' cmp #30\n beq Fetch\n jmp HuExtendedBT',' cmp #30\n beq Fetch\n bne HuExtendedBT')
    start=union.index('HuExtendedBT:\n');end=union.index('.assert *<=$ba54',start)
    transport=union[start:end];union=union[:start]+union[end:]
    union=once(union,'\nHuLo:\n','\n'+transport+'HuLo:\n')
    union+='\n.assert <KrServiceVeneers=0,lderror,"Shared zero-low service transport"\n.assert >KrServiceVeneers=>FwServiceVeneers,lderror,"Shared real B400 high transport"\n'
    write(O/'union.s',union)
    command=json.loads(RECIPE.read_text())['command'][:]
    for flag,name in [('-o','union.o'),('--create-full-dep','union.dep'),('--create-dep','union.dep'),('-l','union.lst')]:
        if flag in command:command[command.index(flag)+1]=str(O/name)
    command[-1]=str(O/'union.s');command[1:1]=['-I',str(O)]
    return resident,command,[Path(__file__),PHYS,UNION,RECIPE,O/'megaman_physics.s',O/'union.s']
