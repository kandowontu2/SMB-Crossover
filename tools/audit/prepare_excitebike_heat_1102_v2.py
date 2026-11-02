"""Restore the omitted original DD8D cooling continuation in a separate kernel."""
from pathlib import Path
import hashlib,json,subprocess,sys
R=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(R/'tools'),str(R/'tools/audit')]
from prepare_excitebike_dispatch_1101_v1 import O,labels,sha,save

HEAT='''ExHeatRelease:
 ; Exact donor DD8D..DDCE state phase. CCDD/CD13 are donor HUD/OAM
 ; publication tails; this private phase returns before those foreign UIs.
 lda ExState+$03c
 ora ExState+$3e0
 beq ExHeatReturn
 lda ExState+$03c
 cmp #8
 beq ExHeatReleased
 bcc ExHeatReturn
 lda ExState+$094
 ora ExState+$098
 ora ExState+$09c
 bne ExHeatReturn
 lda ExState+$058
 beq ExHeatMoveLane
 lda #$c0
 sta ExState+$090
 bne ExHeatReturn
ExHeatMoveLane:
 sta ExState+$090
 ldx #1
 lda ExState+$0b8
 cmp ExRecData_D8C4
 bne ExHeatSetLane
 dex
ExHeatSetLane:
 stx ExState+$0dc
 rts
ExHeatReleased:
 lda #0
 sta ExState+$3e0
 lda #5
 sta ExState+$3b6
 sta ExState+$09c
 sta ExState+$374
ExHeatReturn:rts
.export ExSourceTimers,ExAirRecoveryStep,ExSourceThrottleGate
ExSourceTimers:
 ; Exact donor D310..D325: long timers30..3D tick every11 epochs.
 ldx #$0e
 dec ExState+$020
 bpl ExTimerLoop
 lda #$0a
 sta ExState+$020
 ldx #$1c
ExTimerLoop:
 lda ExState+$021,x
 beq ExTimerNext
 dec ExState+$021,x
ExTimerNext:
 dex
 bpl ExTimerLoop
 rts
ExAirRecoveryStep:
 jsr ExAirStep
 jsr ExSourceThrottleGate
 rts
ExSourceThrottleGate:
 ; Exact donor DCDE..DCF2, called after the source air step.
 lda ExState+$374,x
 beq ExThrottleGateDone
 dec ExState+$374,x
 lda ExState+$05c,x
 and #$c0
 beq ExThrottleGateDone
 lda #0
 sta ExState+$374,x
ExThrottleGateDone:rts
'''


def memory_image():
    rom=R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes'
    assert sha(rom)=='d8a87050beefefe96869ebd4d188beeb52733241cd2c0fa64392a55ec8ebca05'
    raw=bytearray(rom.read_bytes());new=(O/'heat-kernel.bin').read_bytes();old=(O/'host-kernel.bin').read_bytes()
    at=1048592+728*1024;assert raw[at:at+6144]==old
    raw[at:at+6144]=new
    cookie=bytes([167,37,1])+hashlib.sha256(new+(O/'host-metadata.bin').read_bytes()+(O/'body-native.chr').read_bytes()).digest()[:13]
    at=16+65*8192+0x1016;assert raw[at:at+16]==(O/'host-cookie.bin').read_bytes()
    raw[at:at+16]=cookie
    return bytes(raw),cookie


def main():
    source=(O/'host-recovery.s').read_text();start=source.index('ExHeatRelease:\n');end=source.index('.export ExRecoveryEnd',start)
    source='.import ExAirStep\n'+source[:start]+HEAT+source[end:];(O/'heat-recovery.s').write_text(source)
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'heat-recovery.s','-o',O/'heat-recovery.o'],
                [cc/'ld65.exe','-C',O/'host.cfg',R/'build/excite-prince-component-1101-v2/component.o',
                 O/'pose.o',O/'host.o',O/'heat-recovery.o','-o',O/'heat-kernel.bin','-Ln',O/'heat-host.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    old=(O/'host-kernel.bin').read_bytes();new=bytearray((O/'heat-kernel.bin').read_bytes())
    oldlab=labels(O/'host.lbl');newlab=labels(O/'heat-host.lbl')
    for name,a in oldlab.items():
        if name not in ['ExRecoveryEnd']:assert newlab[name]==a,(name,a,newlab.get(name))
    # The linker leaves the transport table blank; preserve every reviewed
    # service row exactly. No service implementation or ingress moved.
    new[0x500:0x571]=old[0x500:0x571]
    at=oldlab['ExHeatRelease']-0xa000;end=newlab['ExRecoveryEnd']-0xa000
    assert new[:at]==old[:at]and new[end:]==old[end:]
    # Preserve all host/public addresses while replacing the incomplete
    # inline timer subset with the exact source divider phase.
    timer=new.index(bytes.fromhex('a203bd26c0f003de26c0'),oldlab['ExHostMovement']-0xa000)
    heatcall=new.index(bytes([32,oldlab['ExHeatRelease']&255,oldlab['ExHeatRelease']>>8]),timer)
    assert heatcall-timer==37
    target=newlab['ExSourceTimers'];resume=0xa000+heatcall
    new[timer:heatcall]=bytes([32,target&255,target>>8,76,resume&255,resume>>8])+bytes([234])*(heatcall-timer-6)
    target=oldlab['ExAirStep'];pattern=bytes([32,target&255,target>>8])
    begin=oldlab['ExHostMovement']-0xa000;finish=oldlab['ExHostEnd']-0xa000
    assert new.count(pattern,begin,finish)==1
    aircall=new.index(pattern,begin,finish);target=newlab['ExAirRecoveryStep']
    new[aircall:aircall+3]=bytes([32,target&255,target>>8])
    (O/'heat-kernel.bin').write_bytes(new)
    raw,cookie=memory_image();(O/'heat-cookie.bin').write_bytes(cookie)
    save('heat-assembly.json',dict(passed=True,ROM_written=False,
        memory_candidate_SHA256=hashlib.sha256(raw).hexdigest(),previous_kernel_SHA256=sha(O/'host-kernel.bin'),
        new_kernel_SHA256=sha(O/'heat-kernel.bin'),heat_entry=oldlab['ExHeatRelease'],
        old_recovery_end=oldlab['ExRecoveryEnd'],new_recovery_end=newlab['ExRecoveryEnd'],
        extra_private_code_bytes=newlab['ExRecoveryEnd']-oldlab['ExRecoveryEnd'],
        no_public_entry_moved=True,no_new_PRG_CHR_RAM=True,
        original_source_half_open=[[0xdd8d,0xddd1],[0xd310,0xd326],[0xdcde,0xdcf2]],UI_tails_return=['CCDD','CD13'],
        host_timer_patch=[0xa000+timer,0xa000+heatcall],host_post_air_patch=0xa000+aircall,
        scope='Separate proposal restoring omitted original cooldown lane completion, timer divider and post-air throttle gate. Source differential and full original overheat/recovery continuation proof required before writing a ROM.',
        bindings={p.relative_to(R).as_posix():sha(p)for p in [Path(__file__),O/'host-recovery.s',O/'heat-recovery.s',O/'heat-kernel.bin',O/'heat-host.lbl',O/'heat-cookie.bin',R/'build/arthur-side-clamp-1101-v8/weapon-tail-candidate.nes']}))
    print(json.dumps(dict(passed=True,extra_code_bytes=newlab['ExRecoveryEnd']-oldlab['ExRecoveryEnd'],memory_SHA256=hashlib.sha256(raw).hexdigest())))


if __name__=='__main__':main()
