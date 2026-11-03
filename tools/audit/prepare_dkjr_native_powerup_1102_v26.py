"""Native row33 keeps an earned source-hit lease through genuine powerup9.

Private compiled successor only, with the real GuestPowerupUpdate import.
No native duration/ability replacement or shared hook is introduced.
"""
import json,re
from pathlib import Path
import measure_dkjr_admission_1102_v11 as A
R=A.R;O=A.O;W=A.W


def main():
    prior=json.loads((O/'native-display-v24-layout.json').read_text());assert json.loads((O/'native-display-v25-CPU.json').read_text())['passed']
    source=(O/'native-display-v24.s').read_text();b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes')
    pc=W.address(b,'GuestPowerupUpdate');bank=((W.location(b,'GuestPowerupUpdate')-16)//8192)|128
    start=source.index('DkServices:\n')+len('DkServices:\n');lines=source[start:].splitlines(True);assert lines[33]==' jmp DkUnavailable\n';lines[33]=' jmp DkNativePowerup\n';source=source[:start]+''.join(lines)
    source=source.replace('DkNativePortsEnd:\n','')
    source+='''
.export DkNativePowerup,DkNativePortsEnd
; The native engine's9/12 update owns its own60updates and final task/timer.
; Empty spawn receipts stay leased while our donor hit still exists. A real
; native completion may setTimer0/Engine8; re-arm before GameCore's AI pass,
; without advancing/resetting original D1AE or its counter during the powerup.
DkNativePowerup:
 lda #$%02x
 sta FarcallJmpTarget_SMC+1
 lda #$%02x
 sta FarcallJmpTarget_SMC+2
 lda #$%02x
 jsr FarCallCommon
 lda $c440
 beq DkPowerupDone
 lda $c068
 beq DkPowerupThaw
 lda GameEngineSubroutine
 cmp #8
 bne DkPowerupDone
 jsr PauseContext
 bcc DkPowerupThaw
 lda #$ff
 sta TimerControl
DkPowerupDone:
 sec
 rts
DkPowerupThaw:
 jsr DkPauseThaw
 jmp DkPowerupDone
DkNativePortsEnd:
'''%(pc&255,pc>>8,bank)
    cfg='MEMORY{C:start=$a000,size=$1fe0,file=%O;P:start=$d540,size=$11e,file="'+(O/'native-powerup-pause-v26.bin').as_posix()+'";M:start=$d65e,size=$46,file="'+(O/'native-powerup-main-v26.bin').as_posix()+'";N:start=$d6a4,size=$15c,file="'+(O/'native-powerup-ports-v26.bin').as_posix()+'";}SEGMENTS{DKJR:load=C,type=rw;DK_PAUSE:load=P,type=ro;DK_MAIN:load=M,type=ro;DK_PORTS:load=N,type=ro;}'
    core,L=A.assemble('native-powerup-v26',source,cfg);ports=(O/'native-powerup-ports-v26.bin').read_bytes();targets=dict(prior['implemented_vector_rows']);targets['33']='DkNativePowerup'
    q=dict(passed=True,qualified=False,native_owner_admitted=False,ROM_written=False,body_bytes=len(core),body_end=L['DkjrComponentEnd'],header_spare=8160-len(core),ports_bytes=len(ports),metadata_end=L['DkNativePortsEnd'],metadata_spare=0xd800-L['DkNativePortsEnd'],labels=L,implemented_vector_rows=targets,unimplemented_rows=[i for i in range(38)if str(i)not in targets],native_powerup_import=dict(PC=pc,physical_PRG=bank&127,first32_bytes=A.BASE.read_bytes()[W.location(b,'GuestPowerupUpdate'):W.location(b,'GuestPowerupUpdate')+32].hex()),
        remaining=['Actual full PlayerChangeSize/NrNativePowerupDispatch/HuPowerup ingress and nested GuestFinish/GetPlayerColors/stack/IRQ proof.','All inherited unfinished private rows, art closure/payload cookie and source-owned Scene/death/retirement integration.'],
        bindings={p.relative_to(R).as_posix():A.sha(p.read_bytes())for p in[Path(__file__),A.BASE,O/'native-display-v24.s',O/'native-display-v25-CPU.json',O/'native-powerup-v26.s',O/'native-powerup-v26.bin',O/'native-powerup-ports-v26.bin']})
    (O/'native-powerup-v26-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','body_bytes','header_spare','ports_bytes','metadata_end','metadata_spare']}))


if __name__=='__main__':main()
