"""Actual assembly/whole-WorldTile primitive proof; no ordinary game overlay."""
from hashlib import sha256
import json
from unittest.mock import patch
import check_prince_wall_body_proposal_1114 as Prior
import check_prince_floor_predicate_1114 as Oracle

SOURCE=Prior.World.F.R/'tools/reference/prince_wall_floor_point_1114.s'


def run(raw,*,expanded=False):
    with patch.object(Prior,'SOURCE',SOURCE):
        info=Prior.metadata(raw);code=Prior.assemble();labels=Prior.assemble(labels_only=True)
    q=Oracle.run(raw,compiled=(code,info['calls'],labels['PeekRoof']),expanded=expanded)
    q.update(info)
    q['private_reader_contract']='Only C is live locally. A/X/V/N/Z clobber; enclosing WorldTile saves and restores caller X/Y/P.'
    q['primitive_assembly_passed']=q['failures']==0
    return q


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--expanded',action='store_true');a=p.parse_args()
    q=run(Prior.World.F.ROM.read_bytes(),expanded=a.expanded)
    q['receipt_SHA256']=sha256(json.dumps(q,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    print(json.dumps(q,separators=(',',':')),flush=True)
