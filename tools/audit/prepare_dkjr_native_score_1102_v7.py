"""Bind original DK score requests to actual current native AddToScore."""
import json,re,subprocess
from pathlib import Path
import prepare_dkjr_native_phase_1102_v6 as P
R=P.R;O=P.O;W=P.W;D=P.D
CURRENT=R/'build/menu-family-root-candidate-1102-v1/mr-gimmick-family.nes'
PIN='22d09909bf952ef007d1582589dc869073262784bf38b92d2c7b206ce3c45b19'


def main():
    proof=json.loads((O/'native-phase-v6-CPU.json').read_text());assert proof['passed']
    for rel,sha in proof['bindings'].items():assert W.P.sha((R/rel).read_bytes())==sha,rel
    prior=json.loads((O/'native-phase-v6-layout.json').read_text());source=(O/'native-phase-v6.s').read_text()
    source=source.replace('DkjrComponentEnd:\n.export DkjrNativePhaseEnd,DkjrComponentEnd','')
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=CURRENT.read_bytes();assert W.P.sha(raw)==PIN
    native={n:W.address(b,n)for n in ['DigitModifier','CurrentPlayer']}
    for name,pc in native.items():source='%s=$%04x\n'%(name,pc)+source
    old=' jsr DkjrNativeControls\n lda $c068';assert source.count(old)==1
    source=source.replace(old,' jsr DkjrNativeControls\n jsr DkjrNativePublishScore\n lda $c068')
    source+='''
.export DkjrNativePublishScore
ScoreAmount=$c8f9
; Original source EE3A consumes the ring before the actor phase. One source
; entry per native phase bounds native HUD work. Types30/40 are donor-only
; scoreboard redraw requests, whose native counterpart is AddToScore's own
; HUD update. They never publish a donor VRAM command into the SMB nametable.
; Preserve AXYP/R0..7/ObjectOffset/all33live SMC bytes and actual PRG maps.
DkjrNativePublishScore:
 php
 pha
 txa
 pha
 tya
 pha
 ldx $c300
 cpx #46
 jcs ScoreReturn
 txa
 and #1
 jne ScoreReturn
 lda $c302,x
 jeq ScoreReturn
 and #$f0
 cmp #$10
 beq ScorePoints
 cmp #$30
 beq ScoreRetireUI
 cmp #$40
 bne ScoreReturn
ScoreRetireUI:
 jsr ScoreRetireEntry
 jmp ScoreReturn
ScorePoints:
 lda $c302,x
 and #$f8
 cmp #$18
 bne ScoreReturn
 lda $c302,x
 and #7
 cmp CurrentPlayer
 bne ScoreReturn
 lda $c303,x
 sta ScoreAmount
 and #$0f
 cmp #10
 bcs ScoreReturn
 lda ScoreAmount
 cmp #$a0
 bcs ScoreReturn
 jsr ScoreRetireEntry
 ldx #7
ScoreSaveScratch:
 lda R0,x
 pha
 dex
 bpl ScoreSaveScratch
 lda ObjectOffset
 pha
 ldx #32
ScoreSaveSMC:
 lda $015a,x
 pha
 dex
 bpl ScoreSaveSMC
 ldx #5
 lda #0
ScoreClearDigits:
 sta DigitModifier,x
 dex
 bpl ScoreClearDigits
 lda ScoreAmount
 and #$0f
 sta DigitModifier+4
 lda ScoreAmount
 lsr
 lsr
 lsr
 lsr
 sta DigitModifier+3
 jsr DkjrNativeAddScore
 ldx #0
ScoreRestoreSMC:
 pla
 sta $015a,x
 inx
 cpx #33
 bne ScoreRestoreSMC
 pla
 sta ObjectOffset
 ldx #0
ScoreRestoreScratch:
 pla
 sta R0,x
 inx
 cpx #8
 bne ScoreRestoreScratch
ScoreReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
ScoreRetireEntry:
 lda #0
 sta $c302,x
 inx
 inx
 cpx #46
 bcc :+
 ldx #0
:
 stx $c300
 rts
'''
    pc=W.address(b,'AddToScore');pos=W.location(b,'AddToScore');bank=((pos-16)//8192)|128
    assert raw[pos:pos+32]==b['raw'][pos:pos+32]
    source+='\nDkjrNativeAddScore:\n lda #$%02x\n sta FarcallJmpTarget_SMC+1\n lda #$%02x\n sta FarcallJmpTarget_SMC+2\n lda #$%02x\n jmp FarCallCommon\n'%(pc&255,pc>>8,bank)
    source+='DkjrNativeScoreEnd:\nDkjrComponentEnd:\n.export DkjrNativeScoreEnd,DkjrComponentEnd\n'
    # Long conditional exits are explicit; assembled size includes them.
    source=re.sub(r'\n (b(?:cc|cs|eq|ne|mi|pl)) ScoreReturn',lambda q:'\n j'+q[1][1:]+' ScoreReturn',source)
    (O/'native-score-v7.s').write_text(source);(O/'native-score-v7.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'native-score-v7.s','-g','-o',O/'native-score-v7.o'],[cc/'ld65.exe','-C',O/'native-score-v7.cfg',O/'native-score-v7.o','-o',O/'native-score-v7.bin','-Ln',O/'native-score-v7.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    blob=(O/'native-score-v7.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-score-v7.lbl').read_text(),re.M)};assert len(blob)<=8160
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=PIN,component_bytes=len(blob),header_reserved_spare=8160-len(blob),code_SHA256=W.P.sha(blob),labels=labels,
        private_state_half_open=[0xc000,0xc900],additional_live_private_scratch=[0xc8f9,0xc8fa],native_bindings={**prior['native_bindings'],**native},
        native_score_call=dict(target='AddToScore',CPU_address=pc,physical_bank=bank&127,file_offset=pos,first32_SHA256=W.P.sha(raw[pos:pos+32]),unchanged_from_full_metadata_base=True),
        original_score_source='Original C61B requests are BCD hundreds: 01/02/03/04/08/12/16 =>100/200/300/400/800/1200/1600. Original ED44/ED7B decide the amount, not the host.',
        score_timing='At most one source ring entry before each actual native phase; original request order/amount is preserved. Donor scoreboard redraw types30/40 retire without publishing donor VRAM.',
        remaining_native_ports=['World-fruit/current-native-victim lifecycle','Camera delta and constructor/script handoff','Body/fruit/point art, OAM/CHR/palette/HUD/status','Typed public service/owner/cold/interrupt/current resource admission'],
        scope='Compiled actual native score adapter; CPU qualification pending. No ROM/shared page/RAM grant or native menu admission.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in [Path(__file__),O/'native-phase-v6-CPU.json',O/'native-phase-v6.s',O/'native-score-v7.s',O/'native-score-v7.bin',CURRENT]})
    (O/'native-score-v7-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','qualified','component_bytes','header_reserved_spare','code_SHA256']}))


if __name__=='__main__':main()
