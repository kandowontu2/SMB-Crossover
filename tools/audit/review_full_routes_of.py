"""Use unchanged route/frame/scroll bounds for an explicitly named subset."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

ROOT=Path(__file__).resolve().parents[2]


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True);p.add_argument('--evidence',type=Path,required=True)
    p.add_argument('--names',nargs='+',required=True);a=p.parse_args()
    replay=json.loads((a.evidence/'replay-results.json').read_text())
    wanted={(n,m)for n in a.names for m in ['easy','hard']}
    assert len(wanted)==len(a.names)*2
    assert len(replay['runs'])==len(wanted)and{(q['identity'],q['mode'])for q in replay['runs']}==wanted
    original=ROOT/'tools/audit/review_tmnt_ny.py';source=original.read_text()
    anchor="len(replay['runs']) == 8";assert source.count(anchor)==1
    source=source.replace(anchor,"len(replay['runs']) == "+str(len(wanted)))
    namespace={'__name__':'explicit_subset_review','__file__':str(original)}
    exec(compile(source,str(original),'exec'),namespace)
    sys.argv=[str(original),'--rom',str(a.rom),'--evidence',str(a.evidence)]
    namespace['main']()
    report=a.evidence/'route-review.json';q=json.loads(report.read_text())
    q['original_review_sha256']=hashlib.sha256(original.read_bytes()).hexdigest()
    q['subset_adapter_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    q['explicit_names']=a.names
    q['bound_changes']='Only expected run count8 is replaced by the explicit subset count; per-run zero-death, exact replay, complete PNG, CHR and scanline/camera/world-step assertions stay unchanged.'
    report.write_text(json.dumps(q,indent=2)+'\n')


if __name__=='__main__':main()
