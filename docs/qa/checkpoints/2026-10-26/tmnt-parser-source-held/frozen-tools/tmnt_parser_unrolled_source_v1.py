"""Unroll the exact six-voice schedule; retain every call/store/flag join."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address,location
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

PARENT='66b911f3a937d3d749b3a88d9e6ba8b1b56b8f2d56c5b16b9317273b13dc20fb'
HELPER='''; Same six source voices/calls/order and all RAM92/RAM93 stores.
.pushseg
.segment "TMNT_DURATION_HELPER"
.proc TnNativeUnrolled
 jsr $a612
 ldx #0
 ldy #0
.repeat 6,I
 stx a:TnAudioRam+$92
 sty a:TnAudioRam+$93
 lda a:TnAudioRam+$0a,x
 beq :+
 jsr $a671
:
 inx
.if I<5
 .if I=4
  ldy #12
 .else
  ldy #(((I+1)*4)&15)
 .endif
 cpx #5
 tya
.else
 cpx #6
.endif
.endrepeat
 rts
.endproc
.assert TnNativeUnrolled=$a221,lderror,"Append only declaredFF after readonly channel table"
.assert *<=$a300,lderror,"Retain complete original products table and moved source stream"
.export TnNativeUnrolled
.popseg
'''


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    b=load(a.parent/'candidate.nes');off=16+63*8192
    assert b['raw'][off+0x221:off+0x300]==bytes([255])*223
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    p=s/'src/tmnt-native.inc';text=p.read_text();old='  .assert *=$a644,lderror,"Original instruction offset 8644"\n  JSR $a612\n'
    assert text.count(old)==1;p.write_text(text.replace(old,'  .assert *=$a644,lderror,"Original instruction offset 8644"\n  JMP ::TnNativeUnrolled\n'))
    p=s/'src/tmnt_audio.s';text=p.read_text();anchor='.include "tmnt_parser_channels.s"\n'
    assert text.count(anchor)==1;p.write_text(text.replace(anchor,anchor+'.include "tmnt_parser_unrolled.s"\n'))
    (s/'src/tmnt_parser_unrolled.s').write_text(HELPER)
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    result=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,(result.stdout+result.stderr)[-3000:]
    after=(a.output/'candidate.nes').read_bytes();before=b['raw'];bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    changes={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};changes={n:v for n,v in changes.items()if v}
    assert set(changes)=={63}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    manifest={};patch=''
    for n in['src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_unrolled.s']:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch);c=load(a.output/'candidate.nes')
    q=dict(prepared=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        changed_PRG_bytes=changes,verified_original_FF_span=[0xa221,0xa300],new_real_helper_PC=address(c,'TnNativeUnrolled'),
        helper_bytes=int(c['syms']['TnNativeUnrolled']['size'],0),all_old_qualified_symbols_exact=True,
        all_six_voice_calls_and_stores_retained_qualification_pending=True,source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'unrolled-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
