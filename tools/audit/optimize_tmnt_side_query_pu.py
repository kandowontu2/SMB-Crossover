"""Specialize the original generic query's known player object and side mode."""
from pathlib import Path
import argparse,hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BASE=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-tmnt-combined-pu/candidate-v11')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output.mkdir(parents=True,exist_ok=False);assert sha(BASE/'candidate.nes')=='48aacd558eca5d54890b15f4073643897a0e35a733020c1fc228fdffc86b2d68'
 s=a.output/'source';shutil.copytree(BASE/'source',s);f=s/'src/tmnt_middle_probe.s';v=f.read_text();assert v.count('jsr BlockBufferColli_Side')==1 and v.count('jmp BlockBufferColli_Side')==1
 v=v.replace('jsr BlockBufferColli_Side','jsr TnNativeSideQuery').replace('jmp BlockBufferColli_Side','jmp TnNativeSideQuery')
 v+='''
; This private caller always requests player object0 and horizontal output.
; Retain every native pointer/row/nibble result and arithmetic flag; omit
; only the generic mode push/pop/branch and object-indexed loads.
.pushseg
.segment "TMNT_COMBAT"
.proc TnNativeSideQuery
.if ::MAPPER_MMC5
 ldx #0
 sty R4
 lda BlockBuffer_X_Adder,y
 clc
 adc Player_X_Position
 sta R5
 lda Player_PageLoc
 adc #0
 and #1
 tay
 lda #>Block_Buffer_1
 sta R7
 lda R5
 lsr
 lsr
 lsr
 lsr
 clc
 adc BlockBufferAddr,y
 sta R6
 ldy R4
 lda Player_Y_Position
 clc
 adc BlockBuffer_Y_Adder,y
 and #$f0
 sec
 sbc #$20
 sta R2
 tay
 lda (R6),y
 sta R3
 ldy R4
 lda Player_X_Position
 and #15
 sta R4
 lda R3
 rts
.else
 jmp BlockBufferColli_Side
.endif
.endproc
.export TnNativeSideQuery
.popseg
''';f.write_text(v)
 z=subprocess.run([sys.executable,str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')],cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(z.stdout+z.stderr);assert z.returncode==0,(z.stdout+z.stderr)[-2500:]
 (a.output/'preparation.json').write_text(json.dumps(dict(prepared=True,accepted=False,ROM_sha256=sha(a.output/'candidate.nes'),parent_ROM_sha256=sha(BASE/'candidate.nes'),changed_source='src/tmnt_middle_probe.s'),indent=2)+'\n');print(sha(a.output/'candidate.nes'))
if __name__=='__main__':main()
