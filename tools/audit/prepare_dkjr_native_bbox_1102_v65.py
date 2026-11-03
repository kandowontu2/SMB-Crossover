"""Current-anchor transport for original D2BD, plus ungranted37B gate proposal."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R,O,W=A.R,A.O,A.W


def main():
    prior=json.loads((O/'native-items-v60-layout.json').read_text());source=(O/'native-items-v60.s').read_text()
    old=''' jsr DkjrBounds
 ldx #3
DkFullBoxCopy:
 lda $c5fc,x
 sta BoundingBox_UL_Corner,x
 dex
 bpl DkFullBoxCopy
 sec
 rts'''
    new=''' jsr DkjrBounds
 ; Original D2BD determines all four source offsets. Transport that shape
 ; from the cached donor OAM origin to the current native world/camera and
 ; anchor, exactly as the native body renderer transports the same pixels.
 ; WLeft/WTop are existing synchronous adapter scratch, never donor state.
 lda Player_X_Position
 sec
 sbc ScreenLeft_X_Pos
 sec
 sbc #8
 sec
 sbc $c213
 sta WLeft
 lda Player_Y_Position
 clc
 adc #15
 sec
 sbc $c210
 sta WTop
 ldx #3
DkFullBoxCopy:
 txa
 and #1
 asl
 tay
 lda $c5fc,x
 clc
 adc WLeft,y
 sta BoundingBox_UL_Corner,x
 dex
 bpl DkFullBoxCopy
 ldx #0
 ldy #0
 sec
 rts'''
    assert source.count(old)==1;source=source.replace(old,new)
    cfg=(O/'native-items-v60.cfg').read_text().replace('native-items-','native-bbox-').replace('-v60.bin','-v65.bin')
    blob,L=A.assemble('native-bbox-v65',source,cfg)
    assert len(blob)==prior['body_bytes'] and L['DkPauseThaw']==0xd60c and L['DkNativePortsEnd']<=0xd800
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    gate='''.setcpu "6502"
.segment "DK_BBOX_GATE"
.export DkBBoxGate,DkBBoxFallback,DkBBoxExtended,DkBBoxGateEnd
DkBBoxGate:
 php
 lda SelectedCharacter
 cmp #36
 beq DkBBoxExtended
 ; CMP36 leaves C=1 for39/40. For values<36 its borrow makes the result
 ; at least216;37/38 becomeFE/FF. Only39/40 produce0/1 below2.
 sbc #39
 cmp #2
 bcc DkBBoxExtended
 plp
DkBBoxFallback:
 jmp BoundingBoxCore
DkBBoxExtended:
 plp
 lda #<HuFullBox
 sta FarcallJmpTarget_SMC+1
 lda #>HuFullBox
 sta FarcallJmpTarget_SMC+2
 lda #$cf
 jsr FarCallCommon
 bcc DkBBoxFallback
 rts
DkBBoxGateEnd:
'''
    gate='\n'.join(n+'=$%04x'%W.address(b,n)for n in ['SelectedCharacter','BoundingBoxCore','HuFullBox','FarcallJmpTarget_SMC','FarCallCommon'])+'\n'+gate
    g,GL=A.assemble('native-bbox-gate-v65',gate,'MEMORY{C:start=$add8,size=38,file=%O;}SEGMENTS{DK_BBOX_GATE:load=C,type=ro;}')
    assert len(g)==37 and GL['DkBBoxGateEnd']==0xadfd
    offset=16+65*8192+0xadd8-0xa000;oldgate=A.BASE.read_bytes()[offset:offset+38]
    assert oldgate.hex()=='08ad0260c924f008c927f004284c4e9f28a9008d6c01a9b78d6d01a9cf205a01b0034c4e9f60'
    q=dict(prior);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),
        metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],
        fullbox_transport=dict(original_dimensions='unmodified D2BD original pose/facing/grip',native_prefix_X='worldX-camera-8',native_prefix_Y='anchorY+15',cached_origin=[0xc213,0xc210],existing_adapter_scratch=[0xc8e8,0xc8ea],native_return_XY=[0,0]),
        ungranted_shared_gate_proposal=dict(physical_PRG=65,CPU_half_open=[0xadd8,0xadfd],file_offset=offset,
            old_hex=oldgate[:37].hex(),new_hex=g.hex(),old_source_extent=[0xadd8,0xadfe],old_bytes=38,new_bytes=37,
            old_ADFD_RTS_preserved=True,new_allocated_bytes=0,admitted_raw_set=[36,39,40],grant_required=True),
        scope='Compiled private original-shape/current-anchor transport, no donor actor writes beyond genuine D2BD. Separate source-funded37B native gate is proposal only, never written to ROM/shared source; its fullforeign/source/lifetime/IRQ proof and root grant remain required.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-items-v60.s',O/'native-bbox-v65.s',O/'native-bbox-v65.bin',O/'native-bbox-ports-v65.bin',O/'native-bbox-gate-v65.s',O/'native-bbox-gate-v65.bin',R/'tools/audit/prepare_bubble_bobble_native_proxy_1102_v5.py']})
    (O/'native-bbox-v65-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in['passed','body_bytes','header_spare','metadata_end','metadata_spare','ungranted_shared_gate_proposal']}))


if __name__=='__main__':main()
