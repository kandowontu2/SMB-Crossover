"""First-valid-engine8 coordinate handoff, guarded pending lifecycle."""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A

R,O=A.R,A.O


def main():
    q=json.loads((O/'native-event-v74-layout.json').read_text())
    source=(O/'native-event-v74.s').read_text()
    start=source.index('DkNativeMature:\n');end=source.index('; Actual native collector',start)
    mature=source[start:end]
    source=source[:start]+source[end:]
    profiles='''DkNativeAdder:
 ldy #2
 sec
 rts
DkNativeBoxProfile:
 ldy #1
 sec
 rts
'''
    assert source.count(profiles)==1;source=source.replace(profiles,'')
    old='DkNativeMain:\n lda $c8fe\n beq DkMainNo'
    assert source.count(old)==1;source=source.replace(old,'DkNativeMain:\n jsr DkNativeAnchorReady\n bcc DkMainNo')
    helper='''
.export DkNativeAnchorReady
; Ready0 is unconstructed,1 awaits the legitimate native entrance,2 owns
; the anchored source actor. Never infer a subsequent impulse from velocity.
DkNativeAnchorReady:
 lda $c8fe
 cmp #2
 beq DkAnchorYes
 cmp #1
 bne DkAnchorNo
 lda GameEngineSubroutine
 cmp #8
 bne DkAnchorNo
 jsr DkjrNativeImportAnchor
 bcc DkAnchorNo
 jsr DkjrNativeCameraSync
 inc $c8fe
DkAnchorYes:
 ; CMP#2 on the anchored path and CameraSync on the pending path both
 ; leave C1; INC does not alter it. No redundant SEC is needed here.
 rts
DkAnchorNo:
 clc
 rts
'''
    marker='DkjrComponentEnd:\n.export DkjrComponentEnd\n'
    assert source.count(marker)==1;source=source.replace(marker,helper+marker)
    old='DkNativeDeathStart:\n jsr DkPauseThaw'
    assert source.count(old)==1;source=source.replace(old,'DkNativeDeathStart:\n lda $c8fe\n cmp #2\n bne DkNativeHandled\n jsr DkPauseThaw')
    old='DkNativeDeath:\n lda $c8fe\n beq DkLifecycleNo'
    assert source.count(old)==1;source=source.replace(old,'DkNativeDeath:\n lda $c8fe\n cmp #2\n bne DkLifecycleNo')
    old='DkNativePickup:\n'
    assert source.count(old)==1;source=source.replace(old,'''DkNativePickup:
 lda $c8fe
 cmp #2
 beq DkPickupReady
 sec
 rts
DkPickupReady:
''')
    old=' lda #>ObjectMetasprite\n sta SmPosePtr+1\n ldy CurrentOAMOffset'
    new=' lda #>ObjectMetasprite\n sta SmPosePtr+1\n lda $c8fe\n cmp #2\n jne BodyDrawDone\n ldy CurrentOAMOffset'
    assert source.count(old)==1;source=source.replace(old,new)
    old='DkFullBox:\n lda $c8fe\n beq DkPortNo'
    assert source.count(old)==1;source=source.replace(old,'DkFullBox:\n lda $c8fe\n cmp #2\n bne DkPortNo')
    start=source.index('DkFullBox:\n');end=source.index('DkPortNo:\n',start)
    box=source[start:end];old=' ldx #0\n ldy #0\n sec\n rts'
    assert box.count(old)==1;box=box.replace(old,' ldx #0\n sec\n rts')
    source=source[:start]+box+source[end:]
    old=' lda $c8fe\n beq DkBounceNo'
    assert source.count(old)==1;source=source.replace(old,' lda $c8fe\n cmp #2\n bne DkBounceNo')
    mature=mature.replace('DkNativeMature:\n','DkNativeMature:\n lda $c8fe\n cmp #2\n bne DkMatureNo\n')
    fresh='''.export DkNativeFresh
; Every legal Fresh/scene constructor first unwinds an old native pause
; lease, then rearms the entrance handoff. Native lives/scores stay native.
DkNativeFresh:
 jsr DkNativeReset
 jmp DkConstruct
'''
    source=source.replace('DkNativePortsEnd:\n',mature+profiles+fresh+'DkNativePortsEnd:\n')
    targets=dict(q['implemented_vector_rows']);targets.update({'15':'DkNativeFresh','36':'DkNativeFresh'})
    at=source.index('DkServices:\n')+len('DkServices:\n');lines=source[at:].splitlines(True)
    for i in range(38):lines[i]=' jmp '+targets.get(str(i),'DkUnavailable')+'\n'
    source=source[:at]+''.join(lines)
    cfg=(O/'native-event-v74.cfg').read_text().replace('native-event-','native-entrance-').replace('-v74.bin','-v89.bin')
    blob,L=A.assemble('native-entrance-v89',source,cfg)
    assert len(blob)<=8160 and L['DkNativePortsEnd']<=0xd800 and L['DkPauseThaw']==0xd60c
    assert L['DkNativeMain']==0xd65e and L['DkNativeMainEnd']==0xd6a7
    q.update(labels=L,body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),
        metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],implemented_vector_rows=targets,
        readiness_contract=dict(address=0xc8fe,legal_values={'0':'unconstructed/reset/cold','1':'constructed, pending legitimate entrance','2':'anchored at first valid engine8'},
            first_native_anchor='Unchanged DkjrNativeImportAnchor current native X/page/Y/high/camera; unchanged CameraSync. No fixed coordinate, new mutable byte or per-update reset.',
            same_life_scene='Both actual publicFresh15 andscene36 call Reset (thaws old lease,Ready0) then original constructor (Ready1). First subsequent valid engine8 anchors after native entrance.',
            pending_guards=['Main no original phase','FullBox no D2BD','DrawBody stablezeroheader but no body OAM','Bounce no D257','Injury/deathstart handled without source damage','Deathtick rejects','MatureCclear','Pickup handled unconsumed']),
        redundant_native_box_LDY0_removed='The final index0 loop iteration setsY0 viaTXA/AND1/ASL/TAY; DEX then terminates without changingY. Existing IRQ preservesY. X0 explicit remains.',
        scope='Private compiled fix for retained88 real native entrance-order negative. ExistingReady byte becomes exact0/1/2 lifecycle. Complete compiled read/write/indirect guards, pending callbacks, actual entrance/scene/powerup/render and IRQ qualification required before native admission.',
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in [Path(__file__),O/'native-event-v74.s',O/'native-event-v74-layout.json',
            O/'native-entrance-v89.s',O/'native-entrance-v89.bin',O/'native-entrance-main-v89.bin',O/'native-entrance-ports-v89.bin',O/'native-entrance-v88-negative.json']})
    (O/'native-entrance-v89-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','metadata_end','metadata_spare','readiness_contract']}))


if __name__=='__main__':main()
