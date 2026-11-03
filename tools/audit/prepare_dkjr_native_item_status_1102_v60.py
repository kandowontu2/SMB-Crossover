"""Private native item/status contracts; no shared raw40 gate admission."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R,O,W=A.R,A.O,A.W


def main():
    previous=json.loads((O/'native-scoretail-v54-layout.json').read_text())
    assert json.loads((O/'native-score-tail-v59.json').read_text())['passed']
    source=(O/'native-scoretail-v54.s').read_text()
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    names=['InvPickupOwner','InvPickup','InvRisePhase','InvPickupSaveLo','InvPickupSaveHi','PowerUpType']
    source='\n'.join(n+'=$%04x'%W.address(b,n)for n in names)+'\n'+source
    pc,collector_at=W.address(b,'MarioSourcePowerupCollision'),W.location(b,'MarioSourcePowerupCollision')
    assert A.BASE.read_bytes()[collector_at:collector_at+32]==b['raw'][collector_at:collector_at+32]
    bank=((collector_at-16)//8192)|128
    leaves='''
.export DkNativePrepare,DkNativeMature,DkNativePickup,DkNativeStatusName
; Genuine native item metadata, matching NrPrepare::Own. Donor DK Jr has
; no private weapon inventory. Only legal native primary slots0..5 are typed.
DkNativePrepare:
 php
 pha
 cpx #6
 bcs DkPrepareDone
 lda #40
 sta InvPickupOwner,x
 lda #$fc
 sta InvPickup,x
 lda #0
 sta InvRisePhase,x
 sta InvPickupSaveLo,x
 sta InvPickupSaveHi,x
DkPrepareDone:
 pla
 plp
 rts
; Exact native emergence admission: regular mushroom/flower must mature;
; Star/1up retain genuine native handling. No source ability is invented.
DkNativeMature:
 cpx #6
 bcs DkMatureNo
 lda PowerUpType,x
 cmp #2
 bcs DkMatureYes
 lda Enemy_State,x
 bmi DkMatureYes
DkMatureNo:
 clc
 rts
DkMatureYes:
 sec
 rts
; Actual native collector, with no redundant private JSR frame. Native
; mushroom/flower/star/life bookkeeping stays native; source actor unchanged.
DkNativePickup:
 lda #$%02x
 sta FarcallJmpTarget_SMC+1
 lda #$%02x
 sta FarcallJmpTarget_SMC+2
 lda #$%02x
 jmp FarCallCommon
; WriteGameText already copied its full genuine header before policy30.
; Change only seven name cells for message0; never replace the header packet.
DkNativeStatusName:
 php
 cmp #0
 bne DkStatusDone
 pha
 tya
 pha
 ldy #6
DkStatusCopy:
 lda DkStatusName,y
 sta VRAM_Buffer1+11,y
 dey
 bpl DkStatusCopy
 pla
 tay
 pla
DkStatusDone:
 plp
 sec
 rts
DkStatusName:
 .byte $0d,$14,$24,$13,$1b,$24,$24
'''%(pc&255,pc>>8,bank)
    marker='DkjrComponentEnd:\n.export DkjrComponentEnd\n';assert source.count(marker)==1
    source=source.replace(marker,leaves+marker)
    targets=dict(previous['implemented_vector_rows']);targets.update({'4':'DkNativeHandled','20':'DkNativePrepare','23':'DkNativeMature','24':'DkNativePickup','30':'DkNativeStatusName'})
    at=source.index('DkServices:\n')+len('DkServices:\n');lines=source[at:].splitlines(True)
    for i in range(38):assert lines[i].startswith(' jmp ');lines[i]=' jmp '+targets.get(str(i),'DkUnavailable')+'\n'
    source=source[:at]+''.join(lines)
    cfg=(O/'native-scoretail-v54.cfg').read_text().replace('native-scoretail-','native-items-').replace('-v54.bin','-v60.bin')
    blob,L=A.assemble('native-items-v60',source,cfg)
    assert L['DkPauseThaw']==0xd60c and L['DkNativePortsEnd']==0xd77b and len(blob)<=8160
    q=dict(previous);q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),
        metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],
        implemented_vector_rows=targets,unimplemented_rows=[i for i in range(38)if str(i)not in targets],
        native_collector=dict(name='MarioSourcePowerupCollision',PC=pc,physical_PRG=bank&127,first32_SHA256=A.sha(b['raw'][collector_at:collector_at+32])),
        scope='Private compiled contract leaves only. No shared Nr/raw40 ingress or menu admission. Source B has no attack, so row4 acknowledges without creating native weapons. Actual item/status callers, AXYP/buffer/source semantics and interrupts require distinct CPU qualification.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-scoretail-v54.s',O/'native-score-tail-v59.json',R/'src/new_roster_dispatch.s',R/'src/screen_render.s',O/'native-items-v60.s',O/'native-items-v60.bin']})
    (O/'native-items-v60-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in['passed','body_bytes','header_spare','metadata_spare','unimplemented_rows']}))


if __name__=='__main__':main()
