"""Private current native fruit-victim adapter; no shared contact/AI mutation."""
import json,re,subprocess
from pathlib import Path
import prepare_dkjr_native_fruit_1102_v8 as P
R=P.R;O=P.O;W=P.W;D=P.D;CURRENT=P.CURRENT;PIN=P.PIN


def main():
    cpu=json.loads((O/'native-fruit-v8-CPU.json').read_text());assert cpu['passed']
    for rel,sha in cpu['bindings'].items():assert W.P.sha((R/rel).read_bytes())==sha,rel
    prior=json.loads((O/'native-fruit-v8-layout.json').read_text());source=(O/'native-fruit-v8.s').read_text()
    lo=source.index('D_d43a:');hi=source.index('D_d56e:',lo);old=source[lo:hi]
    removed=sorted(int(x,16)for x in re.findall(r'^D_([0-9a-f]{4}):',old,re.M));assert all(0xd43a<=pc<0xd55b for pc in removed)
    source=source[:lo]+source[hi:];source=source.replace('DkjrFruitCollision=D_d43a','DkjrFruitCollision=DkjrNativeFruitCollision')
    source=source.replace('DkjrNativeFruitEnd:\nDkjrComponentEnd:\n.export DkjrNativeFruitEnd,DkjrComponentEnd','')
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=CURRENT.read_bytes();assert W.P.sha(raw)==PIN
    native={n:W.address(b,n)for n in ['FloateyNum_Control']}
    for n,pc in native.items():source='%s=$%04x\n'%(n,pc)+source
    source+='''
.export DkjrNativeFruitCollision
; Source fruit rectangle C2DD remains authoritative. Current native victim
; boxes/art/defeat/drop mechanics remain native. Only positive primary ordinary
; enemies00..14, excluding Podoboo0C, are admitted; bosses/platforms/pickups and
; secondary/self-secondary records are rejected. No victim flag is stolen.
DkjrNativeFruitCollision:
 lda $c08c
 jne VictimActiveFruit
 lda #0
 sta $c068
 rts
VictimActiveFruit:
 lda $c230
 sta $c001
 lda $c233
 sta $c000
 lda #<DData_c2dd
 sta $c002
 lda #>DData_c2dd
 sta $c003
 jsr DkjrRect
 php
 txa
 pha
 tya
 pha
 ldx #7
VictimSaveScratch:
 lda R0,x
 pha
 dex
 bpl VictimSaveScratch
 lda ObjectOffset
 pha
 ldx #32
VictimSaveSMC:
 lda $015a,x
 pha
 dex
 bpl VictimSaveSMC
 ldx #5
VictimLoop:
 lda Enemy_Flag,x
 jeq VictimNext
 jmi VictimNext
 lda Enemy_State,x
 and #$a0
 jne VictimNext
 lda Enemy_ID,x
 cmp #$15
 jcs VictimNext
 cmp #$0c
 jeq VictimNext
 lda Enemy_Y_HighPos,x
 cmp #1
 jne VictimNext
 stx ObjectOffset
 jsr NativeOffscreen
 jsr NativeRelative
 ldx ObjectOffset
 jsr NativeVictimBBox
 ldx ObjectOffset
 txa
 clc
 adc #1
 asl
 asl
 tay
 lda BoundingBox_UL_Corner,y
 cmp #$ff
 jeq VictimNext
 cmp BoundingBox_UL_Corner+2,y
 bcc :+
 jne VictimNext
:
 lda BoundingBox_UL_Corner+1,y
 cmp BoundingBox_UL_Corner+3,y
 bcc :+
 jne VictimNext
:
 lda $c040
 cmp BoundingBox_UL_Corner,y
 jcc VictimNext
 lda BoundingBox_UL_Corner+2,y
 cmp $c03e
 jcc VictimNext
 lda $c041
 cmp BoundingBox_UL_Corner+1,y
 jcc VictimNext
 lda BoundingBox_UL_Corner+3,y
 cmp $c03f
 jcc VictimNext
 ; Snapshot only the source hit-effect origin. Native victim art is never
 ; copied into private CHR/OAM or replaced with a donor enemy sprite.
 lda Enemy_Y_Position,x
 sta $c2c0
 lda Enemy_X_Position,x
 sec
 sbc ScreenLeft_X_Pos
 sta $c2c3
 jsr NativeVictimDefeat
 ldx ObjectOffset
 lda #0
 sta FloateyNum_Control,x
 sta $c069
 lda #1
 sta $c068
 jmp VictimRestore
VictimNext:
 dex
 jpl VictimLoop
 lda #0
 sta $c068
VictimRestore:
 ldx #0
VictimRestoreSMC:
 pla
 sta $015a,x
 inx
 cpx #33
 bne VictimRestoreSMC
 pla
 sta ObjectOffset
 ldx #0
VictimRestoreScratch:
 pla
 sta R0,x
 inx
 cpx #8
 bne VictimRestoreScratch
 pla
 tay
 pla
 tax
 plp
 lda $c068
 rts
'''
    calls=[]
    for label,name in [('NativeVictimBBox','GetEnemyBoundBox'),('NativeVictimDefeat','ShellOrBlockDefeat')]:
        pc=W.address(b,name);pos=W.location(b,name);bank=((pos-16)//8192)|128;assert raw[pos:pos+32]==b['raw'][pos:pos+32]
        source+='\n%s:\n lda #$%02x\n sta FarcallJmpTarget_SMC+1\n lda #$%02x\n sta FarcallJmpTarget_SMC+2\n lda #$%02x\n jmp FarCallCommon\n'%(label,pc&255,pc>>8,bank)
        calls.append(dict(target=name,CPU_address=pc,physical_bank=bank&127,file_offset=pos,first32_SHA256=W.P.sha(raw[pos:pos+32]),unchanged_from_full_metadata_base=True))
    source+='DkjrNativeVictimEnd:\nDkjrComponentEnd:\n.export DkjrNativeVictimEnd,DkjrComponentEnd\n'
    (O/'native-victim-v9.s').write_text(source);(O/'native-victim-v9.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'native-victim-v9.s','-g','-o',O/'native-victim-v9.o'],[cc/'ld65.exe','-C',O/'native-victim-v9.cfg',O/'native-victim-v9.o','-o',O/'native-victim-v9.bin','-Ln',O/'native-victim-v9.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    blob=(O/'native-victim-v9.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-victim-v9.lbl').read_text(),re.M)}
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=PIN,component_bytes=len(blob),header_reserved_spare=8160-len(blob),code_SHA256=W.P.sha(blob),labels=labels,native_bindings={**prior['native_bindings'],**native},native_victim_calls=calls,
        source_funding_removed_original_range=[0xd43a,0xd55b],original_instruction_labels_removed=len(removed),original_player_movement_jump_vine_fruit_touch_fall_hit_unchanged=True,
        native_hit_adapter='Ordinary current native positive victim box vs original fruit rect; actual nativeShellOrBlockDefeat once, native100/200 popup disabled because originalED44 supplies source800/1200/1600 later. Original source400 release and hit animation remain.',
        remaining=['Native OAM/CHR/palette/status','Original global hit-freeze vs host enemy AI timing policy; current native enemies continue unless a future owned native gate implements source freeze','Full public owner/cold/contacts/IRQ/resources/native stage traversal'],
        scope='Unqualified compiled private native victim successor. No new shared contact/AI/birth hook, physical resource, menu admission or ROM mutation.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in[Path(__file__),O/'native-fruit-v8-CPU.json',O/'native-fruit-v8.s',O/'native-victim-v9.s',O/'native-victim-v9.bin']})
    (O/'native-victim-v9-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','qualified','component_bytes','header_reserved_spare','code_SHA256']}))


if __name__=='__main__':main()
