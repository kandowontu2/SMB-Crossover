"""Private256-physical-slot/logical64 queue proposal; no native or adoption."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load
from cv3_remaining_sfx_queue_prepare_v8 import replace,proc
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-queue-v8/qualified-v1/source-final'
ROM=PARENT.parent/'candidate.nes'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--unsafe-cold-control',action='store_true');a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(ROM)=='7b0a2cbdd806ff057d86c1af1834ecac5d34e1bb1747852e93d6ca2ec3d2fec2';stage=a.output/'source';shutil.copytree(PARENT,stage);b=load(ROM)
 f=stage/'src/cv3_remaining_source_fx.s';s=f.read_bytes().decode();assert '\r'not in s;s=s.replace('Cv3FxQueue=RgAudioZp+64 ;64 committed cue bytes, within the existing160-byte lane','Cv3FxQueue=RgAudioRam+$100 ;256 physical slots, logical capacity64; CV1 upper RAM unused')
 s=replace(s,'Cv3FxOwnerInit',''' sta Cv3DmcPending
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Clear
 lda GamePauseStatus
 and OperMode
 and #1
 bne Done
Clear:lda #0
 sta Cv3NoiseActive
 sta Cv3FxOwned
 sta Cv3FxSourceHigh
 lda Cv3FxQueueHead
 sta Cv3FxQueueTail
Done:rts
''',38)
 # Unowned IDs are scratch, never active voices. Clear before priority reads.
 s=replace(s,'Cv3FxDrain',''' lda Cv3FxOwned
 and #8
 bne NoiseKnown
 lda #0
 sta Cv3FxNoiseID
NoiseKnown:lda Cv3FxOwned
 and #1
 bne PulseKnown
 lda #0
 sta Cv3FxPulseID
PulseKnown:lda AvAudioRequest
 cmp #26
 bne Begin
 lda Cv3FxPendingNoise
 cmp #$1f
 bcs Begin
 lda #$1f
 sta Cv3FxPendingNoise
Begin:ldy Cv3FxQueueTail
 cpy Cv3FxQueueHead
 beq Done
Loop:lda Cv3FxQueue,y
 cmp #8
 beq Cancel
 tax
 ; Every authenticated source cue1..7 owns noise. Pulse is table bit0.
 lda Cv3FxRawIDs,x
 cmp Cv3FxPendingNoise
 bcc Pulse
 sta Cv3FxPendingNoise
Pulse:lda Cv3FxRawMasks,x
 lsr
 bcc Consumed
 lda Cv3FxRawIDs,x
 cmp Cv3FxPendingPulse
 bcc Consumed
 sta Cv3FxPendingPulse
 jmp Consumed
Cancel:jsr Cv3FxCancelConsumer
Consumed:iny
 cpy Cv3FxQueueHead
 bne Loop
 sty Cv3FxQueueTail
Done:lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 beq Return
 lda Cv3FxPendingPulse
 bne Full
 lda Cv3FxPendingNoise
 cmp #$1f
 bne Full
 lda Cv3FxOwned
 and #9
 bne Full
 ; Paused/muted requests are folded but never ticked or exposed as Av26
 ; to the common decoder. Their original pending priority survives resume.
 lda GamePauseStatus
 and #1
 bne Full
 lda RgAudioSilenced
 bne Full
 lda AvAudioRequest
 beq Legacy
 cmp #26
 bcc DiscardLegacy
 cmp #33
 bcc Legacy
DiscardLegacy:lda #0
 sta Cv3FxPendingNoise
 rts
Legacy:lda #0
 sta Cv3FxPendingNoise
 lda #26
 sta AvAudioRequest
Return:rts
Full:lda Cv3FxOwned
 ora #$80
 sta Cv3FxOwned
 lda Cv3NoiseActive
 cmp #1
 bne Dispatch
 lda Cv3NoiseIndex
 cmp #28
 bcs Dispatch
 lda #$1f
 sta Cv3FxNoiseID
 lda Cv3FxOwned
 ora #$48
 sta Cv3FxOwned
Dispatch:lda #$80
 sta Cv3NoiseActive
 rts
''')
 # Checked genuine compatibility entry retains invalid-input/full behavior.
 s=replace(s,'Cv3FxProducer',''' sta Cv3ShotType,x
 cmp #1
 bcc Done
 cmp #7
 bcs Done
 ldy AvAudioRequest
 beq WorldClear
 cpy #26
 bcc Done
 cpy #33
 bcs Done
WorldClear:pha
 lda Cv3FxQueueHead
 sec
 sbc Cv3FxQueueTail
 cmp #64
 bcs Full
 ldy Cv3FxQueueHead
 pla
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
Done:rts
Full:pla
 inc Cv3FxQueueOverflow
 rts
''')
 start,end=proc(s,'Cv3FxQueueCommand');part=s[start:end];assert part.count(' and #63')==2;part=part.replace(' and #63','');part=part.replace(' lda Cv3FxQueueHead\n tay\n pla',' ldy Cv3FxQueueHead\n pla');s=s[:start]+part+s[end:]
 s=s.replace('; Counters are full bytes; only the slot address is masked. Neither reset nor','; Counters and physical slot indexes are full bytes. Neither reset nor')
 s+='''
.pushseg
.segment "CV3_COMBAT"
; Sole actual caller has constant1..6 and at most21 outstanding commands after
; the NMI mute consumer/cancel-run proof. Checked public entry remains above.
.proc Cv3FxProducerFast
 sta Cv3ShotType,x
 ldy AvAudioRequest
 beq WorldClear
 cpy #26
 bcc Done
 cpy #33
 bcs Done
WorldClear:ldy Cv3FxQueueHead
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
Done:rts
.endproc
.segment "CV3_GRIP"
Cv3FxRawIDs:.byte 0,$13,$15,$24,$21,$1e,$1f,$2f
Cv3FxRawMasks:.byte 0,8,8,9,9,9,8,9
.assert *<=$c000,lderror,"Declared remaining A82 source space"
.segment "CV_AUDIO"
.proc Cv3FxMuteGate
 php
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Empty
 jsr Cv3FxDrainGate
Empty:plp
 lda #0
 jmp GuestNativeStatusSTA
.endproc
.assert *<=$dc00,lderror,"Declared remaining C28 source space"
.popseg
''';f.write_bytes(s.encode())
 f=stage/'src/cv3_combat.s';raw=f.read_bytes();assert raw.count(b'jsr Cv3FxProducer')==1;f.write_bytes(raw.replace(b'jsr Cv3FxProducer',b'jsr Cv3FxProducerFast'))
 f=stage/'src/roster_audio.s';raw=f.read_bytes();assert b'\r'not in raw;s=raw.decode()
 if not a.unsafe_cold_control:
  s=s.replace('  sta RgAudioRam,x\n  sta RgAudioRam+$100,x','''  sta RgAudioRam,x
.if Kind=2 .and ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jmp KeptUpper ; upper channel RAM is the committed FX queue, never CV1 state
.else
  sta RgAudioRam+$100,x
.endif''',1)
  s=s.replace('  .res 12,$ea ; exact original18-byte Save body','''KeptUpper:
  inx
  bne ClearRam
  ldx #ZpCount-1
  jmp ClearZp
  .res 4,$ea ; genuine8-byte cold continuation in old unreachable12-byte tail''',1)
 s=s.replace('Mute:\n  lda #0\n  jsr GuestNativeStatusSTA','''Mute:
.if Kind=2 .and ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5
  jsr Cv3FxMuteGate
  .res 2,$ea ; unchanged5-byte original mute owner span
.else
  lda #0
  jsr GuestNativeStatusSTA
.endif''',1);f.write_bytes(s.encode())
 for ext in['.nes','.dbg','.lbl']:shutil.copyfile(ROM.with_suffix(ext),a.output/('baseline'+ext))
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
 with(a.output/'build.host.log').open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(a.output/'build.host.log').read_text()[-6000:]
 result=dict(passed=True,accepted=False,status='ASSEMBLED_SOURCE_ONLY_NEW_PROTOCOL_NOT_QUALIFIED',ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(ROM),source=str(stage),physical_slots=256,logical_capacity=64,unsafe_cold_control=a.unsafe_cold_control,unowned_ID_representation='IDs are only valid when corresponding Owned bit is set; consumer clears unowned IDs before priority admission.',source_files=[dict(path=f.relative_to(stage).as_posix(),sha256=sha(f))for f in(stage/'src').glob('*.s')if f.read_bytes()!=(PARENT/f.relative_to(stage)).read_bytes()],tool_sha256=sha(__file__))
 (a.output/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,a.output/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
