"""Prepare a real raw0/variant4 Celeste Mario controller run; no native launch."""
from pathlib import Path
import argparse
import json
import current_roster_compact_11_v1 as base
from roster_expansion_native_prepare_v2 import navigation


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rom',type=Path,required=True)
    parser.add_argument('--expected-sha256',required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--identity',choices=['celeste'],default='celeste')
    parser.add_argument('--mode',choices=['easy','hard'],default='easy')
    parser.add_argument('--frames',type=int,default=8000)
    parser.add_argument('--policy',type=Path,
                        default=base.ROOT/'tools/playthroughs/celeste_11_v1.lua')
    parser.add_argument('--replay',type=Path)
    args=parser.parse_args()
    base.BASE['celeste']=(0,0,'MarioVariant',4)
    base.navigation=navigation
    base.prepare(args)
    ready_path=args.output.resolve()/'ready.json'
    receipt=json.loads(ready_path.read_text())
    for dependency in (Path(__file__).resolve(),
                       Path(__file__).with_name('roster_expansion_native_prepare_v2.py')):
        receipt['bindings'][str(dependency)]=base.sha(dependency)
    receipt['staged_new_roster']=True
    receipt['controller_scope']='Actual raw0/variant4 selection. Read-only local context may reuse controller decisions; ROM identity/state never changed.'
    ready_path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(ready=str(ready_path),sha256=base.sha(ready_path))))


if __name__=='__main__':
    main()
