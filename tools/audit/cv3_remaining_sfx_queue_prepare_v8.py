"""Private finite SPSC request publication proposal; source/CPU only, no adoption."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys
from check_tmnt_render_oa import load,address

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-resident-v4/qualified-v1/source-final'
ROM=D/'cv3-remaining-resident-v4/candidate.nes'
HELD='0802527d8a2e0cf8f9584e854d6dd263b72e330c3c89d30921abddc1b10c5790'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def proc(s,name):
 start=s.index('.proc '+name+'\n');end=s.index('.endproc',start)+len('.endproc');return start,end
def replace(s,name,body,size=None):
 start,end=proc(s,name)
 pad=(' .assert *-::'+name+'<='+str(size)+',error,"Retained original callable span"\n .res '+str(size)+'-(*-::'+name+'),$ea\n')if size else''
 return s[:start]+'.proc '+name+'\n'+body+pad+'.endproc'+s[end:]

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(ROM)==HELD
 stage=out/'source';shutil.copytree(PARENT,stage);b=load(ROM)
 f=stage/'src/cv3_remaining_source_fx.s';s=f.read_bytes().decode();assert '\r'not in s
 s=s.replace('Cv3FxSourceHigh=RgAudioZp+55 ; original shared source frequency-high image','''Cv3FxSourceHigh=RgAudioZp+55 ; original shared source frequency-high image
; Main is the sole head/slot producer; NMI is the sole tail consumer.
; Counters are full bytes; only the slot address is masked. Neither reset nor
; an interrupted NMI rewrites producer head. Tail=head discards a cold epoch.
Cv3FxQueueHead=RgAudioZp+56
Cv3FxQueueTail=RgAudioZp+57
Cv3FxQueueOverflow=RgAudioZp+58 ; impossible in the bounded gameplay producer graph
Cv3FxQueue=RgAudioZp+64 ;64 committed cue bytes, within the existing160-byte lane''')
 # Queue work is admitted inside the NMI-owned service. A busy main producer
 # never locks or postpones an already active source voice.
 s=s.replace(' jsr Cv3DmcBeforeCv1\n lda Cv3NoiseActive',''' jsr Cv3DmcBeforeCv1
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Empty
 jsr Cv3FxDrainGate
Empty:lda Cv3NoiseActive''',1)
 # Music reset runs in the consumer. Discard only committed work, retaining
 # any producer interrupted before its final head publication.
 s=s.replace('Cancel:lda #0\n sta Cv3FxNoiseID','Cancel:lda Cv3FxQueueHead\n sta Cv3FxQueueTail\n lda #0\n sta Cv3FxNoiseID',1)
 # Keep the original66-byte span; the old range test can be factored out into
 # the new cold consumer helper without moving following public entries.
 start,end=proc(s,'Cv3FxMusicInit');part=s[start:end]
 old=' lda AvAudioRequest\n cmp #26\n jcc Done\n cmp #33\n jcs Done\n lda #0\n sta AvAudioRequest\nDone:pla'
 assert old in part;part=part.replace(old,' jsr Cv3FxClearTyped\nDone:pla');part=part[:-len('.endproc')]+(' .res 66-(*-::Cv3FxMusicInit),$ea\n.endproc');s=s[:start]+part+s[end:]
 # Both real parent callers overwrite X before reading it; Y remains live.
 # Input A=0
 # is preserved by LDX/CPX on the non-Simon arm; AND#1 supplies A=0 on Clear.
 # The DMC32..35 lane is not touched by the expanded clear loop.
 s=replace(s,'Cv3FxOwnerInit',''' sta Cv3DmcPending
 ldx SelectedCharacter
 cpx #CHARACTER_SIMON
 bne Clear
 lda GamePauseStatus
 and OperMode
 and #1
 bne Done
Clear:sta Cv3NoiseActive
 ldx #19
Loop:sta Cv3FxNoiseID,x
 dex
 bpl Loop
 lda Cv3FxQueueHead
 sta Cv3FxQueueTail
Done:rts
''',38)
 # Keep the old compatibility entry genuine. The sole gameplay JSR targets
 # Producer directly; A/Y/flags are dead there, X and D/I remain live.
 s=replace(s,'Cv3FxSpawn',''' php
 pha
 tya
 pha
 jsr Cv3FxProducer
 pla
 tay
 pla
 plp
 rts
''',191)
 s=replace(s,'Cv3FxBatEnter',''' php
 tya
 pha
 lda #7
 jsr Cv3FxQueueCommand
 pla
 tay
 plp
 lda #1
 sta Cv3Bat
 rts
''',int(b['syms']['Cv3FxBatEnter']['size'],0))
 s=replace(s,'Cv3FxCancel',''' tya
 pha
 lda #8
 jsr Cv3FxQueueCommand
 pla
 tay
 rts
''',int(b['syms']['Cv3FxCancel']['size'],0))
 # Drain before Capture: this is the only owner of pending/voice/Owned writes.
 # DrainGate runs before the existing dispatch, so Service and every source
 # frame keep their exact old PCs and instruction bodies.
 # Retain every source-frame helper address; the service has explicit internal
 # slack before FindIndex. Its last padding absorbs the added JSR.
 # Appended helpers occupy only documented A84/A82 free tails.
 at=s.rfind('.assert *<=$c000')
 helpers='''
; NMI is the only consumer. It is never preempted by another audio owner.
; Process all committed commands before advancing either source voice once.
.proc Cv3FxDrain
 lda AvAudioRequest
 cmp #26
 bne Loop
 lda Cv3FxPendingNoise
 cmp #$1f
 bcs Loop
 lda #$1f
 sta Cv3FxPendingNoise
Loop:lda Cv3FxQueueTail
 cmp Cv3FxQueueHead
 jeq Done
 and #63
 tay
 lda Cv3FxQueue,y
 cmp #8
 jeq Cancel
 cmp #1
 jcc Consumed
 cmp #8
 jcs Consumed
 cmp #6
 bne Index
 lda #0
 beq Mapped
Index:cmp #7
 bne Mapped
 lda #6
Mapped:tay
Admit:lda Cv3FxMasks,y
 and #8
 beq Pulse
 lda Cv3FxIDs,y
 cmp Cv3FxPendingNoise
 bcc Pulse
 sta Cv3FxPendingNoise
Pulse:lda Cv3FxMasks,y
 and #1
 beq Mark
 lda Cv3FxIDs,y
 cmp Cv3FxPendingPulse
 bcc Mark
 sta Cv3FxPendingPulse
Mark:jmp Consumed
Cancel:jsr Cv3FxCancelConsumer
Consumed:inc Cv3FxQueueTail
 jmp Loop
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
 lda AvAudioRequest
 beq Legacy
 cmp #26
 beq Legacy
 lda #0
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
.endproc
.proc Cv3FxCancelConsumer
 lda Cv3NoiseActive
 cmp #1
 bne IDs
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
 lda #$80
 sta Cv3NoiseActive
IDs:lda #0
 sta Cv3FxNoiseID
 sta Cv3FxPulseID
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 jsr Cv3FxClearTyped
 rts
.endproc
; A=7 bat or8 cancel. Main writes the slot before publishing head LAST.
; Full rejection is only a defensive invalid-domain behavior: it neither
; overwrites committed data nor publishes a partially written command.
.proc Cv3FxQueueCommand
 pha
 cmp #8
 bne Room
 lda Cv3FxQueueHead
 cmp Cv3FxQueueTail
 beq Room
 sec
 sbc #1
 and #63
 tay
 lda Cv3FxQueue,y
 cmp #8
 beq Duplicate
Room:
 lda Cv3FxQueueHead
 sec
 sbc Cv3FxQueueTail
 cmp #64
 bcs Full
 lda Cv3FxQueueHead
 and #63
 tay
 pla
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
 rts
Full:pla
 inc Cv3FxQueueOverflow
 rts
Duplicate:pla
 rts
.endproc
'''
 # Producer remains in its caller's actual A84 bank; every cue publishes solely
 # through this committed ring. Legacy1F is selected only by the NMI consumer.
 producer='''
.segment "CV3_COMBAT"
.proc Cv3FxProducer
 sta Cv3ShotType,x
 cmp #1
 bcc Done
 cmp #7
 bcs Done
 lda AvAudioRequest
 beq WorldClear
 cmp #26
 bcc Done
 cmp #33
 bcs Done
WorldClear:lda Cv3FxQueueHead
 sec
 sbc Cv3FxQueueTail
 cmp #64
 bcs Full
 lda Cv3FxQueueHead
 and #63
 tay
 lda Cv3ShotType,x
 sta Cv3FxQueue,y
 inc Cv3FxQueueHead
Done:rts
Full:inc Cv3FxQueueOverflow
 rts
.endproc
.segment "CV_AUDIO"
.proc Cv3FxDrainGate
 php
 pha
 txa
 pha
 tya
 pha
 lda CurrentBank
 pha
 lda #.bank(Cv3FxDrain)|MMC5_PRG_ROM
 sta CurrentBank
 sta $5115
 jsr Cv3FxDrain
 pla
 sta CurrentBank
 sta $5115
 pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
.proc Cv3FxClearTyped
 lda AvAudioRequest
 cmp #26
 bcc Done
 cmp #33
 bcs Done
 lda #0
 sta AvAudioRequest
Done:rts
.endproc
'''
 s=s[:at]+helpers+s[at:]+producer
 # Correct mapped indices: raw1..5 correspond to table1..5, raw6 to0,7 to6.
 f.write_bytes(s.encode())
 f=stage/'src/cv3_combat.s';raw=f.read_bytes();assert raw.count(b'jsr Cv3SpawnAudioType')==1;f.write_bytes(raw.replace(b'jsr Cv3SpawnAudioType',b'jsr Cv3FxProducer'))
 # MMC3 keeps its original call; this source is shared by flag-off builds.
 raw=f.read_bytes();eol=b'\r\n'if b'\r\n'in raw else b'\n';raw=raw.replace(b' jsr Cv3FxProducer',eol.join([b'.if ::MAPPER_MMC5',b' jsr Cv3FxProducer',b'.else',b' jsr Cv3SpawnAudioType',b'.endif']));f.write_bytes(raw)
 f=stage/'src/cv3_source_audio.s';s=f.read_bytes().decode();start,end=proc(s,'Cv3NoiseSceneReset');old=s[start:end];size=int(b['syms']['Cv3NoiseSceneReset']['size'],0)
 replacement='''.proc Cv3NoiseSceneReset
.if ::MAPPER_MMC5
 php
 jsr Cv3DmcSceneRequest
 plp
 lda Cv3Variant
 rts
 .res '''+str(size)+'''-(*-::Cv3NoiseSceneReset),$ea
.else
'''+old.split('.proc Cv3NoiseSceneReset\n',1)[1].replace('.if ::MAPPER_MMC5\n jsr Cv3DmcSceneRequest\n.else\n lda AvAudioRequest\n.endif',' lda AvAudioRequest')[:-len('.endproc')]+'.endif\n.endproc';s=s[:start]+replacement+s[end:];f.write_bytes(s.encode())
 # Existing bank7 is byte-exact. Actual CV3 never publishes generic Fireball;
 # the CV1 wrapper ignores it and shared GuestWorldQueues excludes it.
 for name in['baseline.nes','baseline.dbg','baseline.lbl']:shutil.copyfile(ROM.with_suffix(Path(name).suffix),out/name)
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.host.log').open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.host.log').read_text()[-6000:]
 result=dict(passed=True,accepted=False,status='ASSEMBLED_PROTOCOL_PROPOSAL_CPU_UNQUALIFIED',ROM_sha256=sha(out/'candidate.nes'),held_parent_ROM_sha256=HELD,source_path=str(stage),new_private_lane_offsets=[56,57,58]+list(range(64,128)),new_allocated_RAM_CHR=0,queue_capacity=64,source_files=[dict(path=str(p.relative_to(stage)),sha256=sha(p))for p in(stage/'src').glob('*.s')if(PARENT/p.relative_to(stage)).read_bytes()!=p.read_bytes()],tool_sha256=sha(__file__))
 (out/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,out/Path(__file__).name);print(json.dumps(result,indent=2))
if __name__=='__main__':main()
