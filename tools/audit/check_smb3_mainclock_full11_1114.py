"""Separate completed-Main successor source scopes; no generated files."""
from functools import partial
from hashlib import sha256
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import argparse,json

import replay_smb3_mainclock_full11_1114 as Factory
import check_smb3_alts_full11_1114 as Driver

DRIVER_SOURCE='e76c09a2b5ec799e78f48ebc37e998015a0e22924a75bb9ba2dd697da0326e80'


def run(raw,key,*,metadata_only=False,damage_probe=False,limit=7000):
    assert sha256(Path(Driver.__file__).read_bytes()).hexdigest()==DRIVER_SOURCE
    facade=SimpleNamespace(W=Factory.W,N=Factory.N,ROM=Factory.ROM,normalize=Factory.normalize,
        bindings=partial(Factory.bindings,damage_probe=damage_probe),
        controller=partial(Factory.controller,damage_probe=damage_probe),
        metadata=partial(Factory.metadata,damage_probe=damage_probe))
    with patch.object(Driver,'Factory',facade):return Driver.run(raw,key,metadata_only=metadata_only,limit=limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,required=True)
    p.add_argument('--metadata',action='store_true');p.add_argument('--damage-probe',action='store_true');args=p.parse_args()
    q=run(Factory.ROM.read_bytes(),args.identity,metadata_only=args.metadata,damage_probe=args.damage_probe)
    if not args.metadata:
        receipt=q.pop('receipt')
        q['receipt_summary']={k:v for k,v in receipt.items()if k not in('gap_trace_first','gap_trace_tail','checkpoints','menu_events')}
        q['trace_samples']={k:receipt[k][:1]+receipt[k][-1:]for k in('gap_trace_first','gap_trace_tail')if isinstance(receipt.get(k),list)}
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Completed-Main source route/coverage gate did not pass'
