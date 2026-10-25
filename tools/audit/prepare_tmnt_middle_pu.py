"""Fill the native standing/crouched side-probe gap without a new bank trip."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v9')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False)
 assert sha(BASE/'candidate.nes')=='a91a26f23fa177621725c9a3e8927f308a0a77188576062f32635a5cb3d6e83b'
 s=a.output/'source';shutil.copytree(BASE/'source',s);f=s/'src/tmnt_dispatch.s';v=f.read_text();old='Shift:clc\n adc Player_Y_Position\n sta Player_Y_Position\n ldy TnSavedY\n jsr BlockBufferColli_Side';assert v.count(old)==1
 v=v.replace(old,old.replace('jsr BlockBufferColli_Side','::TnMiddleProbeSpan:\n jsr TnSideMiddleProbe'));f.write_text(v)
 f=s/'src/tmnt.s';v=f.read_text();v+='\n.include "tmnt_middle_probe.s"\n';f.write_text(v)
 (s/'src/tmnt_middle_probe.s').write_text('''; Standing side probes span32px and can straddle a whole16px tile.
; Reuse the exact sampled column and next terrain row on an empty upper
; query. The rolling12px interval already covers a whole row; retain it.
.pushseg
.segment "TMNT_COMBAT"
.proc TnSideMiddleProbe
 jsr BlockBufferColli_Side
 bne Done
 php
 tya
 pha
 lda TnSavedY
 and #1
 beq No
 lda TnSeq
 cmp #$87
 beq No
 ldy R2
 cpy #$c0                     ; never read beyond native row12
 bcs No
 tya
 clc
 adc #16
 tay
 lda (R6),y
 beq No
 sta R3
 sty R2
 pla
 tay
 plp
 lda R3
 rts
No:
 pla
 tay
 plp
 lda #0
Done:rts
.endproc
.export TnSideMiddleProbe
.popseg
''')
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True)
 (a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 q=dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_sources=['src/tmnt.s','src/tmnt_dispatch.s','src/tmnt_middle_probe.s'],first_wrong_native_write='Donatello Hard frame3356: bank10 PC$A2ED changes X2719to2735 after missing thin brick between source top/bottom samples.',scope='Same column, one additional native terrain row on an empty upper query, unchanged roll/lower/nonempty paths, no new RAM. Pending native replay/collision/performance qualification.')
 (a.output/'preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(q['ROM_sha256'])
if __name__=='__main__':main()
