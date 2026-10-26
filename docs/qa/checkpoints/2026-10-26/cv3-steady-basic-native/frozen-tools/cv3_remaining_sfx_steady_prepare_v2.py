"""Private faithful steady-noise fast path on frozen0c45, source/CPU only."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT=D/'cv3-remaining-queue256-v1/qualified-v3'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(PARENT/'candidate.nes')=='0c45ce16fa189debc2303f4df664a0e75f326a807a64bf23280797734615339c';source=a.output/'source';shutil.copytree(PARENT/'source-final',source);f=source/'src/cv3_remaining_source_fx.s';raw=f.read_bytes();assert b'\r'not in raw;s=raw.decode();assert s.count(' bmi Full\n')==1;s=s.replace(' bmi Full\n',' bmi Steady\n',1);s=s.replace('Full:jmp Cv3FxResidentDispatch\n','Full:jmp Cv3FxResidentDispatch\nSteady:jmp Cv3FxSteadyTry\n',1)
 start=s.index('.proc Cv3FxResidentNoise\n');end=s.index('.endproc',start)+len('.endproc');old=s[start:end];new='''.proc Cv3FxResidentNoise
 ; Genuine old callable entry/span: pure body plus original normalization.
 jsr Cv3FxResidentBody
 lda #$80
 sta Cv3NoiseActive
 rts
 ; Sole private entry is Tick's BMI path. A is the negative Active byte.
 ; P is saved before checks; a non80 value falls back with exact originalA/P.
::Cv3FxSteadyTry:
 php
 cmp #$80
 bne Slow
 lda Cv3FxOwned
 cmp #8
 bne Slow
 lda Cv3FxNoiseID
 cmp #$21
 beq Pending
 cmp #$1e
 bne Slow
Pending:lda AvAudioRequest
 ora Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne Slow
 ; SavedA is dead bank-cache scratch on this C28-only path. Generic always
 ; dominates its bank-restore read with its own CurrentBank write.
 sty Cv3FxSavedA
 jsr Cv3FxResidentBody
 ldy Cv3FxSavedA
 lda #$80 ; inputA proven80; Active remains80; V/C/DI restored byPLP
 plp
 rts
Slow:lda Cv3NoiseActive
 pha
 tya
 pha
 lda CurrentBank
 sta Cv3FxSavedA
 jmp Cv3FxResidentDispatch::Generic
 .assert *-::Cv3FxResidentNoise<=149,error,"Old genuine callable span"
 .res 149-(*-::Cv3FxResidentNoise),$ea
.endproc''';s=s[:start]+new+s[end:]
 marker='.assert *<=$dc00,lderror,"Declared remaining C28 source space"';assert s.count(marker)==1;body='''.proc Cv3FxResidentBody
 ; All-zero dirty state avoids three separate taken branches. If music
 ; wrote fields, cache exact new music values before original source emission.
 lda GuestNativeDirty+12
 ora GuestNativeDirty+14
 ora GuestNativeDirty+15
 beq Ready
 lda GuestNativeDirty+12
 beq P
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
P:lda GuestNativeDirty+14
 beq H
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
H:lda GuestNativeDirty+15
 beq FinalCheck
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
FinalCheck:ldy Cv3NoiseIndex
 cpy #42
 bne Emit
 ; The final source frame writes volume only. Reproduce the original
 ; pre-emission restoration/clear of any music period/high writes exactly.
 lda GuestNativeDirty+14
 beq FH
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
FH:lda GuestNativeDirty+15
 beq Emit
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
 jmp Emit
Ready:ldy Cv3NoiseIndex
Emit:lda Cv3FxResidentVolume,y
 sta GuestNativeApu+12
 sta Cv3NoiseApu
 lda #1
 sta GuestNativeDirty+12
 cpy #42
 beq Final
 lda Cv3FxSourceHigh
 ora #8
 sta GuestNativeApu+15
 sta Cv3NoiseApu+3
 lda Cv3FxResidentPeriod,y
 sta GuestNativeApu+14
 sta Cv3NoiseApu+2
 lda #1
 sta GuestNativeDirty+15
 sta GuestNativeDirty+14
 lda #7
 bne Commit
Final:lda #0
 sta Cv3FxNoiseID
 lda #5
Commit:clc
 adc Cv3FxNoisePtr
 sta Cv3FxNoisePtr
 bcc NoCarry
 inc Cv3FxNoisePtr+1
NoCarry:inc Cv3NoiseIndex
 rts
.endproc
''';s=s.replace(marker,body+marker,1);f.write_bytes(s.encode());(a.output/'old-resident-noise.s.txt').write_text(old,encoding='utf-8',newline='\n')
 for ext in['.nes','.dbg','.lbl']:shutil.copyfile(PARENT/('candidate'+ext),a.output/('baseline'+ext))
 cmd=[sys.executable,str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
 with(a.output/'build.host.log').open('w')as log:z=subprocess.run(cmd,cwd=source,stdout=log,stderr=subprocess.STDOUT)
 assert not z.returncode,(a.output/'build.host.log').read_text()[-6000:];r=dict(prepared=True,native_executed=False,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(a.output/'baseline.nes'),source=str(source),changed_source_file='src/cv3_remaining_source_fx.s',changed_source_sha256=sha(f),dead_private_scratch_exception='RgAudioZp52 SavedA stores savedY on successful steady route; Generic reads remain dominated by its own bank-cache write. Must prove all consumers/IRQ before qualification.',genuine_public_Noise_entry_and149B_span_retained=True,source_effect_stores_ticks_queue_priority_unchanged=True,scope='Assembled private optimization only. Need complete exact values/state/ordinary/publicABI/priority/queue/IRQ/cost/native qualification. No production edits or adoption.',tool_sha256=sha(__file__));(a.output/'prepared.json').write_text(json.dumps(r,indent=2)+'\n');shutil.copyfile(__file__,a.output/Path(__file__).name);print(json.dumps(r,indent=2))
if __name__=='__main__':main()
