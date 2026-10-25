"""Private MMC5 dagger/axe extension of the existing authentic noise lane."""
from pathlib import Path
import argparse,csv,hashlib,json,shutil,subprocess,sys
from check_tmnt_render_oa import load,address
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-dmc-complete-v1/final-optimized-current8ff-v2'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def replace(p,old,new):
 raw=p.read_bytes();eol='\r\n'if b'\r\n'in raw else'\n';s=raw.decode().replace('\r\n','\n');assert s.count(old)==1,(p,old);p.write_bytes(s.replace(old,new).replace('\n',eol).encode())
HELPERS='''; Internal typed27/28 are consumed by the private CV3 noise lane before
; common RemainingAudioTick. Each real spawn applies original source priority.
Cv3NoiseCue=RgAudioZp+36 ; original CV1 uses0..23, noise24..31, DMC32..35
.pushseg
.segment "CV3_COMBAT"
.proc Cv3NoiseCueSpawn
 sta Cv3ShotType,x
 php
 pha
 tya
 pha
 lda Cv3ShotType,x
 cmp #1
 beq Dagger
 cmp #2
 beq Axe
 cmp #6
 bne Done
 lda AvAudioRequest
 beq Fireball
 cmp #27
 beq Fireball
 cmp #28
 bne Done
Fireball:lda #26
 sta AvAudioRequest ; original1F supersedes pending13/15, keeps world priority
 jmp Done
Dagger:ldy #$13
 bne Pending
Axe:ldy #$15
Pending:lda AvAudioRequest
 beq Running
 cmp #27
 beq Running
 cmp #28
 bne Done ; existing typed world request retains its current port priority
 cpy #$15
 bcc Done
Running:lda Cv3NoiseActive
 beq Admit
 lda Cv3NoiseIndex
 cmp #28
 bcs Admit ; original voice already released after its last source frame
 lda Cv3NoiseCue
 beq Done ; zero represents existing1F, above13/15
 cpy Cv3NoiseCue
 bcc Done
Admit:cpy #$13
 bne AxeRequest
 lda #27
 bne Store
AxeRequest:lda #28
Store:sta AvAudioRequest
Done:pla
 tay
 pla
 plp
 rts
.endproc
.segment "X5_AUDIO_MIX"
; Existing reset sites supply A=0. Pause holds the existing noise phase;
; character/menu reset drops owned noise and initializes the new private byte.
.proc Cv3NoiseCueOwnerInit
 sta Cv3DmcPending
 php
 lda SelectedCharacter
 cmp #CHARACTER_SIMON
 bne Clear
 lda GamePauseStatus
 and #1
 bne Done
Clear:lda #0
 sta Cv3NoiseCue
 sta Cv3NoiseActive
Done:plp
 lda #0
 rts
.endproc
.assert *<=$c000,lderror,"Use only the remaining X5 audio tail"
.segment "CV_AUDIO"
.proc Cv3NoiseCueReset
 php
 lda AvAudioRequest
 cmp #27
 beq Dagger
 cmp #28
 beq Axe
 lda #0
 sta Cv3NoiseCue
 ldy #0
 beq Clear
Dagger:lda #$13
 sta Cv3NoiseCue
 ldy #15 ;13 source frames at the tail of the original28-frame phase window
 bne Clear
Axe:lda #$15
 sta Cv3NoiseCue
 ldy #11 ;17 source frames, no added silence or shortened source sound
Clear:lda #0
 sta AvAudioRequest
 tya
 plp
 rts
.endproc
'''
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False);assert sha(PARENT/'candidate.nes')=='4c70fe485f73fb8d437fae2e79ae8ddad83908dc26d4008f21e0a2abeccee2da';stage=out/'source';shutil.copytree(PARENT/'source-final',stage);b=load(PARENT/'candidate.nes')
 f=stage/'src/cv3_source_audio.s';old='''.proc Cv3SpawnAudioType
 sta Cv3ShotType,x
 cmp #6
 bne Done
 lda AvAudioRequest
 bne Done
 lda #26
 sta AvAudioRequest
Done:rts
.endproc''';size=int(b['syms']['Cv3SpawnAudioType']['size'],0)
 replace(f,old,f'''.proc Cv3SpawnAudioType
.if ::MAPPER_MMC5
 jmp Cv3NoiseCueSpawn
 .res {size-3},$ea ; fixed original helper span; obsolete private Done removed
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
 replace(f,' cmp #26\n bne Owner',' cmp #26\n.if ::MAPPER_MMC5\n bcc Owner ; internal27/28 must also be canceled at an actual scene reset\n.else\n bne Owner\n.endif')
 replace(f,' cmp #26\n bne Continue',' cmp #26\n.if ::MAPPER_MMC5\n bcc Continue ; same idle/ordinary path cost, new27/28 use private noise reset\n.else\n bne Continue\n.endif')
 replace(f,'Reset:lda #0\n sta AvAudioRequest','Reset:lda #0\n.if ::MAPPER_MMC5\n jsr Cv3NoiseCueReset\n.else\n sta AvAudioRequest\n.endif')
 for key in ['Flags','Periods']:replace(f,f' lda Cv3Noise{key},y',f'.if ::MAPPER_MMC5\n jsr Cv3NoiseCue{key}\n.else\n lda Cv3Noise{key},y\n.endif')
 replace(f,'Volume:lda Cv3NoiseVolumes,y','Volume:\n.if ::MAPPER_MMC5\n jsr Cv3NoiseCueVolumes\n.else\n lda Cv3NoiseVolumes,y\n.endif')
 replace(stage/'src/cv3_dmc_complete.s',' sta Cv3DmcPending ; original two call sites both supply A=0',' jsr Cv3NoiseCueOwnerInit ; same three-byte span; both original sites supply A=0')
 data={};text=HELPERS
 for key in ['Flags','Periods','Volumes']:
  text+=f'''.proc Cv3NoiseCue{key}
 lda Cv3NoiseCue
 beq Legacy
 and #2 ;hex13 has bit1, hex15 does not; preserve carry/overflow and X/Y
 beq Axe
 lda Cv3NoiseDagger{key},y
 rts
Axe:lda Cv3NoiseAxe{key},y
 rts
Legacy:lda Cv3Noise{key},y
 rts
.endproc
'''
 source=D/'cv3-remaining-sfx-v1/source-v2';receipt=json.loads((source/'proof.json').read_text())
 for event,name,start in [(0x13,'Dagger',15),(0x15,'Axe',11)]:
  file=source/f'event-{event:02x}-apu.csv';assert sha(file)==next(r['trace_sha256']for r in receipt['captures']if r['id']==event);writes=[[]for _ in range(28-start)]
  for r in csv.DictReader(file.open()):writes[int(r['frame'])].append((int(r['address']),int(r['value'])))
  arrays={key:[0]*28 for key in ['Flags','Periods','Volumes']};volume=period=0
  for i,ws in enumerate(writes,start):
   values=dict(ws);assert all(a in[0x400c,0x400e,0x400f]for a,v in ws)
   if 0x400c in values:volume=values[0x400c];arrays['Flags'][i]|=1
   if 0x400e in values:assert values[0x400f]==8;period=values[0x400e];arrays['Flags'][i]|=2
   arrays['Volumes'][i]=volume;arrays['Periods'][i]=period
  for key,values in arrays.items():text+=f'Cv3Noise{name}{key}: .byte '+','.join(map(str,values))+'\n'
  data[str(event)]=dict(start_phase=start,frames=len(writes),source_trace_sha256=sha(file),arrays=arrays)
 text+=' .assert *<=$dc00,lderror,"Stay inside recorded original CV1 slack"\n.popseg\n';(stage/'src/cv3_noise_cues.s').write_text(text,newline='\n')
 replace(stage/'src/entrypoint.s','.include "cv3_dmc_complete.s"','.include "cv3_dmc_complete.s"\n.include "cv3_noise_cues.s"')
 for suffix in ['.nes','.dbg','.lbl','.map']:shutil.copyfile(PARENT/('candidate'+suffix),out/('baseline'+suffix))
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.host.log').open('w')as f:r=subprocess.run(cmd,cwd=stage,stdout=f,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.host.log').read_text()[-6000:]
 (out/'noise-source-data.json').write_text(json.dumps(data,indent=2)+'\n');result=dict(passed=True,source_prepared_only=True,accepted=False,baseline_sha256=sha(out/'baseline.nes'),candidate_sha256=sha(out/'candidate.nes'),effects=[0x13,0x15],remaining_multivoice=[0x24,0x21,0x1e,0x2f],cross_existing_CV1_owner_retained=True,source_files={name:sha(stage/name)for name in['src/cv3_source_audio.s','src/cv3_dmc_complete.s','src/cv3_noise_cues.s','src/entrypoint.s']},removed_private_label=['Cv3SpawnAudioType','Done'],scope='Private source build only. Original noise data and lifecycle hooks prepared; assembled owner/APU/priority/cycle/IRQ and ordinary differentials still required. No native worker.')
 (out/'proposal.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
