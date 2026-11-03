"""Private source rectangle and real native CHR/palette services; no ROM write."""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;W=A.W


def main():
    proof=json.loads((O/'native-vector-v23-CPU.json').read_text());assert proof['passed']
    prior=json.loads((O/'native-vector-v22-layout.json').read_text());source=(O/'native-vector-v22.s').read_text();b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=A.BASE.read_bytes();assert A.sha(raw)==A.PIN
    targets={int(i):name for i,name in prior['implemented_vector_rows'].items()};targets.update({1:'DkGraphics',3:'DkGraphics',16:'DkFullBox',26:'DkColors',32:'DkColors'})
    start=source.index('DkServices:\n');end=start+len('DkServices:\n');lines=source[end:].splitlines(True);assert all(line.startswith(' jmp ')for line in lines[:38])
    source=source[:end]+''.join(' jmp '+targets.get(i,'DkUnavailable')+'\n'for i in range(38))+''.join(lines[38:])
    names=['BoundingBox_UL_Corner','SmPosePtr','ObjectMetasprite','VRAM_Buffer1','VRAM_Buffer1_Offset']
    defined=set(re.findall(r'^(\w+)=',source,re.M))
    source=''.join(n+'=$%04x\n'%W.address(b,n)for n in names if n not in defined)+source
    for n in ['X5SetPhysicalChr','X5QueueAreaBackdrop']:
        source+=n+'=$%04x\nBank_%s=$%02x\n'%(W.address(b,n),n,((W.location(b,n)-16)//8192)|128)
    source+='''
.segment "DK_PORTS"
.export DkGraphics,DkFullBox,DkColors,DkNativePortsEnd
; The native collision cache uses the donor's actual state/facing/grip
; rectangle, distinct from the32px rendered body and native terrain probes.
DkFullBox:
 lda $c8fe
 beq DkPortNo
 jsr DkjrBounds
 ldx #3
DkFullBoxCopy:
 lda $c5fc,x
 sta BoundingBox_UL_Corner,x
 dex
 bpl DkFullBoxCopy
 sec
 rts
DkPortNo:
 clc
 rts
; All8x16 source body tiles use pattern1; native enemy pattern0 is retained.
;959 holds32body pairs,960 prefix holds12body pairs.961's legal art prefix
;is reserved for fruit/hit; its executable tail is outside legal tile indices.
DkGraphics:
 ldy #4
DkGraphicsNext:
 tya
 sec
 sbc #4
 tax
 lda DkChrPages,x
 ldx #3
 jsr DkSetChr
 iny
 cpy #8
 bcc DkGraphicsNext
 lda #0
 sta ObjectMetasprite
 lda #<ObjectMetasprite
 sta SmPosePtr
 lda #>ObjectMetasprite
 sta SmPosePtr+1
 lda #0
 sec
 rts
DkChrPages:.byte $bf,$c0,$c1,$c1
DkSetChr:
 sta SafecallA_SMC+1
 lda #<X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+1
 lda #>X5SetPhysicalChr
 sta FarcallJmpTarget_SMC+2
 lda #Bank_X5SetPhysicalChr
 jmp FarCallCommon
; Preserve caller AXYP except handled carry. Native area remains sole
; universal/backdrop owner. Only opaque sprite RGB writes are owned here.
DkColors:
 php
 pha
 txa
 pha
 tya
 pha
 ldx VRAM_Buffer1_Offset
 cpx #62
 bcs DkColorsDone
 lda #<X5QueueAreaBackdrop
 sta FarcallJmpTarget_SMC+1
 lda #>X5QueueAreaBackdrop
 sta FarcallJmpTarget_SMC+2
 lda #Bank_X5QueueAreaBackdrop
 jsr FarCallCommon
 ldx VRAM_Buffer1_Offset
 ldy #0
DkColorsCopy:
 lda DkColorPackets,y
 sta VRAM_Buffer1,x
 inx
 iny
 cpy #18
 bcc DkColorsCopy
 stx VRAM_Buffer1_Offset
 lda #0
 sta VRAM_Buffer1,x
DkColorsDone:
 pla
 tay
 pla
 tax
 pla
 plp
 sec
 rts
DkColorPackets:
 .byte $3f,$1d,3,$30,$06,$36
 .byte $3f,$19,3,$30,$2a,$16
 .byte $3f,$15,3,$2a,$17,$37
DkNativePortsEnd:
'''
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-display-pause-v24.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-display-main-v24.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-display-ports-v24.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    body,L=A.assemble('native-display-v24',source,cfg);parts={kind:(O/('native-display-'+kind+'-v24.bin')).read_bytes()for kind in ['pause','main','ports']}
    assert len(body)==8036 and parts['pause']==(O/'native-vector-pause-v22.bin').read_bytes()and parts['main']==(O/'native-vector-main-v22.bin').read_bytes()
    out=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,compiled_body_bytes=len(body),body_end=L['DkjrComponentEnd'],header_spare=8160-len(body),metadata_ports_bytes=len(parts['ports']),metadata_ports_span=[0xd6a4,L['DkNativePortsEnd']],metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],labels=L,implemented_vector_rows={str(k):v for k,v in targets.items()},unimplemented_rows=[i for i in range(38)if i not in targets],
        original_palette=dict(body=[15,48,6,54],fruit0=[15,48,42,22],fruit2=[15,42,23,55]),
        native_imports=[dict(name=n,PC=W.address(b,n),physical_PRG=(W.location(b,n)-16)//8192,first16bytes=raw[W.location(b,n):W.location(b,n)+16].hex())for n in ['X5SetPhysicalChr','X5QueueAreaBackdrop']],
        remaining=['CPU original bounds/CHR modes/palette VRAM packet proof and actual full native ingresses.','Final all-art reader closure/native fruit/hit/points OAM, header/cookie physical packing and unfinished typed policies/lifecycle.','Latest Prince/Bub fingerprint rebind, all shared/public/IRQ grants and actual native qualification.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,O/'native-vector-v22.s',O/'native-vector-v23-CPU.json',O/'native-display-v24.s',O/'native-display-v24.bin',O/'native-display-main-v24.bin',O/'native-display-pause-v24.bin',O/'native-display-ports-v24.bin']})
    (O/'native-display-v24-layout.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:out[k]for k in ['passed','compiled_body_bytes','header_spare','metadata_ports_bytes','metadata_end','metadata_spare','implemented_vector_rows']}))


if __name__=='__main__':main()
