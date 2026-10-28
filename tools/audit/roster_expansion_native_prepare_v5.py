"""Prepare Alex/Ryan real-input discovery on an explicitly staged test ROM."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--rom',type=Path,required=True)
    p.add_argument('--expected-sha256',required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--identity',choices=['alex','ryan'],default='alex')
    p.add_argument('--mode',choices=['easy','hard'],default='easy')
    p.add_argument('--frames',type=int,default=8000)
    p.add_argument('--policy',type=Path,default=base.ROOT/'tools/playthroughs/full_roster_policy_og.lua')
    a=p.parse_args();a.replay=None
    base.BASE.update(alex=(20,21,'RcVariant',0),ryan=(20,21,'RcVariant',1))
    base.navigation=navigation
    base.prepare(a)
    ready=a.output.resolve()/'ready.json';d=json.loads(ready.read_text())
    for dep in [Path(__file__).resolve(),Path(__file__).with_name('roster_expansion_native_prepare_v2.py')]:
        d['bindings'][str(dep)]=base.sha(dep)
    d['staged_new_roster']=True
    d['controller_scope']='Actual menu raw21 / realSelect alternate; ordinary controller only. Private menu thumbnail/shared adoption remain open.'
    ready.write_text(json.dumps(d,indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready),sha256=base.sha(ready))))


if __name__=='__main__':main()
