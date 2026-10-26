"""Classify cold projectile first without disturbing incoming C/V for legacy."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

PARENT='5acef8b38585be9ba4dc1396e54be767c8216db6125440d82341a0f26e08fba5'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    a.output.mkdir(parents=True);s=a.output/'source';shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    p=s/'src/tmnt_equipment_shuriken_fast.s';before=p.read_text()
    old=' lda R5\n bne Legacy\n ; Caller retains X=shot slot; R7=1 and R3=0 are fixed before this JSR.\n lda TnShotKind,x\n cmp #2\n bne Legacy\n'
    new=' ; Caller retains X=shot slot; R7=1 and R3=0 are fixed before this JSR.\n ; EOR preserves original C/V for the earliest legacy page rejection.\n lda TnShotKind,x\n eor #2\n bne Legacy\n lda R5\n bne Legacy\n'
    assert before.count(old)==1;p.write_text(before.replace(old,new))
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-3000:]
    oldb,newb=load(a.parent/'candidate.nes'),load(a.output/'candidate.nes')
    assert qualified(a.parent/'candidate.nes').items()<=qualified(a.output/'candidate.nes').items()
    bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    delta={n:sum(x!=y for x,y in zip(bank(oldb['raw'],n),bank(newb['raw'],n)))for n in range(128)};delta={n:v for n,v in delta.items()if v}
    assert set(delta)=={87}and oldb['raw'][:16]==newb['raw'][:16]and oldb['raw'][1048592:]==newb['raw'][1048592:]
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n')
    (a.output/'review.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),p.read_text().splitlines(True),fromfile='a/src/tmnt_equipment_shuriken_fast.s',tofile='b/src/tmnt_equipment_shuriken_fast.s')))
    q=dict(prepared=True,source_only=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,candidate_ROM_sha256=sha(a.output/'candidate.nes'),
        changed_PRG_bytes=delta,all_old_qualified_symbols_exact=True,source_file='src/tmnt_equipment_shuriken_fast.s',
        source_before_sha256=sha(a.parent/'source/src/tmnt_equipment_shuriken_fast.s'),source_after_sha256=sha(p),checker_sha256=sha(Path(__file__)))
    (a.output/'fast-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
