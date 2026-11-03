"""Private DK native injury/death/reset leaves, preserving original D405/CF37.

This successor changes no shared route, cartridge, grant or frozen v28 input.
"""
import json
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O


def main():
    previous=json.loads((O/'native-powerup-v26-layout.json').read_text())
    assert json.loads((O/'native-powerup-v29-IRQ.json').read_text())['passed']
    source=(O/'native-powerup-v26.s').read_text()
    targets=dict(previous['implemented_vector_rows'])
    targets.update({str(k):v for k,v in {
        5:'DkNativeInjury',6:'DkNativeInjuryStatus',7:'DkNativeDeathStart',
        8:'DkNativeDeath',9:'DkNativeHandled',19:'DkNativeReset',
        34:'DkNativeHandled',36:'DkConstruct'}.items()})
    at=source.index('DkServices:\n')+len('DkServices:\n')
    lines=source[at:].splitlines(True)
    for i in range(38):
        assert lines[i].startswith(' jmp ')
        lines[i]=' jmp '+targets.get(str(i),'DkUnavailable')+'\n'
    source=source[:at]+''.join(lines)
    leaf='''
.export DkNativeInjury,DkNativeInjuryStatus,DkNativeDeathStart
.export DkNativeDeath,DkNativeReset,DkNativeHandled,DkNativeLifecycleEnd
; InjurePlayer first asks Status for a nonzero native injury profile. That
; admits row5, whose Cset prevents native shrink/recoil/death substitution.
; An earned source-hit phase has no contact processing in original CD91;
; similarly its private injury leaf absorbs contacts without changing D1AE.
DkNativeInjuryStatus:
 lda #1
 tax
 rts
DkNativeInjury:
 lda $c068
 bne DkNativeHandled
 lda $c06b
 cmp #5
 beq DkNativeHandled
DkNativeDeathStart:
 jsr DkPauseThaw
 jsr DkjrDamage
DkNativeHandled:
 sec
 rts
; Native PlayerDeath executes in engine11 with TimerControl normally nonzero.
; Tick the original CF37/DB20/DAF7 state machine directly; it alone chooses
; DImportCF62 and the already-qualified exact native EndDeath event.
DkNativeDeath:
 lda $c8fe
 beq DkLifecycleNo
 lda $c06b
 cmp #5
 beq DkDeathTick
 jsr DkNativeDeathStart
DkDeathTick:
 jsr DkjrDefeatTick
 sec
 rts
; Scene retirement precedes overlay replacement in the proposed manager.
; Reset additionally rejects old constructed state until genuine Fresh.
DkNativeReset:
 jsr DkPauseThaw
 lda #0
 sta $c8fe
 sec
 rts
DkLifecycleNo:
 clc
 rts
DkNativeLifecycleEnd:
'''
    marker='DkjrComponentEnd:\n.export DkjrComponentEnd\n'
    assert source.count(marker)==1
    source=source.replace(marker,leaf+marker)
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-lifecycle-pause-v30.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-lifecycle-main-v30.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-lifecycle-ports-v30.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    blob,L=A.assemble('native-lifecycle-v30',source,cfg)
    assert L['DkPauseThaw']==0xd60c and L['DkNativePortsEnd']==previous['metadata_end']
    # Appending leaves changes no existing original/source/native instruction.
    prior=(O/'native-powerup-v26.bin').read_bytes()
    assert blob[114:len(prior)]==prior[114:]
    for part in ['pause','main','ports']:
        assert (O/f'native-lifecycle-{part}-v30.bin').read_bytes()==(O/f'native-powerup-{part}-v26.bin').read_bytes()
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,
        body_bytes=len(blob),body_end=L['DkjrComponentEnd'],header_spare=8160-len(blob),
        metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],
        labels=L,implemented_vector_rows=targets,unimplemented_rows=[i for i in range(38)if str(i)not in targets],
        original_and_existing_native_instructions_unchanged=True,
        remaining=['Actual InjurePlayer/UnionDeathStartCore/PlayerDeath ingress, all original source defeat epochs and native PlayerLoseLife lifecycle.','All other unfinished vector APIs, final latest-Prince/current-Bub rebind and payload art/cookie closure.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),O/'native-powerup-v26.s',O/'native-powerup-v26.bin',O/'native-powerup-v29-IRQ.json',O/'native-lifecycle-v30.s',O/'native-lifecycle-v30.bin']})
    (O/'native-lifecycle-v30-layout.json').write_text(json.dumps(q,indent=2)+'\n')
    print(json.dumps({k:q[k]for k in ['passed','body_bytes','body_end','header_spare','metadata_spare','unimplemented_rows']}))


if __name__=='__main__':main()
