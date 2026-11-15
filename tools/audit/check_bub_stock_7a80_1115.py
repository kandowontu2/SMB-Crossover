"""Zero-output current Bub/Bob foundation; ordinary natural mushroom only."""
from pathlib import Path
from unittest.mock import patch
from hashlib import sha256
import argparse,json
import replay_bub_stock_7a80_1115 as F

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--identity',type=int,choices=(0,1),default=0);p.add_argument('--metadata',action='store_true');p.add_argument('--inspect-route',action='store_true');a=p.parse_args()
    raw=F.ROM.read_bytes()
    def forbid(*args,**kwargs):raise AssertionError('Current Bub source attempted file output')
    with patch.object(Path,'write_bytes',forbid),patch.object(Path,'write_text',forbid):
        q=F.metadata(raw,a.identity)
        if a.inspect_route:
            text=F.controller(raw,a.identity)
            for start,end in [('local function full_tick_base','local upgrade_'),('local function upgrade_item','local function drive')]:
                lo=text.index(start);hi=text.index(end,lo+len(start));print(text[lo:hi],flush=True)
        if not a.metadata:
            q['source']=F.source_check(raw,a.identity)
            q['source_receipt_SHA256']=sha256(json.dumps(q['source'],sort_keys=True,separators=(',',':')).encode()).hexdigest()
        print('RESULT '+json.dumps(q,separators=(',',':')),flush=True)
