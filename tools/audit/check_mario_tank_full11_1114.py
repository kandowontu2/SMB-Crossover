"""Reuse the closed readonly source driver, explicitly bound to Tank only."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
from unittest.mock import patch

import replay_mario_tank_full11_1114 as Factory
import check_smb1_alts_full11_1114 as Runner

HARNESS_SOURCE='9f56378f3e7ac12765927ebfef824ba7de70805c4105b6a68d89a00280a9d87f'


def run(raw,*,metadata_only=False,limit=6500):
    assert sha256(Path(Runner.__file__).read_bytes()).hexdigest()==HARNESS_SOURCE
    with patch.object(Runner,'Factory',Factory):
        return Runner.strict_metadata(raw,'tank')if metadata_only else Runner.run(raw,'tank',limit)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--metadata',action='store_true')
    args=p.parse_args();q=run(Factory.ROM.read_bytes(),metadata_only=args.metadata)
    print(json.dumps(q,separators=(',',':')),flush=True)
    if not args.metadata:assert q['passed'],'Tank full-stage source route remains unqualified'
