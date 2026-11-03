"""Measure source-funded private world fruit/camera and direct native score.

All addresses are conditional measurement addresses. No host allocation,
public owner, ROM, menu or native helper placement is authorized here.
"""
import json,re,subprocess,zipfile
from pathlib import Path
import prepare_dkjr_native_score_1102_v7 as P
R=P.R;O=P.O;W=P.W;D=P.D
CURRENT=P.CURRENT;PIN=P.PIN


def main():
    checkpoint=R/'docs/qa/checkpoints/2026-11-02/dkjr-native-phase-v7';frozen=json.loads((checkpoint/'manifest.json').read_text())
    assert W.P.sha((checkpoint/'inputs.zip').read_bytes())==frozen['archive_SHA256']
    with zipfile.ZipFile(checkpoint/'inputs.zip')as z:
        rel='build/dkjr-native-source-1102-v2/native-score-v7.s';data=z.read(rel);assert W.P.sha(data)==frozen['files'][rel]['SHA256'];source=data.decode().replace('\r\n','\n')
        prior=json.loads(z.read('build/dkjr-native-source-1102-v2/native-score-v7-layout.json'))
    removed=[]
    def cut(first,last,role):
        nonlocal source
        a=source.index(first);b=source.index(last,a);removed.append(dict(first=first.split(':')[0],last=last.split(':')[0],role=role));source=source[:a]+source[b:]
    cut('D_ec84:','D_ecb7:','Donor-only source scoreboard queue/highscore redraw requests; source point choice and popup drawing remain')
    cut('D_ee7f:','DNativeData_c614:','Donor source score/VRAM packet ring producers, bounds-unwind and nametable/attribute writes are replaced by native score/world-fruit removal')
    cut('DkjrNativeSourceFruitInitialize:','DkjrNativePhaseEnd:','Screen-fixed source fixture initializer; native world-fruit constructor replaces it')
    cut('.export DkjrNativePublishScore','DkjrNativeScoreEnd:','Source queue consumer; source point choice now calls the same real native score service directly')
    source=source.replace('DkjrNativeScoreEnd:\nDkjrComponentEnd:\n.export DkjrNativeScoreEnd,DkjrComponentEnd','')
    source=source.replace(' jsr D_ec84',' jsr DkjrNativeAwardSourcePoints')
    for pc in [0xefce,0xf1c5]:
        old='DImport_%04x: jmp D_%04x'%(pc,pc);assert source.count(old)==1;source=source.replace(old,'DImport_%04x: jmp DkjrNativeFruitRemove'%pc)
    old=' jsr DkjrNativeControls\n jsr DkjrNativePublishScore\n lda $c068';assert source.count(old)==1
    source=source.replace(old,' jsr DkjrNativeShiftCamera\n jcc DkjrNativePhaseReject\n jsr DkjrNativeControls\n jsr DkjrNativeFruitProject\n lda $c068')
    # Every direct4xx source access was donor geometry or absent in profile1.
    # The retained original indirect domains are descriptors/OAM,91 fruit, and
    # native C8 terrain. Only the typed91 producer may now point into C400.
    old_direct=re.findall(r'^\s+(?:lda|sta|ldx|ldy|adc|sbc|cmp|inc|dec)\s+\$[cC]4[0-9a-fA-F]{2}',source,re.M);assert not old_direct,old_direct
    source+='''
.export DkjrNativeAwardSourcePoints,DkjrNativeFruitReset,DkjrNativeFruitSet,DkjrNativeFruitProject,DkjrNativeFruitRemove
.export DkjrNativeCameraSync,DkjrNativeShiftCamera
DkjrNativeSourceFruitInitialize=DkjrNativeFruitReset
; Measurement-only source-dead donor geometry RAM, inside the original2KB:
; C400..41C original7-byte records/header;420/424worldXlo/hi,428Y,42Cbase,
; 430availability,434count,435/436lastcamera,437ready,438delta scratch.
FruitCount=$c434
CameraLow=$c435
CameraHigh=$c436
WorldReady=$c437
CameraDelta=$c438
ScoreAmount=$c8f9
R1=R0+1
R2=R0+2
R3=R0+3
DkjrNativeAwardSourcePoints:
 php
 pha
 txa
 pha
 tya
 pha
 cpx #7
 jcs AwardReturn
 lda DNativeData_c61b,x
 sta ScoreAmount
 ldx #7
AwardSaveScratch:
 lda R0,x
 pha
 dex
 bpl AwardSaveScratch
 lda ObjectOffset
 pha
 ldx #32
AwardSaveSMC:
 lda $015a,x
 pha
 dex
 bpl AwardSaveSMC
 ldx #5
 lda #0
AwardClearDigits:
 sta DigitModifier,x
 dex
 bpl AwardClearDigits
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
AwardRestoreSMC:
 pla
 sta $015a,x
 inx
 cpx #33
 bne AwardRestoreSMC
 pla
 sta ObjectOffset
 ldx #0
AwardRestoreScratch:
 pla
 sta R0,x
 inx
 cpx #8
 bne AwardRestoreScratch
AwardReturn:
 pla
 tay
 pla
 tax
 pla
 plp
 rts
; Explicit constructor, after original actor init/body pose/native anchor.
; No fruit is placed in SMB by default. Typed stage data must call FruitSet.
DkjrNativeFruitReset:
 lda #0
 sta FruitCount
 sta $c08c
 sta $c068
 sta $c066
 ldx #3
FruitResetLoop:
 sta $c430,x
 sta $c09a,x
 dex
 bpl FruitResetLoop
 lda #0
 sta $c091
 lda #4
 sta $c092
 lda #1
 sta $c04a
 sta $c0a0
 sta $c0b0
 lda #$ff
 sta $c2c0
 sta $c2e0
 jsr DkjrNativeCameraSync
 jmp DkjrNativeFruitProject
; InputX0..3,R0/R1worldX,R2Y32..200,R3kind0..2. Cset accepts.
; Reject before any private change. Original state/phase/controls are not reset.
DkjrNativeFruitSet:
 cpx #4
 bcs FruitSetReject
 lda R2
 cmp #32
 bcc FruitSetReject
 cmp #201
 bcs FruitSetReject
 lda R3
 cmp #3
 bcs FruitSetReject
 pha
 ora #0
 beq :+
 lda #2
:
 sta $c08d,x
 pla
 asl
 asl
 clc
 adc #$a4
 sta $c42c,x
 lda R0
 sta $c420,x
 lda R1
 sta $c424,x
 lda R2
 sta $c428,x
 lda #1
 sta $c430,x
 txa
 clc
 adc #1
 cmp FruitCount
 bcc :+
 sta FruitCount
:
 sec
 rts
FruitSetReject:
 clc
 rts
; Exactly four bounded source-format records. World availability survives
; viewport exit; source9A is the current visible/touchable projection only.
DkjrNativeFruitProject:
 ldx FruitCount
 cpx #5
 bcs FruitProjectReject
 lda #0
 sta $c093
 cpx #0
 beq FruitLengthDone
FruitLengthLoop:
 clc
 adc #7
 dex
 bne FruitLengthLoop
FruitLengthDone:
 sta $c093
 sta $c400
 ldx #0
 ldy #1
FruitProjectLoop:
 lda #0
 sta $c09a,x
 cpx FruitCount
 bcs FruitProjectNext
 lda $c430,x
 beq FruitProjectNext
 lda $c420,x
 sec
 sbc ScreenLeft_X_Pos
 sta $c400,y
 lda $c424,x
 sbc ScreenLeft_PageLoc
 bne FruitProjectNext
 lda $c400,y
 cmp #240
 bcs FruitProjectNext
 lda $c428,x
 sta $c401,y
 lda $c42c,x
 sta $c402,y
 lda #$24
 sta $c403,y
 sta $c404,y
 sta $c405,y
 sta $c406,y
 lda #1
 sta $c09a,x
FruitProjectNext:
 tya
 clc
 adc #7
 tay
 inx
 cpx #4
 bne FruitProjectLoop
 sec
 rts
FruitProjectReject:
 clc
 rts
; Original D955 has already cleared source9A and published8C. This semantic
; world/OAM removal replaces both old BG-tile erase and attribute restore.
; It is idempotent: camera projection cannot resurrect a touched fruit.
DkjrNativeFruitRemove:
 php
 pha
 txa
 pha
 ldx $c08c
 beq FruitRemoveReturn
 cpx #5
 bcs FruitRemoveReturn
 dex
 lda #0
 sta $c430,x
FruitRemoveReturn:
 pla
 tax
 pla
 plp
 rts
DkjrNativeCameraSync:
 lda ScreenLeft_X_Pos
 sta CameraLow
 lda ScreenLeft_PageLoc
 sta CameraHigh
 lda #$d7
 sta WorldReady
 sec
 rts
; Normal native camera transport only. Script/scene jumps must explicitly
; import the native anchor and call CameraSync. No velocity inference.
DkjrNativeShiftCamera:
 lda WorldReady
 cmp #$d7
 bne CameraReject
 lda ScreenLeft_X_Pos
 sec
 sbc CameraLow
 sta CameraDelta
 lda ScreenLeft_PageLoc
 sbc CameraHigh
 beq CameraPositive
 cmp #$ff
 bne CameraReject
 lda CameraDelta
 cmp #$f8
 bcc CameraReject
 bcs CameraTranslate
CameraPositive:
 lda CameraDelta
 cmp #9
 bcs CameraReject
CameraTranslate:
 lda CameraDelta
 beq CameraCommit
 ldx #252
CameraCellLoop:
 lda $c200,x
 cmp #$ff
 beq CameraNextCell
 lda $c203,x
 sec
 sbc CameraDelta
 sta $c203,x
CameraNextCell:
 dex
 dex
 dex
 dex
 cpx #252
 bne CameraCellLoop
CameraCommit:
 jmp DkjrNativeCameraSync
CameraReject:
 clc
 rts
'''
    b=W.scoped_load(R/'build/excitebike-pose-1101-v3/current4.nes');raw=CURRENT.read_bytes();assert W.P.sha(raw)==PIN
    pc=W.address(b,'AddToScore');pos=W.location(b,'AddToScore');bank=((pos-16)//8192)|128;assert raw[pos:pos+32]==b['raw'][pos:pos+32]
    source+='\nDkjrNativeAddScore:\n lda #$%02x\n sta FarcallJmpTarget_SMC+1\n lda #$%02x\n sta FarcallJmpTarget_SMC+2\n lda #$%02x\n jmp FarCallCommon\n'%(pc&255,pc>>8,bank)
    source+='DkjrNativeFruitEnd:\nDkjrComponentEnd:\n.export DkjrNativeFruitEnd,DkjrComponentEnd\n'
    (O/'native-fruit-v8.s').write_text(source);(O/'native-fruit-v8.cfg').write_text('MEMORY{C:start=$a000,size=$2000,file=%O;}SEGMENTS{DKJR:load=C,type=rw;}')
    cc=R/'tools/Windows/cc65/bin'
    for cmd in [[cc/'ca65.exe',O/'native-fruit-v8.s','-g','-o',O/'native-fruit-v8.o'],[cc/'ld65.exe','-C',O/'native-fruit-v8.cfg',O/'native-fruit-v8.o','-o',O/'native-fruit-v8.bin','-Ln',O/'native-fruit-v8.lbl']]:
        p=subprocess.run(list(map(str,cmd)),capture_output=True,text=True);assert p.returncode==0,p.stderr
    blob=(O/'native-fruit-v8.bin').read_bytes();labels={n:int(a,16)for a,n in re.findall(r'^al ([0-9A-Fa-f]+) \.(\S+)$',(O/'native-fruit-v8.lbl').read_text(),re.M)}
    q=dict(passed=True,qualified=False,ROM_written=False,native_owner_admitted=False,base_ROM_SHA256=PIN,component_bytes=len(blob),header_reserved_spare=8160-len(blob),code_SHA256=W.P.sha(blob),labels=labels,native_bindings=prior['native_bindings'],
        source_funding_removed_regions=removed,world_state_measurement_half_open=[0xc400,0xc439],additional_host_RAM_bytes=0,original2KB_state_retyped=True,
        old4xx_direct_reader_count=len(old_direct),indirect_contract='Only original91 fruit pointer may access typed C400..41C records; original02/04 pointer domains remain source descriptors/OAM and native C8 lists. Full finite proof pending before resource admission.',
        remaining=['Current native enemy fruit hit/defeat lifecycle','Body/fruit/points native8x16 OAM/CHR/palette/status','Cold/owner/37row/native contact/event/IRQ resource admission'],
        scope='Unqualified compiled private successor measurement. Direct native score, world fruit projection/removal and camera transport require CPU/source differential proof before use. No actual SMB fruit placement or host resource/menu grant.',
        bindings={p.relative_to(R).as_posix():W.P.sha(p.read_bytes())for p in [Path(__file__),checkpoint/'inputs.zip',O/'native-fruit-v8.s',O/'native-fruit-v8.bin']})
    (O/'native-fruit-v8-layout.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps({k:q[k]for k in ['passed','qualified','component_bytes','header_reserved_spare','code_SHA256','world_state_measurement_half_open','additional_host_RAM_bytes']}))


if __name__=='__main__':main()
