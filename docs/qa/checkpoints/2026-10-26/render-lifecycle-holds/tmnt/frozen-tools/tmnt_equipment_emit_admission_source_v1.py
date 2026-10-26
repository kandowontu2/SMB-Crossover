"""Short source-owned emitter admissions; retain cold-path cost negatives."""
from pathlib import Path
import argparse
import difflib
import json
import shutil
import subprocess
import sys
from check_tmnt_render_oa import load,address
from check_tmnt_audio_fallback_oc import qualified
from tmnt_native_storage_driver import ROOT,sha

PARENT='c1957666f674ead536e7382913fae08f4ad840a1428bc41ecdfd5ce5a2580d68'


def main():
    p=argparse.ArgumentParser(description=__doc__)
    for n in['parent','output']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();assert sha(a.parent/'candidate.nes')==PARENT
    assert not a.output.exists()and not a.output.resolve().is_relative_to(ROOT)
    old=load(a.parent/'candidate.nes');a.output.mkdir(parents=True);s=a.output/'source'
    shutil.copytree(a.parent/'source',s,ignore=shutil.ignore_patterns('__pycache__'))
    capacity=lambda n:f' ldx CurrentOAMOffset\n lda #{n}\n clc\n adc CurrentOAMOffset\n bcc :+\n jmp TnWorldDraw\n:\n'
    p=s/'src/tmnt_equipment_icon_fast.s';text=p.read_text();lo=text.index('.proc TnExactIconRender\n')+len('.proc TnExactIconRender\n');hi=text.index('Legacy:',lo)
    body=[' ; Only the original icon JSR calls here: X is its immutable right',
        ' ; table index (Equipment+79), and R4/R5/R6/R7/R3=128/0/23/1/0.',
        ' lda CurrentOAMOffset',' cmp #240',' bcs Legacy']
    for i in range(4):body += [f' cpx #{80+i}',f' beq Icon{i}Gate']
    text=text[:lo]+'\n'.join(body)+'\n'+text[hi:];assert text.count(capacity(16))==4
    text=text.replace(capacity(16),' ldx CurrentOAMOffset\n')
    size=int(old['syms']['TnExactIconRender']['size'],0)
    text=text.replace('.endproc',f' .res {size}-(*-TnExactIconRender),$ff ; preserve this private helper footprint\n.endproc')
    p.write_text(text)
    p=s/'src/tmnt_equipment_shuriken_fast.s';text=p.read_text()
    anchor=' lda R5\n bne Legacy\n lda R7\n cmp #1\n bne Legacy\n'
    assert text.count(anchor)==1
    text=text.replace(anchor,' lda R5\n bne Legacy\n ; Caller retains X=shot slot; R7=1 and R3=0 are fixed before this JSR.\n lda TnShotKind,x\n cmp #2\n bne Legacy\n lda CurrentOAMOffset\n cmp #248\n bcs Legacy\n')
    anchor=' lda R3\n bne Legacy\n';assert text.count(anchor)==1;text=text.replace(anchor,'')
    assert text.count(capacity(8))==6;text=text.replace(capacity(8),' ldx CurrentOAMOffset\n')
    size=int(old['syms']['TnExactShurikenRender']['size'],0)
    text=text.replace('.endproc',f' .res {size}-(*-TnExactShurikenRender),$ff ; preserve this private helper footprint\n.endproc')
    p.write_text(text)
    cmd=[sys.executable,'-B',str(s/'tools/build_mmc5_expanded.py'),'--workspace',str(s),'--compiler',str(ROOT/'tools/Windows/cc65/bin/cl65.exe'),'--output',str(a.output/'candidate.nes')]
    r=subprocess.run(cmd,cwd=s,capture_output=True,text=True);(a.output/'build.log').write_text(r.stdout+r.stderr)
    assert r.returncode==0,(r.stdout+r.stderr)[-4000:]
    new=load(a.output/'candidate.nes');oq=qualified(a.parent/'candidate.nes');nq=qualified(a.output/'candidate.nes');moved={}
    for name,val in oq.items():
        if nq.get(name)!=val:
            assert len(name)==2 and name[0]in['TnExactIconRender','TnExactShurikenRender'],(name,val,nq.get(name))
            moved[str(name)]=dict(old=val,new=nq.get(name),genuine_private_control_label=True)
    for n in['TnExactIconRender','TnExactShurikenRender']:
        assert address(old,n)==address(new,n)and old['syms'][n]['size']==new['syms'][n]['size']
    before=old['raw'];after=new['raw'];bank=lambda raw,n:raw[16+n*8192:16+(n+1)*8192]
    delta={n:sum(x!=y for x,y in zip(bank(before,n),bank(after,n)))for n in range(128)};delta={n:v for n,v in delta.items()if v}
    assert set(delta)=={87}and before[:16]==after[:16]and before[1048592:]==after[1048592:]
    assert bank(before,87)[:0x1700]==bank(after,87)[:0x1700]
    prep=json.loads((a.parent/'preparation.json').read_text());prep['candidate_ROM_sha256']=sha(a.output/'candidate.nes')
    (a.output/'preparation.json').write_text(json.dumps(prep,indent=2)+'\n');manifest={};patch=''
    for n in['src/tmnt_equipment_icon_fast.s','src/tmnt_equipment_shuriken_fast.s']:
        p=a.parent/'source'/n;q=s/n;manifest[n]=dict(before_sha256=sha(p),after_sha256=sha(q))
        patch+=''.join(difflib.unified_diff(p.read_text().splitlines(True),q.read_text().splitlines(True),fromfile='a/'+n,tofile='b/'+n))
    (a.output/'review.patch').write_text(patch)
    q=dict(prepared=True,stage='short-emitter-admission',source_only=True,native_run=False,accepted=False,parent_ROM_sha256=PARENT,
        candidate_ROM_sha256=sha(a.output/'candidate.nes'),changed_PRG_bytes=delta,all_original_pre1d741_symbols_exact=True,
        own_public_helper_entries_and_footprints_exact=True,genuine_private_label_moves=moved,literal_original_fallback=True,
        source_changes=manifest,checker_sha256=sha(Path(__file__)))
    (a.output/'fast-preparation.json').write_text(json.dumps(q,indent=2)+'\n');print(json.dumps(q))


if __name__=='__main__':main()
