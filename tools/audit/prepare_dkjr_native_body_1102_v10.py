"""Bounded four-pair native8x16 output from genuine DK source OAM."""
import json,re,subprocess
from pathlib import Path
import prepare_dkjr_native_victim_1102_v9 as P
R=P.R;O=P.O;W=P.W;D=P.D;CURRENT=P.CURRENT;PIN=P.PIN


def main():
    cpu=json.loads((O/'native-victim-v9-CPU.json').read_text());assert cpu['passed']
    for rel,sha in cpu['bindings'].items():assert W.P.sha((R/rel).read_bytes())==sha,rel
    prior=json.loads((O/'native-victim-v9-layout.json').read_text());source=(O/'native-victim-v9.s').read_text().replace('DkjrComponentEnd:\n.export DkjrNativeVictimEnd,DkjrComponentEnd','')
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');native={n:W.address(b,n)for n in ['CurrentOAMOffset','ObjectMetasprite','SmPosePtr','Sprite_Data','GuestOamRotationActive','RgOamRotation']}
    for n,pc in native.items():source='%s=$%04x\n'%(n,pc)+source
    source+='''
.export DkjrNativeDrawBody
DrawBodyResult=$c8fa
; Native CHR publication is a separate, unadmitted port. This leaf expects the
; proven1408B body atlas at sprite pattern1 tiles00..57, exact source palette1
; RGB mapped to native sprite palette3. Four source8x8 vertical pairs become
; four native8x16 cells. No source animation/state is selected here.
DkjrNativeDrawBody:
 php
 pha
 txa
 pha
 tya
 pha
 lda #0
 sta DrawBodyResult
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 ldy CurrentOAMOffset
 jeq BodyDrawDone
 tya
 and #3
 jne BodyDrawDone
 cpy #241
 jcs BodyDrawDone
 lda GuestOamRotationActive
 beq :+
 lda RgOamRotation
 and #3
 jne BodyDrawDone
:
 ldx #0
BodyValidate:
 lda $c210,x
 cmp #240
 jcs BodyDrawDone
 clc
 adc #8
 cmp $c214,x
 jne BodyDrawDone
 lda $c211,x
 cmp #88
 jcs BodyDrawDone
 and #1
 jne BodyDrawDone
 lda $c211,x
 clc
 adc #1
 cmp $c215,x
 jne BodyDrawDone
 lda $c212,x
 cmp $c216,x
 jne BodyDrawDone
 and #$80
 jne BodyDrawDone
 lda $c213,x
 cmp $c217,x
 jne BodyDrawDone
 txa
 clc
 adc #8
 tax
 cpx #32
 bne BodyValidate
 ldx #0
BodyWrite:
 lda $c210,x
 sta Sprite_Data,y
 lda $c211,x
 ora #1
 sta Sprite_Data+1,y
 lda $c212,x
 and #$e0
 ora #3
 sta Sprite_Data+2,y
 lda $c213,x
 sta Sprite_Data+3,y
 iny
 iny
 iny
 iny
 txa
 clc
 adc #8
 tax
 cpx #32
 bne BodyWrite
 sty CurrentOAMOffset
 inc DrawBodyResult
BodyDrawDone:
 lda DrawBodyResult
 beq BodyDrawRejected
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
BodyDrawRejected:
 pla
 tay
 pla
 tax
 pla
 plp
 clc
 rts
DkjrNativeBodyEnd:
DkjrComponentEnd:
.export DkjrNativeBodyEnd,DkjrComponentEnd
'''
    (O/'native-body-v10.s').write_text(source);(O/'native-body-v10.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'native-body-v10.s','-g','-o',O/'native-body-v10.o'],[cc/'ld65.exe','-C',O/'native-body-v10.cfg',O/'native-body-v10.o','-o',O/'native-body-v10.bin','-Ln',O/'native-body-v10.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    blob=(O/'native-body-v10.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-body-v10.lbl').read_text(),re.M)}
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=PIN,component_bytes=len(blob),header_reserved_spare=8160-len(blob),code_SHA256=W.P.sha(blob),labels=labels,native_bindings={**prior['native_bindings'],**native},
        body_sprites=4,body_atlas_bytes=1408,OAM_policy='Four complete pairs only, aligned cursor4..240. Zero/full cursor and insufficient/unaligned capacity reject before OAM writes. Source pair validation precedes all body writes; stable unbanked zeroheader always published to suppress duplicate reservation.',
        additional_live_context=[0xc8fa,0xc8fb],remaining=['Native fullbox/head/side/contact/status/CHR/colors/cold owner/event ingress','Fruit/point/hanging art output and global-hit-freeze nativeAI timing','Full resource/physical carrier/public owner/IRQ/menu/native traversal admission'],
        scope='Unqualified compiled bounded body renderer. No native CHR/palette publication, public Draw caller, physical ROM/menu/shared mutation or actual hardware evidence.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in[Path(__file__),O/'native-victim-v9-CPU.json',O/'native-victim-v9.s',O/'native-body-v10.s',O/'native-body-v10.bin']})
    (O/'native-body-v10-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in['passed','qualified','component_bytes','header_reserved_spare','code_SHA256']}))


if __name__=='__main__':main()
