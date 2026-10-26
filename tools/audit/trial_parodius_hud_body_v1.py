"""Build the exact disjoint union of two private display fixes; never install."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from link_pit_rygar_sophia_audit_cpu import scoped_load
from check_tmnt_render_oa import address,location

ROOT=Path(__file__).resolve().parents[2]
D=Path('C:/Users/kando/Videos/SMB Crossover Archive/2026-10-24-native-rest-py')
P=D/'parodius-visibility-current50b5-v1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--compiler',type=Path,required=True)
    a=p.parse_args();assert not a.output.resolve().is_relative_to(ROOT)
    hud=P/'hud-scroll-candidate-v1';body=D/'root-parodius-body-order-v1'
    baseline=ROOT/'build/smb-crossover-mmc5-expanded.nes'
    assert sha(baseline)=='50b51c3c69f45ef137720c47f521574097f421056e3b73296d06ba70080d2363'
    assert sha(hud/'candidate.nes')=='df5154bc035ba2c392bb8d34068897a2bccf7a78a6f4554bd6790d31a586c357'
    assert sha(body/'candidate.nes')=='7e52b78d6be39cf5315f937c0af4705fbd8c38b03416c7b66bc44cfc0cf37979'
    bodyproof=json.loads((body/'proof.json').read_text())
    assert all(sha(body/'source'/name)==value for name,value in bodyproof['changed_source'].items())
    a.output.mkdir(parents=True,exist_ok=False);source=a.output/'source'
    shutil.copytree(hud/'source',source)
    for name in bodyproof['changed_source']:
        target=source/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(body/'source'/name,target)
    rom=a.output/'candidate.nes'
    cmd=[sys.executable,'-B',str(source/'tools/build_mmc5_expanded.py'),
         '--workspace',str(source),'--source-overlay',str(source),
         '--compiler',str(a.compiler),'--output',str(rom)]
    result=subprocess.run(cmd,capture_output=True,text=True)
    (a.output/'build-host.log').write_text(result.stdout+result.stderr)
    assert result.returncode==0,result.stdout+result.stderr
    original=baseline.read_bytes();h=(hud/'candidate.nes').read_bytes();b=(body/'candidate.nes').read_bytes()
    expected=bytearray(h)
    bodydelta={i for i,(x,y) in enumerate(zip(original,b)) if x!=y}
    huddelta={i for i,(x,y) in enumerate(zip(original,h)) if x!=y}
    assert not bodydelta&huddelta
    for i in bodydelta:expected[i]=b[i]
    actual=rom.read_bytes();assert actual==expected
    old=scoped_load(hud/'candidate.nes');new=scoped_load(rom)
    for name,symbol in old['syms'].items():
        assert address(old,name)==address(new,name),name
        if 'seg' in symbol and 'ooffs' in old['segs'][symbol['seg']]:
            assert location(old,name)==location(new,name),name
    proof=dict(prepared=True,adopted=False,native_run=False,goal_complete=False,
               candidate_ROM_sha256=sha(rom),baseline_ROM_sha256=sha(baseline),
               HUD_parent_ROM_sha256=sha(hud/'candidate.nes'),body_donor_ROM_sha256=sha(body/'candidate.nes'),
               exact_disjoint_byte_union=True,body_delta_bytes=len(bodydelta),HUD_delta_bytes=len(huddelta),
               all_parent_symbols_exact=len(old['syms']),CHR_exact=original[1048592:]==actual[1048592:],
               source_body_delta=bodyproof['changed_source'],tool_sha256=sha(Path(__file__)),
               compiler_sha256=sha(a.compiler),
               limits='Private composition only. First HUD cold control passed on df515, '
                      'but its remaining controls are separate. Body ordering still needs '
                      'fresh actual source-bound pixel/readability/fairness and cadence checks. '
                      'No old native receipt certifies this combined ROM.')
    (a.output/'proof.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))


if __name__=='__main__':main()
