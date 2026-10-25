"""Private C28 steady ice/lightning proposal; no native or deployment claim."""
from pathlib import Path
import argparse, hashlib, json, re, shutil, subprocess, sys
from check_tmnt_render_oa import load, address

ROOT = Path(__file__).resolve().parents[2]
D = Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
PARENT = D/'cv3-remaining-stubs-v2/qualified-v1/source-final'
PARENT_ROM = PARENT.parent/'candidate.nes'
HELD = '2e005c8e2acde44bc184459d92b2966ee488b92819dd91151577fdf444b751df'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();out=a.output.resolve();assert not out.is_relative_to(ROOT);out.mkdir(parents=True,exist_ok=False)
 assert sha(PARENT_ROM)==HELD
 stage=out/'source';shutil.copytree(PARENT,stage)
 f=stage/'src/cv3_remaining_source_fx.s';original=f.read_bytes();s=original.decode();assert '\r'not in s
 old=load(PARENT_ROM)
 full=s.index('Full:php');end=s.index('.endproc',full)
 s=s[:full]+'''Full:jmp Cv3FxResidentDispatch
 .res 67-(*-::Cv3FxTick),$ea
'''+s[end:]
 # Avoid redundant zero writes when the corresponding pending request is known
 # zero. The nonzero/rejected paths still clear it once at the original owner.
 s=s.replace('Pending:lda Cv3FxPendingNoise\n beq PulseAdmission', 'Pending:lda Cv3FxPendingNoise\n beq PulseAlreadyClear',1)
 s=s.replace('PulseAdmission:lda #0\n sta Cv3FxPendingNoise\n lda Cv3FxPendingPulse\n beq Noise', 'PulseAdmission:lda #0\n sta Cv3FxPendingNoise\nPulseAlreadyClear:lda Cv3FxPendingPulse\n beq Pulse',1)
 s=s.replace(' jsr Peek\n cmp #255', ' ldy #0\n lda (R0),y\n cmp #255')
 # The preceding AND supplies A=0 on an unowned-noise branch. Both running and
 # unowned paths now fall into the actual shared R0/R1 return, avoiding a second
 # owned-mask test. NoiseRelease remains a real out-of-line block.
 s=s.replace('NoiseTick:lda Cv3FxOwned\n and #8\n beq Done', 'NoiseTick:lda Cv3FxOwned\n and #8\n beq Done',1)
 tail_start=s.index('NoiseRunning:lda #$80');tail_end=s.index('FindIndex:ldy #6',tail_start)
 s=s[:tail_start]+'''NoiseRunning:lda #$80
Done:sta Cv3NoiseActive
Return:pla
 sta R1
 pla
 sta R0
 rts
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
 jmp Done
 .assert *-::Cv3FxService<='''+str(address(old,'FindIndex')-address(old,'Cv3FxService'))+''',error,"Original helper boundary"
 .res '''+str(address(old,'FindIndex')-address(old,'Cv3FxService'))+'''-(*-::Cv3FxService),$ea
'''+s[tail_end:]
 # Pull the original real native packet operands into fixed tables. Every
 # pointer still advances to the SAME old A82 packet PC, never to these tables.
 packets=[]
 for i in range(43):
  m=re.search(r'Cv3Fx21NoiseFrame'+f'{i:03d}'+r':\n lda #(\d+)(?:\n ldx #(\d+))?\n jmp Cv3FxFrameNoise(Full|Volume)',s);assert m,(i,'original native packet')
  packets.append((int(m[1]),int(m[2])if m[2]else 0,m[3]))
 assert all(r[2]=='Full'for r in packets[:42])and packets[42][2]=='Volume'
 resident='''
; C28 resident steady source21/1E. The real generic owner handles admission,
; mixed pulse/noise, priority, release and every non-steady state.
.proc Cv3FxResidentDispatch
 php
 pha
 tya
 pha
 lda CurrentBank
 sta Cv3FxSavedA
 lda Cv3FxOwned
 cmp #8
 bne Generic
 lda Cv3FxNoiseID
 beq Generic
 cmp #$21
 beq Pending
 cmp #$1e
 bne Generic
Pending:lda AvAudioRequest
 bne Generic
 lda Cv3FxPendingNoise
 ora Cv3FxPendingPulse
 bne Generic
 jsr Cv3FxResidentNoise
 jmp Restore
Generic:txa ; resident-only work never touches X, so only the fallback saves it
 pha
 lda #.bank(Cv3FxService)|MMC5_PRG_ROM
 sta CurrentBank
 sta $5115
 jsr Cv3FxService
 lda Cv3FxSavedA
 sta CurrentBank
 sta $5115
 pla
 tax
Restore:pla
 tay
 pla
 plp
 rts
.endproc
.proc Cv3FxResidentNoise
 lda GuestNativeDirty+12
 beq NC12
 lda GuestNativeApu+12
 sta Cv3NoiseMusicVolume
 lda Cv3NoiseApu
 sta GuestNativeApu+12
 lda #0
 sta GuestNativeDirty+12
NC12:lda GuestNativeDirty+14
 beq NC14
 lda GuestNativeApu+14
 sta Cv3NoiseMusicPeriod
 lda Cv3NoiseApu+2
 sta GuestNativeApu+14
 lda #0
 sta GuestNativeDirty+14
NC14:lda GuestNativeDirty+15
 beq NC15
 lda GuestNativeApu+15
 sta Cv3NoiseMusicHigh
 lda Cv3NoiseApu+3
 sta GuestNativeApu+15
 lda #0
 sta GuestNativeDirty+15
NC15:ldy Cv3NoiseIndex
 lda Cv3FxResidentVolume,y
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
 lda #1
 sta GuestNativeDirty+15
 lda Cv3FxResidentPeriod,y
 sta GuestNativeApu+14
 sta Cv3NoiseApu+2
 lda #1
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
 lda #$80
 sta Cv3NoiseActive
 rts
.endproc
Cv3FxResidentVolume:.byte '''+','.join(str(r[0])for r in packets)+'''
Cv3FxResidentPeriod:.byte '''+','.join(str(r[1])for r in packets[:42])+'''
'''
 insert=s.index('.assert *<=$dc00');s=s[:insert]+resident+s[insert:]
 f.write_bytes(s.encode())
 shutil.copyfile(PARENT_ROM,out/'baseline.nes');shutil.copyfile(PARENT_ROM.with_suffix('.dbg'),out/'baseline.dbg');shutil.copyfile(PARENT_ROM.with_suffix('.lbl'),out/'baseline.lbl')
 cmd=[sys.executable,str(stage/'tools/build_mmc5_expanded.py'),'--workspace',str(stage),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(out/'candidate.nes')]
 with(out/'build.host.log').open('w')as log:r=subprocess.run(cmd,cwd=stage,stdout=log,stderr=subprocess.STDOUT)
 assert not r.returncode,(out/'build.host.log').read_text()[-7000:]
 result=dict(passed=True,accepted=False,ROM_sha256=sha(out/'candidate.nes'),parent_ROM_sha256=HELD,source_path=str(stage),new_RAM=0,resident_packets_source='Actual 42 full C/F/E native packets plus final C-volume silence from frozen2e source21;1E shared source stream.',source21_packets=packets,modified_source_sha256=sha(f),tool_sha256=sha(__file__))
 (out/'prepared.json').write_text(json.dumps(result,indent=2)+'\n');shutil.copyfile(__file__,out/Path(__file__).name);print(json.dumps(result,indent=2))

if __name__=='__main__':main()
