"""Remove private service register saves from the deepest native stack."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    prior=json.loads((O/'native-defeat-v45-layout.json').read_text());negative=json.loads((O/'native-service-v47-IRQ-negative.json').read_text())
    assert not negative['passed']and negative['minimum_ISR_SP']==119
    source=(O/'native-defeat-v45.s').read_text()
    old='''DkjrNativeAwardSourcePoints:
 php
 pha
 txa
 pha
 tya
 pha'''
    new='''DkjrNativeAwardSourcePoints:
 sta $c4b4
 stx $c4b5
 sty $c4b6
 php
 pla
 sta $c4b7'''
    assert source.count(old)==1;source=source.replace(old,new)
    old='''AwardReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts'''
    new='''AwardReturn:
 lda $c4b7
 pha
 ldx $c4b5
 ldy $c4b6
 lda $c4b4
 plp
 rts'''
    assert source.count(old)==1;source=source.replace(old,new)
    old=''' jsr DkjrRect
 php
 txa
 pha
 tya
 pha
 ldx #7
VictimSaveScratch:'''
    new=''' jsr DkjrRect
 stx $c4b8
 sty $c4b9
 php
 pla
 sta $c4ba
 ldx #7
VictimSaveScratch:'''
    assert source.count(old)==1;source=source.replace(old,new)
    old=''' pla
 tay
 pla
 tax
 plp
 lda $c068
 rts'''
    new=''' lda $c4ba
 pha
 ldx $c4b8
 ldy $c4b9
 plp
 lda $c068
 rts'''
    assert source.count(old)==1;source=source.replace(old,new)
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-registers-pause-v48.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-registers-main-v48.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-registers-ports-v48.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-registers-v48',source,cfg);assert len(blob)==prior['body_bytes']+28 and L['DkPauseThaw']==0xd60c
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),private_service_packet_extent=[0xc460,0xc4bb],register_frames=dict(score=dict(A=0xc4b4,X=0xc4b5,Y=0xc4b6,P=0xc4b7),victim=dict(X=0xc4b8,Y=0xc4b9,P=0xc4ba)),
        scope='Seven private register-save bytes append to dedicated native service packets inside the granted conditional state. Only one transient PHP/PLA or PHA/PLP is used; original source/native register/flag return semantics remain unchanged. Deep actual NMI and full continuation must be requalified.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-defeat-v45.s',O/'native-service-v47-IRQ-negative.json',O/'native-registers-v48.s',O/'native-registers-v48.bin']})
    (O/'native-registers-v48-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','private_service_packet_extent']}))


if __name__=='__main__':main()
