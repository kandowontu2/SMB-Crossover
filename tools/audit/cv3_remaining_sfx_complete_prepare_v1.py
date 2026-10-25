"""Private complete original CV3 per-voice overlay; frozen4c70 parent only."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-dmc-complete-v1/final-optimized-current8ff-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(p,old,new):
 b=p.read_bytes();eol='\r\n'if b'\r\n'in b else'\n';s=b.decode().replace('\r\n','\n');assert s.count(old)==1,(p,old);p.write_bytes(s.replace(old,new).replace('\n',eol).encode())
C='''; Complete source13/15/24/21/1E/2F plus retained source1F.
; Same selected-family160B slab;0..35 keep all existing owners.
Cv3FxNoiseID=RgAudioZp+36
Cv3FxPulseID=RgAudioZp+37
Cv3FxOwned=RgAudioZp+38 ;1pulse,8noise,64promote legacy1F,128new request
Cv3FxPulseFrame=RgAudioZp+39
Cv3FxPulseApu=RgAudioZp+40
Cv3FxPulseMusic=RgAudioZp+44
Cv3FxNoisePtr=RgAudioZp+48
Cv3FxPulsePtr=RgAudioZp+50
Cv3FxSavedA=RgAudioZp+52
Cv3FxPendingNoise=RgAudioZp+53 ; independent same-update source requests
Cv3FxPendingPulse=RgAudioZp+54
Cv3FxSourceHigh=RgAudioZp+55 ; original shared source frequency-high image
.pushseg
.segment "CV_AUDIO"
.proc Cv3FxTick
 jsr Cv3DmcBeforeCv1
 lda Cv3NoiseActive
 bmi Full
 bne Legacy
 lda Cv3FxOwned
 bne Full
 lda AvAudioRequest
 cmp #26
 beq Legacy
 lda #0 ; match old final active load/register flags for ordinary requests
 rts
Legacy:jmp Cv3MusicAndNoiseTick+3 ; unchanged executable legacy body
Full:php
 pha
 txa
 pha
 tya
 pha
 lda CurrentBank
 sta Cv3FxSavedA
 lda #.bank(Cv3FxService)|MMC5_PRG_ROM
 sta CurrentBank
 sta $5115
 jsr Cv3FxService
 lda Cv3FxSavedA
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
.proc Cv3FxMusicInit
 php
 pha
 lda Cv3NoiseActive
 cmp #1
 bne Cancel ; only genuine legacy1F needs conversion into an owned noise image
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
 lda #$80
 sta Cv3NoiseActive
Cancel:lda #0
 sta Cv3FxNoiseID
 sta Cv3FxPulseID
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 sta Cv3FxSourceHigh
 lda AvAudioRequest
 cmp #26
 bcc Done
 cmp #33
 bcs Done
 lda #0
 sta AvAudioRequest
Done:pla
 plp
 jmp CvAudioInit
.endproc
.proc Cv3FxLegacyNoiseHigh
 lda Cv3FxSourceHigh
 ora #8
 sta Cv3NoiseApu+3
 rts
.endproc
.assert *<=$dc00,lderror,"Only recorded original CV1 C28 slack"
.segment "X5_AUDIO_MIX"
.proc Cv3FxOwnerInit
 sta Cv3DmcPending ; original surrounding reset owns flags and supplies A=0
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Clear
 lda GamePauseStatus
 and OperMode
 and #1
 bne Done
Clear:lda #0
 sta Cv3NoiseActive
 sta Cv3FxNoiseID
 sta Cv3FxPulseID
 sta Cv3FxOwned
 sta Cv3FxSourceHigh
Done: ; enclosing original reset immediately reloads A; no new public return
 rts
.endproc
.assert *<=$c000,lderror,"Only remaining38B X5 mixer tail"
.segment "CV3_COMBAT"
.proc Cv3FxSpawn
 sta Cv3ShotType,x
 php
 pha
 txa
 pha
 tya
 pha
 lda Cv3ShotType,x
 cmp #1
 bcc Done
 cmp #7
 bcs Done
 cmp #6
 bne Sub
 lda #26
 bne Queue
Sub:clc
 adc #26
Queue:tay
 lda AvAudioRequest
 beq Initialize
 cmp #26
 bcc Done ; common world/typed requests retain existing port precedence
 cmp #33
 bcs Done
Initialize:lda Cv3FxOwned
 bne Admit
 lda #0 ; no owned/pending complete voice: discard cold inactive scratch
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 lda AvAudioRequest
 cmp #26
 bne Admit
 lda #$1f ; a previous same-update legacy request also owns its priority
 sta Cv3FxPendingNoise
Admit:tya
 cmp #26
 bne NewCue
 lda Cv3FxOwned
 bne NewCue
 lda #26 ; retain old native1F fast path and its public active/index ABI
 sta AvAudioRequest
 jmp Done
NewCue:tya ; owned-mask test above must not replace the pending typed request
 sta AvAudioRequest
 sec
 sbc #26
 tax
 lda Cv3FxQueueMasks,x
 and #8
 beq PendingPulse
 lda Cv3FxQueueIDs,x
 cmp Cv3FxPendingNoise
 bcc PendingPulse
 sta Cv3FxPendingNoise
PendingPulse:lda Cv3FxQueueMasks,x
 and #1
 beq Mark
 lda Cv3FxQueueIDs,x
 cmp Cv3FxPendingPulse
 bcc Mark
 sta Cv3FxPendingPulse
Mark:
 lda Cv3FxOwned
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
Done:pla
 tay
 pla
 tax
 pla
 plp
 rts
.endproc
Cv3FxQueueIDs:.byte $1f,$13,$15,$24,$21,$1e,$2f
Cv3FxQueueMasks:.byte 8,8,8,9,9,9,9
.segment "CV3_GRIP"
.proc Cv3FxBatEnter
 php
 lda #32
 sta AvAudioRequest ; source2F highest of the implemented pulse/noise cues
 lda #$2f
 sta Cv3FxPendingNoise
 sta Cv3FxPendingPulse
 lda Cv3FxOwned
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
 plp
 lda #1
 sta Cv3Bat
 rts
.endproc
.proc Cv3FxSceneRequest
 php ; real original Cv3DmcSceneRequest PHP displaced into this prelude
 jsr Cv3FxCancel
 lda #0
 jmp Cv3DmcSceneRequest+3 ; original STA pending and original remaining body
.endproc
.proc Cv3FxCancel
 lda Cv3NoiseActive
 cmp #1
 bne IDs ; a pending80 marker has not borrowed the native music image
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
 lda AvAudioRequest
 cmp #26
 bcc Done
 cmp #33
 bcs Done
 lda #0
 sta AvAudioRequest
Done:rts
.endproc
.proc Cv3FxDeathDispatch
 php
 pha
 txa
 pha
 tya
 pha
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Done
 lda Cv3Variant
 beq Done
 cmp #4
 bcs Done
 jsr Cv3FxCancel
Done:pla
 tay
 pla
 tax
 pla
 plp
 farcall RlDeathStartDispatch,jmp
.endproc
.proc Cv3FxService
 lda R0
 pha
 lda R1
 pha
 ; The source update has already run. Capture only its genuinely dirty
 ; owned registers, suppress them in the current FX image, and keep music
 ; advancing at its original cadence underneath each independently owned voice.
 lda Cv3FxOwned
 and #$40
 beq Capture
 ldy Cv3NoiseIndex
 lda Cv3FxLegacyOffsets,y
 clc
 adc #<Cv3Fx1FNoise
 sta Cv3FxNoisePtr
 lda #>Cv3Fx1FNoise
 adc #0
 sta Cv3FxNoisePtr+1
Capture:lda Cv3FxOwned
 and #8
 beq PulseCapture
'''
C=C.replace(' bcc Done',' jcc Done').replace(' bcs Done',' jcs Done')
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(PARENT/'candidate.nes')=='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da';stage=out/'source';shutil.copytree(PARENT/'source-final',stage);b=load(PARENT/'candidate.nes');s=C
 # The old noise-only body remains executable at all original labels; its
 # public entry now selects complete vs genuine unchanged legacy service.
 f=stage/'src/cv3_source_audio.s';replace(f,' jsr Cv3DmcBeforeCv1',' jmp Cv3FxTick')
 size=int(b['syms']['Cv3SpawnAudioType']['size'],0);old='''.proc Cv3SpawnAudioType
 sta Cv3ShotType,x
 cmp #6
 bne Done
 lda AvAudioRequest
 bne Done
 lda #26
 sta AvAudioRequest
Done:rts
.endproc'''
 replace(f,old,f'''.proc Cv3SpawnAudioType
.if ::MAPPER_MMC5
 jmp Cv3FxSpawn
 .res {size-3},$ea
.else
 sta Cv3ShotType,x
 cmp #6
 bne Done
 lda AvAudioRequest
 bne Done
 lda #26
 sta AvAudioRequest
Done:rts
.endif
.endproc''')
 replace(f,' lda #8\n sta Cv3NoiseApu+3',' .if ::MAPPER_MMC5\n jsr Cv3FxLegacyNoiseHigh\n .res 2,$ea\n .else\n lda #8\n sta Cv3NoiseApu+3\n .endif')
 replace(stage/'src/cv3_dmc_complete.s',' sta Cv3DmcPending ; original two call sites both supply A=0',' jsr Cv3FxOwnerInit ; fixed original3B span, original outer PHP owns status')
 replace(stage/'src/cv3_dmc_complete.s','.proc Cv3DmcSceneRequest\n php\n lda #0','.proc Cv3DmcSceneRequest\n jmp Cv3FxSceneRequest ; original PHP/LDA0 relocated, following PCs exact')
 f=stage/'src/roster_audio.s';replace(f,'  jsr CvAudioInit\n.endif\nEffects:',' .if ::ENABLE_MMC5_EXPANDED .and ::MAPPER_MMC5\n  jsr Cv3FxMusicInit\n .else\n  jsr CvAudioInit\n .endif\n.endif\nEffects:')
 f=stage/'src/megaman_death.s';replace(f,'  farcall RlDeathStartDispatch',' .if ::MAPPER_MMC5\n  farcall Cv3FxDeathDispatch\n .else\n  farcall RlDeathStartDispatch\n .endif')
 f=stage/'src/cv3_abilities.s';replace(f,' lda #1\n sta Cv3Bat\n lda #36\n sta Cv3BatTransform\n jmp Still\nNo:',' .if ::MAPPER_MMC5\n jsr Cv3FxBatEnter\n .res 2,$ea\n .else\n lda #1\n sta Cv3Bat\n .endif\n lda #36\n sta Cv3BatTransform\n jmp Still\nNo:')
 for off,cache,img in [(12,'Cv3NoiseMusicVolume','Cv3NoiseApu'),(14,'Cv3NoiseMusicPeriod','Cv3NoiseApu+2'),(15,'Cv3NoiseMusicHigh','Cv3NoiseApu+3')]:
  s+=f''' lda GuestNativeDirty+{off}
 beq NC{off}
 lda GuestNativeApu+{off}
 sta {cache}
 lda {img}
 sta GuestNativeApu+{off}
 lda #0
 sta GuestNativeDirty+{off}
NC{off}:
'''
 s+='PulseCapture:lda Cv3FxOwned\n and #1\n beq Admit\n'
 for off in range(4):
  s+=f''' lda GuestNativeDirty+{off}
 beq PC{off}
 lda GuestNativeApu+{off}
 sta Cv3FxPulseMusic+{off}
 lda Cv3FxPulseApu+{off}
 sta GuestNativeApu+{off}
 lda #0
 sta GuestNativeDirty+{off}
PC{off}:
'''
 s+='''Admit:lda Cv3FxOwned
 and #9
 sta Cv3FxOwned
 lda AvAudioRequest
 cmp #26
 bcc Pending
 cmp #33
 bcs Pending
 sec
 sbc #26
 tay
 lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne ClearRequest
 lda Cv3FxMasks,y
 and #8
 beq SeedPulse
 lda Cv3FxIDs,y
 sta Cv3FxPendingNoise
SeedPulse:lda Cv3FxMasks,y
 and #1
 beq ClearRequest
 lda Cv3FxIDs,y
 sta Cv3FxPendingPulse
ClearRequest:
 lda #0
 sta AvAudioRequest
Pending:lda Cv3FxPendingNoise
 beq PulseAdmission
 cmp Cv3FxNoiseID
 bcc PulseAdmission
 jsr FindIndex
 lda Cv3FxOwned
 and #8
 bne NewNoise
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
NewNoise:lda Cv3FxPendingNoise
 sta Cv3FxNoiseID
 lda Cv3FxNoiseLo,y
 sta Cv3FxNoisePtr
 lda Cv3FxNoiseHi,y
 sta Cv3FxNoisePtr+1
 lda #0
 sta Cv3NoiseIndex
 lda Cv3FxOwned
 ora #8
 sta Cv3FxOwned
PulseAdmission:lda #0
 sta Cv3FxPendingNoise
 lda Cv3FxPendingPulse
 beq Noise
 cmp Cv3FxPulseID
 bcc Noise
 jsr FindIndex
 lda Cv3FxOwned
 and #1
 bne NewPulse
 ldx #3
PM:lda GuestNativeApu,x
 sta Cv3FxPulseMusic,x
 dex
 bpl PM
NewPulse:lda Cv3FxPendingPulse
 sta Cv3FxPulseID
 lda Cv3FxPulseLo,y
 sta Cv3FxPulsePtr
 lda Cv3FxPulseHi,y
 sta Cv3FxPulsePtr+1
 lda #0
 sta Cv3FxPulseFrame
 lda Cv3FxOwned
 ora #1
 sta Cv3FxOwned
Noise:lda #0
 sta Cv3FxPendingPulse
 lda Cv3FxOwned
 and #8
 beq Pulse
 lda Cv3FxNoiseID
 beq NoiseRelease
 lda Cv3FxNoisePtr
 sta R0
 lda Cv3FxNoisePtr+1
 sta R1
 jsr Decode
 lda R0
 sta Cv3FxNoisePtr
 lda R1
 sta Cv3FxNoisePtr+1
 inc Cv3NoiseIndex
 jsr Peek
 cmp #255
 bne NoiseRunning
 lda #0
 sta Cv3FxNoiseID ; original priority clears on the final silence frame
NoiseRunning:lda #$80
 sta Cv3NoiseActive
 jmp Pulse
NoiseRelease:lda Cv3NoiseMusicVolume
 sta GuestNativeApu+12
 lda Cv3NoiseMusicPeriod
 sta GuestNativeApu+14
 lda Cv3NoiseMusicHigh
 sta GuestNativeApu+15
 lda #1
 sta GuestNativeDirty+12
 sta GuestNativeDirty+14
 sta GuestNativeDirty+15
 lda Cv3FxOwned
 and #$f7
 sta Cv3FxOwned
 lda #0
 sta Cv3NoiseActive
Pulse:lda Cv3FxOwned
 and #1
 beq Done
 lda Cv3FxPulseID
 beq PulseRelease
 lda Cv3FxPulsePtr
 sta R0
 lda Cv3FxPulsePtr+1
 sta R1
 jsr Decode
 lda R0
 sta Cv3FxPulsePtr
 lda R1
 sta Cv3FxPulsePtr+1
 inc Cv3FxPulseFrame
 jsr Peek
 cmp #255
 bne Done
 lda #0
 sta Cv3FxPulseID
 beq Done
PulseRelease:ldx #3
PR:lda Cv3FxPulseMusic,x
 sta GuestNativeApu,x
 lda #1
 sta GuestNativeDirty,x
 dex
 bpl PR
 lda Cv3FxOwned
 and #$fe
 sta Cv3FxOwned
Done:lda Cv3FxOwned
 and #8
 bne Return
 lda #0
 sta Cv3NoiseActive ; pulse-only ownership must leave native noise alone
Return:pla
 sta R1
 pla
 sta R0
 rts
FindIndex:ldy #6
Find:cmp Cv3FxIDs,y
 beq Found
 dey
 bpl Find
Found:rts
Decode:jsr Read
 cmp #254
 beq Decoded
 tax
 jsr Read
 sta GuestNativeApu,x
 cpx #12
 bcc PulseImage
 sta Cv3NoiseApu-12,x
 jmp Dirty
PulseImage:sta Cv3FxPulseApu,x
Dirty:lda #1
 sta GuestNativeDirty,x
 jmp Decode
Decoded:rts
Read:jsr Peek
 inc R0
 bne ByteDone
 inc R1
ByteDone:rts
Peek:ldy #0
 lda (R0),y
 rts
.endproc
Cv3FxIDs:.byte $1f,$13,$15,$24,$21,$1e,$2f
Cv3FxMasks:.byte 8,8,8,9,9,9,9
'''
 # Source secondary pulse executes before source secondary noise. Keep the
 # original shared frequency-high image for raw400F low bits across effects.
 start=s.index('Noise:lda #0\n sta Cv3FxPendingPulse\n')
 end=s.index('Done:lda Cv3FxOwned\n and #8\n',start)
 block=s[start:end];split=block.index('Pulse:lda Cv3FxOwned\n')
 noise=block[:split].replace('Noise:lda #0\n sta Cv3FxPendingPulse\n lda Cv3FxOwned','NoiseTick:lda Cv3FxOwned',1).replace(' beq Pulse\n',' beq Done\n').replace(' jmp Pulse\n',' jmp Done\n')
 pulse=block[split:].replace('Pulse:','Noise:lda #0\n sta Cv3FxPendingPulse\nPulse:',1).replace(' beq Done\n',' beq NoiseTick\n').replace(' bne Done\n',' bne NoiseTick\n')
 s=s[:start]+pulse+noise+s[end:]
 s=s.replace(' jsr Read\n sta GuestNativeApu,x\n cpx #12',' jsr Read\n cpx #15\n bne Store\n lda Cv3FxSourceHigh\n ora #8\nStore:sta GuestNativeApu,x\n cpx #12',1)
 s=s.replace('PulseImage:sta Cv3FxPulseApu,x\nDirty:', 'PulseImage:sta Cv3FxPulseApu,x\n cpx #3\n bne Dirty\n and #7\n sta Cv3FxSourceHigh\nDirty:',1)
 # Exact source byte streams, including sparse frames and release silences.
 gold=D/'cv3-remaining-sfx-v1/source-v2';receipt=json.loads((gold/'proof.json').read_text());streams={};offsets=None
 for event in[0x1f,0x13,0x15,0x24,0x21,0x2f]:
  file=gold/f'event-{event:02x}-apu.csv';assert sha(file)==next(r['trace_sha256']for r in receipt['captures']if r['id']==event);rows=list(csv.DictReader(file.open()))
  for voice,regs in[('Noise',[12,14,15]),('Pulse',[0,1,2,3])]:
   ws=[(int(r['frame']),int(r['address'])-0x4000,int(r['value']))for r in rows if int(r['address'])-0x4000 in regs]
   if not ws:continue
   last=max(r[0]for r in ws);data=[];frames=[]
   for frame in range(last+1):
    frames.append(len(data))
    for fr,reg,val in ws:
     if fr==frame:data +=[reg,val]
    data.append(254)
   frames.append(len(data));data.append(255);streams[(event,voice)]=data;s+=f'Cv3Fx{event:02X}{voice}:.byte '+','.join(map(str,data))+'\n'
   if event==0x1f:offsets=frames
 assert sum(map(len,streams.values()))==1072
 for voice in['Noise','Pulse']:
  labels=[f'Cv3Fx{event:02X}{voice}'if(event,voice)in streams else'0'for event in[0x1f,0x13,0x15,0x24,0x21,0x21,0x2f]]
  s+=f'Cv3Fx{voice}Lo:.byte '+','.join('<'+n if n!='0'else'0'for n in labels)+'\n';s+=f'Cv3Fx{voice}Hi:.byte '+','.join('>'+n if n!='0'else'0'for n in labels)+'\n'
 s+='Cv3FxLegacyOffsets:.byte '+','.join(map(str,offsets))+'\n.assert *<=$c000,lderror,"Complete sourceFX inside recorded A82 slack"\n.popseg\n';(stage/'src/cv3_remaining_source_fx.s').write_text(s,newline='\n')
 replace(stage/'src/entrypoint.s','.include "cv3_dmc_complete.s"','.include "cv3_dmc_complete.s"\n.include "cv3_remaining_source_fx.s"')
 for ext in['.nes','.dbg','.lbl','.map']:shutil.copyfile(PARENT/('candidate'+ext),out/('baseline'+ext))
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.host.log').open('w')as f:r=subprocess.run(cmd,cwd=stage,stdout=f,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.host.log').read_text()[-8000:]
 proof=dict(passed=True,accepted=False,ROM_sha256=sha(out/'candidate.nes'),baseline_ROM_sha256=sha(out/'baseline.nes'),source_stream_bytes=1072,new_RAM_allocation=0,new_selected_family_slab_offsets=[36,56],scope='Private complete per-voice source build only; assembled exact streams/priority/lifecycle/ordinary/cycles/IRQ and native qualification not yet run.')
 (out/'proposal.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof,indent=2))
if __name__=='__main__':main()
