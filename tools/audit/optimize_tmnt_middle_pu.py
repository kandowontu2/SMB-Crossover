"""Admit only the upper nonrolling query before doing any extra work."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v10')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(BASE/'candidate.nes')=='458ec338eb315d198474a40062ac123df6a2f9ec656fb4459a646365d4591d5d'
 s=a.output/'source';shutil.copytree(BASE/'source',s)
 (s/'src/tmnt_middle_probe.s').write_text('''; A32px standing/crouched side interval needs the intervening tile row.
; Lower and rolling calls keep the native query through a direct tail.
.pushseg
.segment "TMNT_COMBAT"
.proc TnSideMiddleProbe
 tya
 and #1
 beq Original
 lda TnSeq
 cmp #$87
 beq Original
 jsr BlockBufferColli_Side
 bne Done
 php
 ldy R2
 cpy #$c0
 bcs No
 tya
 clc
 adc #16
 tay
 lda (R6),y
 beq No
 sta R3
 sty R2
 ldy TnSavedY
 plp
 lda R3
 rts
No:
 ldy TnSavedY
 plp
 lda #0
Done:rts
Original:jmp BlockBufferColli_Side
.endproc
.export TnSideMiddleProbe
.popseg
''')
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2400:]
 (a.output/'preparation.json').write_text(json.dumps(dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_source='src/tmnt_middle_probe.s'),indent=2)+'\n');print(sha(a.output/'candidate.nes'))
if __name__=='__main__':main()
