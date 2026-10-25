"""Avoid the ordinary APU owner loop when only MMC5 pulses have effects."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(BASE/'candidate.nes')=='45ea5b8ece3b5a596df1fb6aa2dede011547c667774610853f776e159834d69d'
 s=a.output/'source';shutil.copytree(BASE/'source',s);f=s/'src/guest_audio.s';v=f.read_text();old='  lda GuestMixMask\n  ora GuestMixChanged\n  bne MixedChannels';assert v.count(old)==1
 v=v.replace(old,'''  lda GuestMixMask
.if ::ENABLE_MMC5_EXPANDED
::X5NativeNoiseSpan:
  jsr X5NativeNoiseMask
.else
  ora GuestMixChanged
.endif
  bne MixedChannels''');f.write_text(v)
 f=s/'src/tmnt_audio_resident.s';v=f.read_text();v+='''
; Ordinary pulse effects are already mixed/flushed to MMC5 voices.
; Only the noise owner/change can alter the native APU register image.
::X5NativeNoiseMask:
 ora a:GuestMixChanged
 and #8
 rts
.export X5NativeNoiseMask
''';f.write_text(v)
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True)
 (a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 q=dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_sources=['src/guest_audio.s','src/tmnt_audio_resident.s'],scope='MMC5 expansion pulses do not own ordinary APU pulses. Same native flush when no noise ownership/change; three-byte callsite retained. Pending full mixer differential and native timing.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'])
if __name__=='__main__':main()
