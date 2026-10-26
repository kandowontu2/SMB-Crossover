"""Private faithful AAD0 product and A671 pointer-load inline proposal."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

PARENT='53736e142c6cf568039a3c4927c9356077e3358b7c02fb7b69d3ca72985f2ff6'
HELPER='''; Native TMNT NMI-only helpers in verified originalFF A1B2..A1FF.
; Existing TnFastProduct/Proto ownership applies: neither IRQ nor foreground
; reads the product registers. Reads return the product, never old operands.
.assert *=$a1b2,lderror,"Retain real command vectors and all earlier helpers"
.proc TnTempoProduct
 cpx #2
 bcc Original
 stx $5205
 sta $5206
 lda $5206
 bne Original                 ; Early-carry cases retain literal source loop/X.
 lda $5205
 sec
 sbc z:TnAudioZp+2           ; The accumulator before the ORIGINAL last ADC.
 clc
 adc z:TnAudioZp+2           ; Preserve exact last-ADC V, including signed wrap.
 ldx #0
 jmp $aad7                  ; Real original CMP80 / saturation / writer path.
Original:
 lda z:TnAudioZp+2           ; Proven source entry A==E2; no private RAM added.
 dex
 beq Done
 jmp $aacf                  ; Literal original CLC/ADC/carry/DEX loop.
Done:
 jmp $aad7
.endproc
.proc TnParserPointer
 ; Inline EVERY original AF96 instruction except its call/return overhead.
 ; The original numeric AF96 entry remains genuine for all other callers.
 ldy #0
 lda a:TnAudioRam+$22,x
 sta z:TnAudioZp
 lda a:TnAudioRam+$28,x
 sta z:TnAudioZp+1
 lda a:TnAudioRam+$16,x
 dec a:TnAudioRam+$04,x
 beq Expired
 jmp $a67f                  ; Exact original CPX2 flags/returns and parser body.
Expired:
 jmp $a91f                  ; Exact original command stream handler.
.endproc
.assert *<=$a200,lderror,"Retain genuine A200 duration helper and A300 table"
.export TnTempoProduct,TnParserPointer
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in ['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    before=(a.parent/'candidate.nes').read_bytes();off=16+63*8192
    assert before[off+0x1b2:off+0x200]==bytes([255])*78
    a.output.mkdir(parents=True);source=a.output/'source';shutil.copytree(a.parent/'source',source,ignore=shutil.ignore_patterns('__pycache__'))
    p=source/'src/tmnt-native.inc';old=p.read_text();text=old
    first='  .assert *=$a671,lderror,"Original instruction offset 8671"\n  JSR $af96\n'
    replacement='  .assert *=$a671,lderror,"Original instruction offset 8671"\n  JMP ::TnParserPointer\n'
    assert text.count(first)==1;text=text.replace(first,replacement)
    first='''  .assert *=$aacc,lderror,"Original instruction offset 8acc"
  DEX
  .assert *=$aacd,lderror,"Original instruction offset 8acd"
  .byte $f0,$08 ; BEQ source$8ad7
'''
    replacement='''  .assert *=$aacc,lderror,"Original instruction offset 8acc"
  JMP ::TnTempoProduct
'''
    assert text.count(first)==1;text=text.replace(first,replacement);p.write_text(text)
    p=source/'src/tmnt_audio.s';text=p.read_text();anchor='.include "tmnt_audio_parser.s"\n'
    assert text.count(anchor)==1;p.write_text(text.replace(anchor,anchor+'.include "tmnt_parser_math_next.s"\n'))
    (source/'src/tmnt_parser_math_next.s').write_text(HELPER)
    cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),'--workspace',str(source),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    result=subprocess.run(cmd,cwd=source,capture_output=True,text=True);(a.output/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,(result.stdout+result.stderr)[-4000:]
    after=(a.output/'candidate.nes').read_bytes();bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    changes={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};changes={n:v for n,v in changes.items()if v}
    assert set(changes)=={63}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    names=['src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_math_next.s'];manifest={};patch=''
    for n in names:
        prior=a.parent/'source'/n;current=source/n;manifest[n]=dict(before_sha256=sha(prior)if prior.exists()else None,after_sha256=sha(current))
        patch+=''.join(difflib.unified_diff(prior.read_text().splitlines(True)if prior.exists()else[],current.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    proof=dict(prepared=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        changed_PRG_bytes=changes,verified_FF_helper_span=[0xa1b2,0xa200],all_existing_qualified_symbols_exact=True,
        source_changes=manifest,source_init_play_ticks_APU_and_RAM_unchanged_still_require_tests=True,
        math_new_user_in_existing_Tn_NMI_owner=True,no_foreground_math=True,checker_sha256=sha(Path(__file__)))
    (a.output/'preparation-next.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
