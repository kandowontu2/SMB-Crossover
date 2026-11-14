"""Source-only bare CF clock controller, distinct from full-stage navigation."""
import argparse
import json
from unittest.mock import patch

import replay_contra_force_clock_1114 as Factory
import check_contra_force_full11_1114 as CF
import check_smb1_alts_full11_1114 as Harness


def metadata(raw,key):
    with patch.object(Harness,'Factory',Factory):return Harness.strict_metadata(raw,key)


def run(raw,key):
    with patch.object(Harness,'Factory',Factory),patch.object(CF,'Factory',Factory),patch.object(Harness,'cold',CF.cold):
        return Harness.run(raw,key,2000)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--identity',choices=Factory.IDENTITIES,default='burns')
    p.add_argument('--metadata',action='store_true');args=p.parse_args();raw=Factory.ROM.read_bytes()
    q=metadata(raw,args.identity)if args.metadata else run(raw,args.identity)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Bare CF source clock controller did not pass'
