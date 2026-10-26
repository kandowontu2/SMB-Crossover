"""Finite readonly channel-index lookup on frozen1346; all joined flags exact."""
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

PARENT='13463703ea95e769f332acecbcc0d35ef066f4ddd22624fa3fa771d5773fe60d'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    b=load(a.parent/'candidate.nes');end=address(b,'TnFastDuration')+int(b['syms']['TnFastDuration']['size'],0)
    start=location(b,'TnFastDuration')+int(b['syms']['TnFastDuration']['size'],0)
    assert b['raw'][start:start+6]==bytes([255])*6 and end+6<=0xa300
    cfg=(a.parent/'source/smb1base-mmc5-expanded.cfg').read_text()
    assert 'TN_DURATION_MEM:start=$a200,size=$0100,type=ro' in cfg
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    path=s/'src/tmnt-native.inc';old=path.read_text();lo=old.index('  .assert *=$a65e,lderror,"Original instruction offset 865e"')
    hi=old.index('  .assert *=$a66d,lderror,"Original instruction offset 866d"',lo)
    oldspan=old[lo:hi]
    replacement='''  .assert *=$a65e,lderror,"Original instruction offset 865e"
  LDY ::TnNativeChannelOffsets,x
  CPX #5 ; Identical C:0for1..4,1for5. V/D/I remain untouched.
  TYA    ; Identical final A/N/Z as original offset arithmetic.
  JMP $a64b
  .res 6,$ff ; Unreachable; retain all original later numeric entries.
'''
    path.write_text(old[:lo]+replacement+old[hi:])
    path=s/'src/tmnt_audio.s';text=path.read_text();anchor='.include "tmnt_parser_math_next.s"\n'
    assert text.count(anchor)==1;path.write_text(text.replace(anchor,anchor+'.include "tmnt_parser_channels.s"\n'))
    (s/'src/tmnt_parser_channels.s').write_text('''; Immutable original six-channel register mapping; no music data removed.
.pushseg
.segment "TMNT_DURATION_HELPER"
TnNativeChannelOffsets:
 .byte 0,4,8,12,0,12
.assert TnNativeChannelOffsets>=$a200 && *<=$a300,lderror,"Declared duration-helper FF tail only"
.export TnNativeChannelOffsets
.popseg
''')
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-3000:]
    before,after=b['raw'],(a.output/'candidate.nes').read_bytes();bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    changed={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};changed={n:v for n,v in changed.items()if v}
    assert set(changed)=={63}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    c=load(a.output/'candidate.nes');assert address(c,'TnNativeChannelOffsets')==end
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    manifest={};patch=''
    for n in['src/tmnt-native.inc','src/tmnt_audio.s','src/tmnt_parser_channels.s']:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p)if p.exists()else None,after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True)if p.exists()else[],q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    proof=dict(prepared=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        changed_PRG_bytes=changed,verified_linker_FF_table=[end,end+6],all_old_qualified_symbols_exact=True,
        source_changes=manifest,actual_caller_golden_IRQ_qualification_pending=True,checker_sha256=sha(Path(__file__)))
    (a.output/'channels-preparation.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
